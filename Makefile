tests: unittests

.PHONY: venv
venv:
	if [ ! -d "venv" ]; then python3 -m venv venv; fi
	venv/bin/pip3 install -r requirements.txt

venv-test: venv
	venv/bin/pip3 install -r requirements-test.txt

container: clean
	podman run -d --rm --name dyndnsmountebank -p 2525:2525 -p 8080:8080 registry.gitlab.com/soerenschneider/mountebank-docker
	sleep 2
	curl -X POST --data @mountebank/dyndns.json http://localhost:2525/imposters

clean:
	podman rm -f dyndnsmountebank || true

unittests:
	venv/bin/python3 -m unittest tests/test_*.py

integrationtests:
	venv/bin/python3 -m unittest inttests/*test_*.py

