#!/usr/bin/env python
r"""
Create a Kodi add-on repository from add-on sources

This tool extracts Kodi add-ons from their respective locations and
copies the appropriate files into a Kodi add-on repository. Each add-on
is placed in its own directory. Each contains the add-on metadata files
and a zip archive. In addition, the repository catalog "addons.xml" is
placed in the repository folder.

Each add-on location is either a local path or a URL. If it is a local
path, it can be to either an add-on folder or an add-on ZIP archive. If
it is a URL, it should be to a Git repository and it should use the
format:
    REPOSITORY_URL#BRANCH:PATH
The first segment is the Git URL that would be used to clone the
repository, (e.g.,
"https://github.com/chadparry/kodi-repository.chad.parry.org.git").
That is followed by an optional "#" sign and a branch or tag name,
(e.g. "release-1.0"). If no branch name is specified, then the default
is the repository's currently active branch, which is the same default
as git-clone. Next comes an optional ":" sign and path. The path
denotes the location of the add-on within the repository. If no path is
specified, then the default is ".".

For example, if you are in the directory that should contain addons.xml
and you just copied a new version of the only add-on
"repository.chad.parry.org" to a subdirectory, then you can create or
update the addons.xml file with this command:

    ./create_repository.py repository.chad.parry.org

As another example, here is the command that generates Chad Parry's
Repository:

    create_repository.py \
        --datadir=~/html/software/kodi \
        --compressed \
        https://github.com/chadparry\
/kodi-repository.chad.parry.org.git:repository.chad.parry.org \
        https://github.com/chadparry\
/kodi-plugin.program.remote.control.browser.git\
:plugin.program.remote.control.browser

This script has been tested with Python 2.7.10 and Python 3.6.5. It
depends on the GitPython module.
"""

__author__ = "Chad Parry"
__contact__ = "github@chad.parry.org"
__copyright__ = "Copyright 2016-2021 Chad Parry"
__license__ = "GNU GENERAL PUBLIC LICENSE. Version 2, June 1991"
__version__ = "2.3.6"


import argparse
import collections
import errno
import gzip
import hashlib
import io
import os
import re
import shutil
import stat
import sys
import tempfile
import threading
import xml.etree.ElementTree
import zipfile


AddonMetadata = collections.namedtuple(
    'AddonMetadata', ('id', 'version', 'root'))
WorkerResult = collections.namedtuple(
    'WorkerResult', ('addon_metadata', 'exc_info'))
AddonWorker = collections.namedtuple('AddonWorker', ('thread', 'result_slot'))


INFO_BASENAME = 'addon.xml'
METADATA_BASENAMES = (
    INFO_BASENAME,
    'icon.png',
    'fanart.jpg',
    'LICENSE.txt')


# The specification for version numbers is at http://semver.org/.
# The Kodi documentation at
# http://kodi.wiki/index.php?title=Addon.xml&oldid=128873#How_versioning_works
# adds a twist by recommending a tilde instead of a hyphen.
VERSION_PATTERN = (r'^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)'
                   r'(?:[-~]((?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)'
                   r'(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?'
                   r'(?:\+([0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?$')


def get_archive_basename(addon_metadata):
    return '{}-{}.zip'.format(addon_metadata.id, addon_metadata.version)


def get_metadata_basenames(addon_metadata):
    return ([(basename, basename) for basename in METADATA_BASENAMES] +
            [(
                'changelog.txt',
                'changelog-{}.txt'.format(addon_metadata.version))])


def is_url(addon_location):
    return bool(re.match(r'[A-Za-z0-9+.-]+://.', addon_location))


def get_posix_path(path):
    return path.replace(os.path.sep, '/')


def samefile(a, b):
    try:
        return os.path.samefile(a, b)
    except AttributeError:
        return (os.path.normcase(os.path.normpath(a)) ==
                os.path.normcase(os.path.normpath(b)))


def parse_metadata(metadata_file):
    # Parse the addon.xml metadata.
    try:
        tree = xml.etree.ElementTree.parse(metadata_file)
    except IOError:
        raise RuntimeError(
            'Cannot open add-on metadata: {}'.format(metadata_file))
    root = tree.getroot()
    addon_metadata = AddonMetadata(
        root.get('id'),
        root.get('version'),
        root)
    # Validate the add-on ID.
    if (addon_metadata.id is None or
            re.search(r'[^a-z0-9._-]', addon_metadata.id)):
        raise RuntimeError('Invalid add-on ID: {}'.format(addon_metadata.id))
    if (addon_metadata.version is None or
            not re.match(VERSION_PATTERN, addon_metadata.version)):
        raise RuntimeError(
            'Invalid add-on verson: {}'.format(addon_metadata.version))
    return addon_metadata


