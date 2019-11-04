
venv/bin/activate:
	python3 -m venv venv
	source venv/bin/activate && pip install --upgrade pip
	source venv/bin/activate && pip install -r requirements.txt

.PHONY: virtualenv
virtualenv: venv/bin/activate

.PHONY: test-types
test-types: venv/bin/activate
	source venv/bin/activate && mypy -m unittest
test: test-types

.PHONY: test-lint
test-lint: venv/bin/activate
	source venv/bin/activate && pylint pydevicetree
test: test-lint

.PHONY: test
test: venv/bin/activate
	source venv/bin/activate && python3 -m unittest
