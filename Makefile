SHELL := /bin/bash

test:
	nosetests --cover-html --cover-html-dir=coverage --with-coverage --cover-package=softlayer_messaging
pep8:
	pep8 --repeat --show-source  softlayer_messaging
