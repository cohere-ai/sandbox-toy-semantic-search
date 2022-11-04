APP ?= notion-semantic-search
PROJECT ?= cohere-sandbox-360501
COMPONENT ?= backend
VERSION ?= stable
REGISTRY ?= gcr.io/$(PROJECT)
IMAGE ?= $(REGISTRY)/$(APP)-$(COMPONENT)


download-python-docs:
	curl https://docs.python.org/3/archives/python-3.11.0-docs-html.zip --output python-docs.zip
	unzip python-docs.zip -d txt
	rm -r  txt/python-3.10.7-docs-text/whatsnew  # remote whatsnew because it adds a lot of noise
	rm python-docs.zip

download-python-docs-small:
	curl https://docs.python.org/3/archives/python-3.11.0-docs-html.zip --output python-docs.zip
	unzip python-docs.zip -d txt
	find txt -d 2 | grep -v tutorial | xargs rm -rd  # remove everything except the tutorial
	rm python-docs.zip

clean:
	rm -r txt
	rm embeddings.npz

embeddings:
	poetry run embed localtxt --root-dir txt --output-file embeddings.npz

build-data: download-python-docs embeddings

build-server:
	@DOCKER_DEFAULT_PLATFORM='linux/amd64' docker build --build-arg port=8080 -t $(IMAGE):$(VERSION) .

build-server-data: embeddings.npz
	-@docker rm $(APP)-$(COMPONENT)-data 2>/dev/null
	@docker create --name $(APP)-$(COMPONENT)-data $(IMAGE):$(VERSION)
	@docker cp embeddings.npz $(APP)-$(COMPONENT)-data:/data/embeddings.npz
	@docker commit $(APP)-$(COMPONENT)-data $(IMAGE):$(VERSION)

build: build-server build-server-data

shell: build
	@DOCKER_DEFAULT_PLATFORM='linux/amd64' docker run -e COHERE_TOKEN=$(COHERE_TOKEN) -it $(IMAGE):$(VERSION) /bin/bash

run: build
	@DOCKER_DEFAULT_PLATFORM='linux/amd64' docker run -e COHERE_TOKEN=$(COHERE_TOKEN) -p 8080:8080 -it $(IMAGE):$(VERSION)
