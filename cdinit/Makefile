update: addremote
	git fetch --all
	git rm --ignore-unmatch -rf dinit
	rm -Rf dinit
	git read-tree --prefix=dinit -u 2b636592714fb619164e43eee3d9119232602636
	# strip docs and tests: they are not built and there are multiple shellcheck complaints
	git rm --ignore-unmatch -rf  dinit/doc
	git rm --ignore-unmatch -rf  dinit/src/igr-tests
	git rm --ignore-unmatch -rf  dinit/configs/mconfig.Linux.sh
	git rm --ignore-unmatch -rf  dinit/.github

addremote:
	-git remote add upstream git@github.com:davmac314/dinit.git --no-tags -t master
	-git remote add mydinit git@github.com:asherikov/dinit.git --no-tags
