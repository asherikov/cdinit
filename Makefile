update: addremote
	git fetch --all
	git rm --ignore-unmatch -rf dinit
	rm -Rf dinit
	git read-tree --prefix=dinit -u c49e4d290bdfc97f707bfcfa43e6857f14af634d

addremote:
	-git remote add upstream git@github.com:davmac314/dinit.git --no-tags -t master
	-git remote add mydinit git@github.com:asherikov/dinit.git --no-tags 
