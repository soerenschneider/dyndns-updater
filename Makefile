tests: unittest

.PHONY: venv
venv:
	if [ ! -d "venv" ]; then python3 -m venv venv; fi
	venv/bin/pip3 install -r requirements.txt

venv-test: venv
	venv/bin/pip3 install -r requirements-test.txt

unittests:
	venv/bin/python3 -m unittest tests/test_*.py

integrationtest:
	venv/bin/python3 -m unittest itest_*.py

