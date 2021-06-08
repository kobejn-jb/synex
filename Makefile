.DEFAULT_GOAL := help
CURRENT_DIR = $(shell pwd)
PYTHON_MODULES ?= $(shell find synex -name [a-z]*.py)
BLACK_EXCLUDE = "/(\.eggs|\.git|\.hg|\.mypy_cache|\.tox|\.venv|_build|buck-out|build|dist)/"
CLEAN_TARGETS = "*.out" "*.tar" "*.tgz" "*.gz"

clean: ## Deletes non essential files
	for i in $(CLEAN_TARGETS); do find . -name "$$i" -delete; done
	rm -rf temp
	rm -rf archive

prepare: clean ## Creates archive folder
	mkdir -p ${CURDIR}/archive

stylecheck: black pylint ## Runs stylechecker and static code analysis, read only mode

black: ## Runs black stylechecker in read only mode
	black . -l 120 -S -t py36 --check --diff --exclude $(BLACK_EXCLUDE) > black.out

black-fix: ## Runs black stylechecker in fix mode
	black . -l 120 -S -t py36 --exclude $(BLACK_EXCLUDE)

pylint: ## Runs pylint static analysis
	pylint -j 4 ${PYTHON_MODULES} > pylint.out

package: tar ## Creates the application package in the archive dir

tar:
	mkdir -p archive
	tar --exclude=.git --exclude=.cache --exclude=temp \
	--exclude=venv \
	--exclude=**/*.pyc \
	--exclude=**/__pycache__ \
	--exclude=**/*.log \
	--exclude=*.out \
	--exclude=.coverage \
	-czf archive/synex.tgz synex

# Docker specific Make commands are below
IMAGE_REGISTRY ?= synex
TAG ?= 0.1
IMAGE ?= "$(IMAGE_REGISTRY):$(TAG)"
TEST_IMAGE ?= "$(IMAGE_REGISTRY):test"

SENTRY_PROJECT ?= synex
COMMIT_SHA = `git rev-parse HEAD`

UID = $(shell id -u)
GID = $(shell id -g)

local-run: build-image-test ## Run bash in synex test container locally
	docker run -it --rm \
		-v $(CURRENT_DIR)/synex/:/opt/synex \
		-v $(CURRENT_DIR)/synex.conf:/etc/synex.conf \
		-v $(CURRENT_DIR)/tests:/opt/synex-tests \
		$(TEST_IMAGE) /bin/bash || true

unittests: build-image-test ## Run pytest in synex test container locally
	docker run -it --rm \
		-v $(CURRENT_DIR)/synex/:/opt/synex \
		-v $(CURRENT_DIR)/synex.conf:/etc/synex.conf \
		-v $(CURRENT_DIR)/tests:/opt/synex-tests \
		$(TEST_IMAGE) pytest --cov=. /opt/synex-tests

build-image-test: ## Build container image for local testing
	docker build --build-arg UID=$(UID) --build-arg GID=$(GID) --target test -t $(TEST_IMAGE) .

build-image-release: ## Build release docker image
	docker build --target release -t $(IMAGE) .

push: ecr_login ## Push Kubernetes type image to Dockerhub. Use variable TAG
	docker push $(IMAGE);

help: ## Display this help. Default target
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'
