.DEFAULT_GOAL := help
CURRENT_DIR = $(shell pwd)
CLEAN_TARGETS = "*.out" "*.tar" "*.tgz" "*.gz"

clean: ## Deletes non essential files
	for i in $(CLEAN_TARGETS); do find . -name "$$i" -delete; done

prepare: clean ## Creates out dir
	mkdir -p ${CURRENT_DIR}/out

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
IMAGE_REGISTRY ?= kobejn/synex
TAG ?= 0.1
IMAGE ?= "$(IMAGE_REGISTRY):$(TAG)"
TEST_IMAGE ?= "$(IMAGE_REGISTRY):test"

DOCKER_RUN_CMD = docker run --rm \
		-v $(CURRENT_DIR)/synex/:/opt/synex \
		-v $(CURRENT_DIR)/synex.conf:/etc/synex.conf \
		-v $(CURRENT_DIR)/tests:/opt/synex-tests \
		-v $(CURRENT_DIR)/scripts:/opt/scripts \
		-v $(CURRENT_DIR)/out:/out \
		$(TEST_IMAGE)

SENTRY_PROJECT ?= synex
COMMIT_SHA = `git rev-parse HEAD`

UID = $(shell id -u)
GID = $(shell id -g)

local-run: build-image-test ## Run bash in synex test container locally
	docker run -it --rm \
		-v $(CURRENT_DIR)/synex/:/opt/synex \
		-v $(CURRENT_DIR)/synex.conf:/etc/synex.conf \
		-v $(CURRENT_DIR)/tests:/opt/synex-tests \
		-v $(CURRENT_DIR)/scripts:/opt/scripts \
		-v $(CURRENT_DIR)/out:/out \
		$(TEST_IMAGE) /bin/bash || true

unittest: build-image-test ## Run pytest in synex test container locally and generate coverage report
	$(DOCKER_RUN_CMD) pytest --cov=. /opt/synex-tests

stylecheck: build-image-test black pylint ## Runs stylechecker and static code analysis, read only mode

black: build-image-test ## Runs black stylechecker in read only mode
	$(DOCKER_RUN_CMD) /opt/scripts/stylecheck.sh black /out

black-fix: build-image-test ## Runs black stylechecker in fix mode
	$(DOCKER_RUN_CMD) /opt/scripts/stylecheck.sh black-fix /out

pylint: build-image-test ## Runs pylint static analysis
	$(DOCKER_RUN_CMD) /opt/scripts/stylecheck.sh pylint /out

build-image-test: ## Build container image for local testing
	docker build --build-arg UID=$(UID) --build-arg GID=$(GID) --target test -t $(TEST_IMAGE) .

build-image-release: ## Build release docker image
	docker build --target release -t $(IMAGE) .

push: ## Push Kubernetes type image to Dockerhub. Use variable TAG
	docker push $(IMAGE);

help: ## Display this help. Default target
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'