def generate_checksum(archive_path, is_binary=True, checksum_path_opt=None):
    checksum_path = ('{}.md5'.format(archive_path)
                     if checksum_path_opt is None else checksum_path_opt)
    checksum_dirname = os.path.dirname(checksum_path)
    archive_relpath = os.path.relpath(archive_path, checksum_dirname)

    checksum = hashlib.md5()
    with open(archive_path, 'rb') as archive_contents:
        for chunk in iter(lambda: archive_contents.read(2**12), b''):
            checksum.update(chunk)
    digest = checksum.hexdigest()

    binary_marker = '*' if is_binary else ' '
    # Force a UNIX line ending, like the md5sum utility.
    with io.open(checksum_path, 'w', newline='\n') as sig:
        sig.write(u'{} {}{}\n'.format(digest, binary_marker, archive_relpath))


def copy_metadata_files(source_folder, addon_target_folder, addon_metadata):
    for (source_basename, target_basename) in get_metadata_basenames(
            addon_metadata):
        source_path = os.path.join(source_folder, source_basename)
        if os.path.isfile(source_path):
            shutil.copyfile(
                source_path,
                os.path.join(addon_target_folder, target_basename))


def on_remove_error(function, path, excinfo):
    exc_info_value = excinfo[1]
    if (hasattr(exc_info_value, 'errno') and
            exc_info_value.errno == errno.EACCES):
        os.chmod(path, stat.S_IWUSR)
        function(path)
    else:
        raise


def fetch_addon_from_git(addon_location, target_folder):
    # Parse the format "REPOSITORY_URL#BRANCH:PATH". The colon is a delimiter
    # unless it looks more like a scheme, (e.g., "http://").
    match = re.match(
        r'((?:[A-Za-z0-9+.-]+://)?.*?)(?:#([^#]*?))?(?::([^:]*))?$',
        addon_location)
    (clone_repo, clone_branch, clone_path_option) = match.groups()
    clone_path = (os.path.join('.', '')
                  if clone_path_option is None else clone_path_option)

    # Create a temporary folder for the git clone.
    clone_folder = tempfile.mkdtemp('-repo')
    try:
        # Check out the sources.
        cloned = git.Repo.clone_from(clone_repo, clone_folder)
        if clone_branch is not None:
            cloned.git.checkout(clone_branch)
        clone_source_folder = os.path.join(clone_folder, clone_path)

        metadata_path = os.path.join(clone_source_folder, INFO_BASENAME)
        addon_metadata = parse_metadata(metadata_path)
        addon_target_folder = os.path.join(target_folder, addon_metadata.id)

        # Create the compressed add-on archive.
        if not os.path.isdir(addon_target_folder):
            os.mkdir(addon_target_folder)
        archive_path = os.path.join(
            addon_target_folder, get_archive_basename(addon_metadata))
        with open(archive_path, 'wb') as archive:
            cloned.archive(
                archive,
                treeish='HEAD:{}'.format(clone_path),
                prefix=os.path.join(addon_metadata.id, ''),
                format='zip')
        generate_checksum(archive_path)

        copy_metadata_files(
            clone_source_folder, addon_target_folder, addon_metadata)

        return addon_metadata
    finally:
        shutil.rmtree(
            clone_folder,
            ignore_errors=False,
            onerror=on_remove_error)


def fetch_addon_from_folder(raw_addon_location, target_folder):
    addon_location = os.path.expanduser(raw_addon_location)
    metadata_path = os.path.join(addon_location, INFO_BASENAME)
    addon_metadata = parse_metadata(metadata_path)
    addon_target_folder = os.path.join(target_folder, addon_metadata.id)

    # Create the compressed add-on archive.
    if not os.path.isdir(addon_target_folder):
        os.mkdir(addon_target_folder)
    archive_path = os.path.join(
        addon_target_folder, get_archive_basename(addon_metadata))
    with zipfile.ZipFile(
            archive_path, 'w', compression=zipfile.ZIP_DEFLATED) as archive:
        for (root, dirs, files) in os.walk(addon_location):
            relative_root = os.path.join(
                addon_metadata.id, os.path.relpath(root, addon_location))
            for relative_path in files:
                archive.write(
                    os.path.join(root, relative_path),
                    os.path.join(relative_root, relative_path))
    generate_checksum(archive_path)

    if not samefile(addon_location, addon_target_folder):
        copy_metadata_files(
            addon_location, addon_target_folder, addon_metadata)

    return addon_metadata


def fetch_addon_from_zip(raw_addon_location, target_folder):
    addon_location = os.path.expanduser(raw_addon_location)
    with zipfile.ZipFile(
            addon_location, compression=zipfile.ZIP_DEFLATED) as archive:
        # Find out the name of the archive's root folder.
        roots = frozenset(
            next(iter(path.split('/')), '')
            for path in archive.namelist())
        if len(roots) != 1:
            raise RuntimeError('Archive should contain one directory')
        root = next(iter(roots))

        metadata_file = archive.open(
            get_posix_path(os.path.join(root, INFO_BASENAME)))
        addon_metadata = parse_metadata(metadata_file)
        addon_target_folder = os.path.join(target_folder, addon_metadata.id)

        # Copy the metadata files.
        if not os.path.isdir(addon_target_folder):
            os.mkdir(addon_target_folder)
        for (source_basename, target_basename) in get_metadata_basenames(
                addon_metadata):
            try:
                source_file = archive.open(
                    get_posix_path(os.path.join(root, source_basename)))
            except KeyError:
                continue
            with open(
                    os.path.join(addon_target_folder, target_basename),
                    'wb') as target_file:
                shutil.copyfileobj(source_file, target_file)

    # Copy the archive.
    archive_basename = get_archive_basename(addon_metadata)
    archive_path = os.path.join(addon_target_folder, archive_basename)
    addon_source_folder = os.path.dirname(addon_location) or '.'
    if (not samefile(addon_source_folder, addon_target_folder) or
            os.path.basename(addon_location) != archive_basename):
        shutil.copyfile(addon_location, archive_path)
    generate_checksum(archive_path)

    return addon_metadata


