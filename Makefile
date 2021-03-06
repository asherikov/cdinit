update: addremote
	git fetch --all
	git rm --ignore-unmatch -rf dinit
	rm -Rf dinit
	git read-tree --prefix=dinit -u 77da28603ee862ab57efa2fb73d19cd2af3e6726
	# strip docs and tests: they are not built and there are multiple shellcheck complaints
	git rm --ignore-unmatch -rf  dinit/doc
	git rm --ignore-unmatch -rf  dinit/src/igr-tests
	git rm --ignore-unmatch -rf  dinit/configs/mconfig.Linux.sh

addremote:
	-git remote add upstream git@github.com:davmac314/dinit.git --no-tags -t master
	-git remote add mydinit git@github.com:asherikov/dinit.git --no-tags 
