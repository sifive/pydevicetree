# Copyright (c) 2019 SiFive Inc.
# SPDX-License-Identifier: Apache-2.0

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

.PHONY: test-unit
test-unit: venv/bin/activate
	source venv/bin/activate && python3 -m unittest
test: test-unit

.PHONY: test
test:
