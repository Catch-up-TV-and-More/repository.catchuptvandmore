# Catch-up TV &amp; More repository


## Notes for Kodi users

This is the repository of Catch-up &amp; More in order to give the user the ability to keep Catch-up &amp; More automatically up to date.
There is different add-on for different Kodi version.

Leia users can use Krypton add-on.

**In order to install our repo addon, please follow the wiki tutorial: [Add-the-official-repository](https://github.com/Catch-up-TV-and-More/plugin.video.catchuptvandmore/wiki/Add-the-official-repository)**



## Developers notes


### Automatic script

The `update_all_repos.sh` can be used to automatically check if any of our addon has been updated to a newer version. If that is the case the script will automatically create a commit with the latest changes and it will push the modification on this GitHub repository.
This script is executed by Travis each time a new commit is detected on `plugin.video.catchuptvandmore` or `resource.images.catchuptvandmore` but you can trigger it manually on your own computer.


### Manually update a specific repository

**Once `create_repository.py` is done, do not forget to commit/push modifications on this GitHub repo**


#### How to update the Krypton Release repository

```bash
python create_repository.py \
	--datadir ./zips/release \
	--info ./addons_xmls/krypton_release/addons.xml \
	--checksum ./addons_xmls/release/addons.xml.md5 \
	./repo_addons_src/catchuptvandmore.kodi.release/ \
	https://github.com/Catch-up-TV-and-More/plugin.video.catchuptvandmore\#master:plugin.video.catchuptvandmore \
	https://github.com/Catch-up-TV-and-More/resource.images.catchuptvandmore\#master:resource.images.catchuptvandmore
```

#### How to update the Krypton Beta repository

```bash
python create_repository.py \
	--datadir ./zips/beta \
	--info ./addons_xmls/beta/addons.xml \
	--checksum ./addons_xmls/beta/addons.xml.md5 \
	./repo_addons_src/catchuptvandmore.kodi.beta/ \
	https://github.com/Catch-up-TV-and-More/plugin.video.catchuptvandmore\#dev:plugin.video.catchuptvandmore \
	https://github.com/Catch-up-TV-and-More/resource.images.catchuptvandmore\#master:resource.images.catchuptvandmore
```


