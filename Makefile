
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

#---- Packaging ----

package: requirements.txt clean *.py */*.py
	pipenv run python setup.py sdist bdist_wheel

requirements.txt: Pipfile Pipfile.lock
	pipenv run pipenv_to_requirements

#---- Publishing ----

check-package: package
	pipenv run twine check dist/*

publish-test: check-package
	pipenv run twine upload --repository-url https://test.pypi.org/legacy/ dist/* 

publish-prod: check-package
	pipenv run twine upload dist/*

publish-travis: check-package
	pipenv run twine upload dist/* -u $$PYPI_USERNAME -p $$PYPI_PASSWORD

travis:
	make test

travis-deploy:
	git checkout master ;
	./scripts/bump-version-from-commit.sh ;
	./scripts/push-and-publish-if-changed.sh ;
