# Catch-up TV &amp; More repository


## Notes for Kodi users

This is the repository of Catch-up &amp; More in order to give the user the ability to keep Catch-up &amp; More automatically up to date.
There is different add-on for different Kodi version.

Leia users can use Krypton add-on.

**In order to install our repo addon, please follow the wiki tutorial: [Add-the-official-repository](https://github.com/Catch-up-TV-and-More/plugin.video.catchuptvandmore/wiki/Add-the-official-repository)**



## Developers notes


### Automatic script

The `update_all_repos.sh` can be used to automatically check if any of our addon has been updated to a newer version. If that is the case the script will automatically create a commit with the latest changes and it will push the modification on this GitHub repository.
This script is executed every night with a cron task but you can trigger it manually on your own computer.


### Manually update a specific repository

**Once `create_repository.py` is done, do not forget to commit/push modifications on this GitHub repo**

#### How to update the Jarvis Release repository

```bash
python create_repository.py \
	--datadir ./zips/jarvis_release \
	--info addons_xmls/jarvis_release/addons.xml \
	--checksum addons_xmls/jarvis_release/addons.xml.md5 \
	repo_addons_src/catchuptvandmore.kodi.jarvis.release/ \
	https://github.com/Catch-up-TV-and-More/plugin.video.catchuptvandmore\#kodi16
```

#### How to update the Jarvis Beta repository

```bash
python create_repository.py \
	--datadir ./zips/jarvis_beta \
	--info addons_xmls/jarvis_beta/addons.xml \
	--checksum addons_xmls/jarvis_beta/addons.xml.md5 \
	repo_addons_src/catchuptvandmore.kodi.jarvis.beta/ \
	https://github.com/Catch-up-TV-and-More/plugin.video.catchuptvandmore\#kodi16
```

#### How to update the Krypton Release repository

```bash
python create_repository.py \
	--datadir ./zips/krypton_release \
	--info addons_xmls/krypton_release/addons.xml \
	--checksum addons_xmls/krypton_release/addons.xml.md5 \
	repo_addons_src/catchuptvandmore.kodi.krypton.release/ \
	https://github.com/Catch-up-TV-and-More/plugin.video.catchuptvandmore\#master
```

#### How to update the Krypton Beta repository

```bash
python create_repository.py \
	--datadir ./zips/krypton_beta \
	--info addons_xmls/krypton_beta/addons.xml \
	--checksum addons_xmls/krypton_beta/addons.xml.md5 \
	repo_addons_src/catchuptvandmore.kodi.krypton.beta/ \
	https://github.com/Catch-up-TV-and-More/plugin.video.catchuptvandmore\#dev
```

#### How to update the Leia Test DRM repository

```bash
python create_repository.py \
	--datadir ./zips/leia_drmtest \
	--info addons_xmls/leia_drmtest/addons.xml \
	--checksum addons_xmls/leia_drmtest/addons.xml.md5 \
	repo_addons_src/catchuptvandmore.kodi.leia.drmtest/ \
	https://github.com/Catch-up-TV-and-More/plugin.video.catchuptvandmoretestdrmkodi18\#master
```