def fetch_addon(addon_location, target_folder):
    if is_url(addon_location):
        addon_metadata = fetch_addon_from_git(addon_location, target_folder)
    elif os.path.isdir(addon_location):
        addon_metadata = fetch_addon_from_folder(addon_location, target_folder)
    elif os.path.isfile(addon_location):
        addon_metadata = fetch_addon_from_zip(addon_location, target_folder)
    else:
        raise RuntimeError('Path not found: {}'.format(addon_location))
    return addon_metadata


def fetch_addon_to_result_slot(addon_location, target_folder, result_slot):
    try:
        addon_metadata = fetch_addon(addon_location, target_folder)
        result_slot.append(WorkerResult(addon_metadata, None))
    except Exception:
        result_slot.append(WorkerResult(None, sys.exc_info()))


def get_addon_worker(addon_location, target_folder):
    result_slot = []
    thread = threading.Thread(target=lambda: fetch_addon_to_result_slot(
        addon_location, target_folder, result_slot))
    return AddonWorker(thread, result_slot)


def create_repository(
        addon_locations,
        target_folder,
        info_path,
        checksum_path,
        is_compressed,
        no_parallel):
    # Import git lazily.
    if any(is_url(addon_location) for addon_location in addon_locations):
        try:
            global git
            import git
        except ImportError:
            raise RuntimeError(
                'Please install GitPython: pip install gitpython')

    # Create the target folder.
    if not os.path.isdir(target_folder):
        os.mkdir(target_folder)

    if no_parallel or len(addon_locations) <= 1:
        metadata = [
            fetch_addon(addon_location, target_folder)
            for addon_location in addon_locations]
    else:
        # Fetch all the add-on sources in parallel.
        workers = [
            get_addon_worker(addon_location, target_folder)
            for addon_location in addon_locations]
        for worker in workers:
            worker.thread.start()
        for worker in workers:
            worker.thread.join()

        # Collect the results from all the threads.
        metadata = []
        for worker in workers:
            try:
                result = next(iter(worker.result_slot))
            except StopIteration:
                raise RuntimeError('Add-on worker did not report result')
            if result.exc_info is not None:
                raise result.exc_info[1]
            metadata.append(result.addon_metadata)

    # Generate the addons.xml file.
    root = xml.etree.ElementTree.Element('addons')
    for addon_metadata in metadata:
        root.append(addon_metadata.root)
    tree = xml.etree.ElementTree.ElementTree(root)
    if is_compressed:
        info_file = gzip.open(info_path, 'wb')
    else:
        info_file = open(info_path, 'wb')
    with info_file:
        tree.write(info_file, encoding='UTF-8', xml_declaration=True)
    is_binary = is_compressed
    generate_checksum(info_path, is_binary, checksum_path)


def main():
    parser = argparse.ArgumentParser(
        description='Create a Kodi add-on repository from add-on sources')
    parser.add_argument(
        '--datadir',
        '-d',
        default='.',
        help='Path to place the add-ons [current directory]')
    parser.add_argument(
        '--info',
        '-i',
        help='''Path for the addons.xml file [DATADIR/addons.xml or
                DATADIR/addons.xml.gz if compressed]''')
    parser.add_argument(
        '--checksum',
        '-c',
        help='Path for the addons.xml.md5 file [INFO.md5]')
    parser.add_argument(
        '--compressed',
        '-z',
        action='store_true',
        help='Compress addons.xml with gzip')
    parser.add_argument(
        '--no-parallel',
        '-n',
        action='store_true',
        help='''Build add-on sources serially,
                which also makes error diagnosis easier''')
    parser.add_argument(
        'addon',
        nargs='*',
        metavar='ADDON',
        help='''Location of the add-on: either a path to a local folder or
                to a zip archive or a URL for a Git repository with the
                format REPOSITORY_URL#BRANCH:PATH''')
    args = parser.parse_args()

    data_path = os.path.expanduser(args.datadir)
    if args.info is None:
        if args.compressed:
            info_basename = 'addons.xml.gz'
        else:
            info_basename = 'addons.xml'
        info_path = os.path.join(data_path, info_basename)
    else:
        info_path = os.path.expanduser(args.info)

    checksum_path = (
        os.path.expanduser(args.checksum) if args.checksum is not None
        else '{}.md5'.format(info_path))
    create_repository(
        args.addon,
        data_path,
        info_path,
        checksum_path,
        args.compressed,
        args.no_parallel)


if __name__ == "__main__":
    main()
