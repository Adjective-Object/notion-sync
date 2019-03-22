## Setup

- copy `config-example.json` to `config.json`
- set token_v2 to the value of your token_v2 token on a logged-in session of notion
- set sync_root to the url of a collection view page (the database-as-rows page)

Then run:

```
pip3 install --user pipenv
pipenv install
pipenv run python ./sync.py
```
