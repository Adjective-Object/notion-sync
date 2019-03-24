

test: lint-check

lint-check:
	pipenv run black --check *.py

lint:
	pipenv run black *.py

setup:
	pip install pipenv
	pipenv install --dev --three

package: requirements.txt
	

requirements.txt:
	pipenv lock --requirements > $@