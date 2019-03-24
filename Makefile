

test: lint-check

lint-check:
	pipenv run black --check *.py **/*.py

lint:
	pipenv run black *.py **/*.py

setup:
	pip install pipenv
	pipenv install --dev --three

clean:
	rm -rf dist

package: requirements.txt clean *.py */*.py
	pipenv run python setup.py sdist bdist_wheel

check-package: package
	twine check dist/*

publish-test: check-package
	twine upload --repository-url https://test.pypi.org/legacy/ dist/* 

publish-prod: check-package
	twine upload dist/*

requirements.txt:
	pipenv lock --requirements > $@