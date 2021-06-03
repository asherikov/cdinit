update: addremote
	git fetch --all
	git rm --ignore-unmatch -rf dinit
	rm -Rf dinit
	git read-tree --prefix=dinit -u 348c61d9b819ddb46fda1bc677a8355001e398b9

addremote:
	-git remote add upstream git@github.com:davmac314/dinit.git --no-tags -t master
	-git remote add mydinit git@github.com:asherikov/dinit.git --no-tags 
