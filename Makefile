setup: ## Command to setup the project
	pip install -r requirements.txt
	python setup.py develop

tests: ## Starts the CI pipeline
	tox
 
lint: ## Check for isort and flake8 rules
	flake8 src tests
	isort src

doc: ## Generate doc with Sphinx
	python setup.py doc

.PHONY: tests

help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'
