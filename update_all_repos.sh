#!/usr/bin/env bash



echo -e "\n# Get previous addons.xml md5 of all repos\n"


jarvis_beta_md5=$(head -n 1 ./addons_xmls/jarvis_beta/addons.xml.md5| awk '{print $1;}')
echo -e "\t* Jarvis beta repo current MD5: $jarvis_beta_md5"

jarvis_release_md5=$(head -n 1 ./addons_xmls/jarvis_release/addons.xml.md5| awk '{print $1;}')
echo -e "\t* Jarvis release repo current MD5: $jarvis_release_md5"

krypton_beta_md5=$(head -n 1 ./addons_xmls/krypton_beta/addons.xml.md5| awk '{print $1;}')
echo -e "\t* Krypton beta repo current MD5: $krypton_beta_md5"

krypton_release_md5=$(head -n 1 ./addons_xmls/krypton_release/addons.xml.md5| awk '{print $1;}')
echo -e "\t* Krypton release repo current MD5: $krypton_release_md5"

leia_drmtest_md5=$(head -n 1 ./addons_xmls/leia_drmtest/addons.xml.md5| awk '{print $1;}')
echo -e "\t* Leai DRM test repo current MD5: $leia_drmtest_md5"





echo -e "\n# Start create_repository.py script on all repos\n"

echo -e "\t* Start create_repository.py on Jarvis beta repo"
python create_repository.py \
	--datadir ./zips/jarvis_beta \
	--info addons_xmls/jarvis_beta/addons.xml \
	--checksum addons_xmls/jarvis_beta/addons.xml.md5 \
	repo_addons_src/catchuptvandmore.kodi.jarvis.beta/ \
	https://github.com/Catch-up-TV-and-More/plugin.video.catchuptvandmore\#kodi16

echo -e "\t* Start create_repository.py on Jarvis release repo"
python create_repository.py \
	--datadir ./zips/jarvis_release \
	--info addons_xmls/jarvis_release/addons.xml \
	--checksum addons_xmls/jarvis_release/addons.xml.md5 \
	repo_addons_src/catchuptvandmore.kodi.jarvis.release/ \
	https://github.com/Catch-up-TV-and-More/plugin.video.catchuptvandmore\#kodi16

echo -e "\t* Start create_repository.py on Krypton beta repo"
python create_repository.py \
	--datadir ./zips/krypton_beta \
	--info addons_xmls/krypton_beta/addons.xml \
	--checksum addons_xmls/krypton_beta/addons.xml.md5 \
	repo_addons_src/catchuptvandmore.kodi.krypton.beta/ \
	https://github.com/Catch-up-TV-and-More/plugin.video.catchuptvandmore\#dev

echo -e "\t* Start create_repository.py on Krypton release repo"
python create_repository.py \
	--datadir ./zips/krypton_release \
	--info addons_xmls/krypton_release/addons.xml \
	--checksum addons_xmls/krypton_release/addons.xml.md5 \
	repo_addons_src/catchuptvandmore.kodi.krypton.release/ \
	https://github.com/Catch-up-TV-and-More/plugin.video.catchuptvandmore\#master

echo -e "\t* Start create_repository.py on Leai DRM test repo"
python create_repository.py \
	--datadir ./zips/leia_drmtest \
	--info addons_xmls/leia_drmtest/addons.xml \
	--checksum addons_xmls/leia_drmtest/addons.xml.md5 \
	repo_addons_src/catchuptvandmore.kodi.leia.drmtest/ \
	https://github.com/Catch-up-TV-and-More/plugin.video.catchuptvandmoretestdrmkodi18\#master





echo -e "\n# Get new addons.xml md5 of all repos\n"


jarvis_beta_md5_new=$(head -n 1 ./addons_xmls/jarvis_beta/addons.xml.md5| awk '{print $1;}')
echo -e "\t* Jarvis beta repo new MD5: $jarvis_beta_md5_new"

jarvis_release_md5_new=$(head -n 1 ./addons_xmls/jarvis_release/addons.xml.md5| awk '{print $1;}')
echo -e "\t* Jarvis release repo new MD5: $jarvis_release_md5_new"

krypton_beta_md5_new=$(head -n 1 ./addons_xmls/krypton_beta/addons.xml.md5| awk '{print $1;}')
echo -e "\t* Krypton beta repo new MD5: $krypton_beta_md5_new"

krypton_release_md5_new=$(head -n 1 ./addons_xmls/krypton_release/addons.xml.md5| awk '{print $1;}')
echo -e "\t* Krypton release repo new MD5: $krypton_release_md5_new"

leia_drmtest_md5_new=$(head -n 1 ./addons_xmls/leia_drmtest/addons.xml.md5| awk '{print $1;}')
echo -e "\t* Leai DRM test repo new MD5: $leia_drmtest_md5_new"




echo -e "\n# Compare previous and new MD5 values of all repos in order to commit/push if necessary\n"
commit_msg="Auto update repo(s): "
need_to_commit_push=false

if [ "$jarvis_beta_md5" == "$jarvis_beta_md5_new" ]
then
	echo -e "\t* No change on Jarvis beta repo"
else
	echo -e "\t* Change detected on Jarvis beta repo"
	commit_msg="$commit_msg Jarvis beta,"
	need_to_commit_push=true
fi


if [ "$jarvis_release_md5" == "$jarvis_release_md5_new" ]
then
	echo -e "\t* No change on Jarvis release repo"
else
	echo -e "\t* Change detected on Jarvis release repo"
	commit_msg="$commit_msg Jarvis release,"
	need_to_commit_push=true
fi


if [ "$krypton_beta_md5" == "$krypton_beta_md5_new" ]
then
	echo -e "\t* No change on Krypton beta repo"
else
	echo -e "\t* Change detected on Krypton beta repo"
	commit_msg="$commit_msg Krypton beta,"
	need_to_commit_push=true
fi


if [ "$krypton_release_md5" == "$krypton_release_md5_new" ]
then
	echo -e "\t* No change on Krypton release repo"
else
	echo -e "\t* Change detected on Krypton release repo"
	commit_msg="$commit_msg Krypton release,"
	need_to_commit_push=true
fi



if [ "$leia_drmtest_md5" == "$leia_drmtest_md5_new" ]
then
	echo -e "\t* No change on Leai DRM test repo"
else
	echo -e "\t* Change detected on Leai DRM test repo"
	commit_msg="$commit_msg Leai DRM test,"
	need_to_commit_push=true
fi



if [ "$need_to_commit_push" = true ]
then
    echo -e "\n# Change detected on one or more repos, need to commit/push on the GitHub repo\n"
    echo -e "\t* Commit message: $commit_msg"
    git add --all
    git commit -m "$commit_msg"
    git push
    echo -e "\t* Changes have been pushed"
else
	echo -e "\n# No change detected on any repos, no need to commit/push on the GitHub repo\n"
fi


exit 0









