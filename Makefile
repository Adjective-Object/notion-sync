

test: lint-check

lint-check:
	pipenv run black --check **/*.py

lint:
	pipenv run black **/*.py

setup:
	pip install pipenv
	pipenv install --dev --three

clean:
	rm -rf dist

package: requirements.txt clean
	pipenv run python setup.py sdist bdist_wheel

publish-test: package
	twine check dist/*
	twine upload --repository-url https://test.pypi.org/legacy/ dist/* 

requirements.txt:
	pipenv lock --requirements > $@