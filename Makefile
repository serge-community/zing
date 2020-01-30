CWD = $(shell pwd)
SRC_DIR = ${CWD}/pootle
WEBSITE_DIR = ${CWD}/website
STATIC_DIR = ${SRC_DIR}/static
# The ASSETS_DIR is where STATIC_ROOT configuration variable
# usually points to (see pootle/settings/10-base.conf)
ASSETS_DIR = ${SRC_DIR}/assets
JS_DIR = ${STATIC_DIR}/js
FORMATS=--formats=bztar
TEST_ENV_NAME = pootle_test_env

POOTLE_CMD = $(shell sh -c "command -v zing")
ifeq ($(POOTLE_CMD),)
	POOTLE_CMD=python manage.py
endif

.PHONY: all build clean test pot help docs assets

all: help

build: docs assets
	python setup.py sdist ${FORMATS} ${TAIL}

assets:
	cd ${JS_DIR} && \
	npm install && \
	npm run build -- --display-error-details && \
	cd ${CWD}
	${POOTLE_CMD} compilejsi18n
	mkdir -p ${ASSETS_DIR}

	${POOTLE_CMD} collectstatic --noinput --clear -i node_modules -i .tox -i docs ${TAIL}
	${POOTLE_CMD} assets build ${TAIL}

	chmod 664 ${ASSETS_DIR}/.webassets-cache/*

travis-assets:
	if [ -d "${ASSETS_DIR}/.webassets-cache" ]; then \
		echo "eating cache - yum!"; \
	else \
		cd ${JS_DIR} && \
		npm install && \
		npm run dev:nowatch && \
		cd ${CWD}; \
		${POOTLE_CMD} compilejsi18n; \
		mkdir -p ${ASSETS_DIR}; \
		${POOTLE_CMD} collectstatic --noinput --clear -i node_modules -i .tox -i docs ${TAIL}; \
		${POOTLE_CMD} assets build ${TAIL}; \
		chmod 664 ${ASSETS_DIR}/.webassets-cache/*; \
	fi

docs:
	cd ${WEBSITE_DIR} && \
	npm install && \
	npm run build ${TAIL}

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
	black --check . && \
	isort --check-only --diff && \
	pylint --rcfile=.pylint-travisrc pootle tests

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
	@echo "  docs - build the Zing website"
	@echo "  clean - remove temporary files"
	@echo "  test - run test suite"
	@echo "  pot - update the POT translations templates"
	@echo "  linguas - update the LINGUAS file with languages over 80% complete"
	@echo "  publish-pypi - publish on PyPI"
