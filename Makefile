install:
	pip install -r requirements/base.txt
	pip install --no-deps -r requirements/git.txt

reinstall-proto:
	pip install --force-reinstall --no-deps -r requirements/git.txt
