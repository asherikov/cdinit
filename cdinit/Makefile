update: addremote
	git fetch --all
	git rm --ignore-unmatch -rf ./dinit
	rm -Rf dinit
	git read-tree --prefix=cdinit/dinit -u f9940806af769d90e199c8842e6bfcd65770849b
	# strip docs and tests: they are not built and there are multiple shellcheck complaints
	git rm --ignore-unmatch -rf ./dinit/doc
	git rm --ignore-unmatch -rf ./dinit/src/igr-tests
	git rm --ignore-unmatch -rf ./dinit/src/tests
	git rm --ignore-unmatch -rf ./dinit/configs/mconfig.Linux.sh
	git rm --ignore-unmatch -rf ./dinit/.github
	git rm --ignore-unmatch -rf ./dinit/contrib

addremote:
	-git remote add upstream git@github.com:davmac314/dinit.git --no-tags -t master
	-git remote add mydinit git@github.com:asherikov/dinit.git --no-tags
