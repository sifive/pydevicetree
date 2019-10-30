
venv/bin/activate:
	python3 -m venv venv

.PHONY: virtualenv
virtualenv: venv/bin/activate
	source venv/bin/activate && pip install --upgrade pip
	source venv/bin/activate && pip install -r requirements.txt

.PHONY: test
test: venv/bin/activate
	source venv/bin/activate && python3 -m unittest
