# Copyright (c) 2019 SiFive Inc.
# SPDX-License-Identifier: Apache-2.0

all: test dist

venv/bin/activate:
	python3 -m venv venv
	. $@ && pip install --upgrade pip
	. $@ && pip install -r requirements.txt

.PHONY: virtualenv
virtualenv: venv/bin/activate

.PHONY: dist
dist: venv/bin/activate
	. $< && pip install --upgrade setuptools wheel
	. $< && python3 setup.py sdist bdist_wheel

.PHONY: dist-clean
dist-clean: venv/bin/activate
	. $< && python3 setup.py clean --all
	-rm -rf dist pydevicetree.egg-info
clean: dist-clean

.PHONY: upload
upload: venv/bin/activate dist
	. $< && pip install twine
	. $< && python3 -m twine upload dist/*

.PHONY: test-types
test-types: venv/bin/activate
	. $< && mypy -p pydevicetree
test: test-types

.PHONY: test-lint
test-lint: venv/bin/activate
	. $< && pylint pydevicetree
test: test-lint

UNIT_TESTS = tests/test_devicetree.py \
	     tests/test_grammar.py \
	     tests/test_exceptions.py \
	     tests/test_overlay.py

.PHONY: test-unit
test-unit: venv/bin/activate $(UNIT_TESTS)
	. $< && python3 -m unittest $(UNIT_TESTS)
test: test-unit

INTEGRATION_TESTS = tests/test_full_trees.py

.PHONY: test-integration
test-integration: venv/bin/activate
	. $< && python3 -m unittest $(INTEGRATION_TESTS)
test: test-integration

.PHONY: test
test:

.PHONY: clean
clean:
	-rm -rf venv .mypy_cache __pycache__
