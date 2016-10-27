CWD = $(shell pwd)
SRC_DIR = ${CWD}/pootle
DOCS_DIR = ${CWD}/docs
STATIC_DIR = ${SRC_DIR}/static
ASSETS_DIR = $(shell python -c "from pootle.settings import *; print(STATIC_ROOT)")
JS_DIR = ${STATIC_DIR}/js
FORMATS=--formats=bztar
TEST_ENV_NAME = pootle_test_env

POOTLE_CMD = $(shell sh -c "command -v zing")
ifeq ($(POOTLE_CMD),)
	POOTLE_CMD=python manage.py
endif

.PHONY: all build clean sprite test pot help docs assets

all: help

build: docs assets
	python setup.py sdist ${FORMATS} ${TAIL}

assets:
	npm --version
	node --version
	cd ${JS_DIR} && \
	npm cache clear && \
	npm install && \
	cd ${CWD}
	${POOTLE_CMD} compilejsi18n
	${POOTLE_CMD} webpack --extra=--display-error-details
	mkdir -p ${ASSETS_DIR}

	${POOTLE_CMD} collectstatic --noinput --clear -i node_modules -i .tox -i docs ${TAIL}
	${POOTLE_CMD} assets build ${TAIL}

	chmod 664 ${ASSETS_DIR}.webassets-cache/*

travis-assets:
	npm --version
	node --version
	if [ -d "${ASSETS_DIR}.webassets-cache/" ]; then \
		echo "eating cache - yum!"; \
	else \
		cd ${JS_DIR} && \
		npm install && \
		cd ${CWD}; \
		${POOTLE_CMD} compilejsi18n; \
		${POOTLE_CMD} webpack --dev --nowatch; \
		mkdir -p ${ASSETS_DIR}; \
		${POOTLE_CMD} collectstatic --noinput --clear -i node_modules -i .tox -i docs ${TAIL}; \
		${POOTLE_CMD} assets build ${TAIL}; \
		chmod 664 ${ASSETS_DIR}.webassets-cache/*; \
	fi

docs:
	# The following creates the HTML docs.
	# NOTE: cd and make must be in the same line.
	cd ${DOCS_DIR}; make SPHINXOPTS="-W -q -j 4" html ${TAIL}

clean:
	npm cache clear
	rm -rf ${TEST_ENV_NAME}

test: clean assets
	virtualenv ${TEST_ENV_NAME} && \
	source ${TEST_ENV_NAME}/bin/activate && \
	pip install -r requirements/tests.txt && \
	python setup.py test

pot:
	@${SRC_DIR}/tools/createpootlepot

linguas:
	@${SRC_DIR}/tools/make-LINGUAS.sh 80 > ${SRC_DIR}/locale/LINGUAS

lint: lint-python lint-js lint-css

lint-py: lint-python

lint-python:
	flake8 --config=setup.cfg && \
	pydocstyle && \
	isort --check-only --diff && \
	pylint --rcfile=.pylint-travisrc pootle tests pytest_pootle

lint-js:
	cd ${JS_DIR} \
	&& npm run lint

lint-css:
	cd ${JS_DIR} \
	&& npm run stylelint

test-js:
	cd ${JS_DIR} \
	&& npm test

publish-pypi:
	python setup.py sdist ${FORMATS} upload

help:
	@echo "Help"
	@echo "----"
	@echo
	@echo "  assets - collect and rebuild the static assets"
	@echo "  build - create sdist with required prep"
	@echo "  docs - build Sphinx docs"
	@echo "  sprite - create CSS sprite"
	@echo "  clean - remove any temporal files"
	@echo "  test - run test suite"
	@echo "  pot - update the POT translations templates"
	@echo "  linguas - update the LINGUAS file with languages over 80% complete"
	@echo "  publish-pypi - publish on PyPI"
