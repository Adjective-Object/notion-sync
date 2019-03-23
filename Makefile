
pr: lint-check

lint-check:
	pipenv run autopep8 --exit-code *.py > /dev/null

lint:
	pipenv run autopep8 --in-place --aggressive *.py
