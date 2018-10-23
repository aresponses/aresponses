python_version = 3.6.6
venv_prefix = aresponses
venv_name = $(venv_prefix)-$(python_version)
pyenv_instructions=https://github.com/pyenv/pyenv#installation
pyenv_virt_instructions=https://github.com/pyenv/pyenv-virtualenv#pyenv-virtualenv


init: require_pyenv
	@pyenv install $(python_version) -s
	@echo "\033[0;32m ✔️  🐍 $(python_version) installed \033[0m"
	@if ! [ -d "$$(pyenv root)/versions/$(venv_name)" ]; then\
		pyenv virtualenv $(python_version) $(venv_name);\
	fi;
	@pyenv local $(venv_name)
	@echo "\033[0;32m ✔️  🐍 $(venv_name) virtualenv activated \033[0m"
	pip install --upgrade pip
	pip install -r requirements.txt --upgrade
	@echo "\nEnvironment setup! ✨ 🍰 ✨ 🐍 \n\nCopy this path to tell PyCharm where your virtualenv is. You may have to click the refresh button in the pycharm file explorer.\n"
	@echo "\033[0;32m"
	@pyenv which python
	@echo "\n\033[0m"


autoformat:
	@black .

test:
	@pytest -n auto
	@echo "The tests pass! ✨ 🍰 ✨"

lint:
	@pylava
	@echo "No linting errors - well done! ✨ 🍰 ✨"

deploy:
	pip install twine wheel
	git tag $$(python setup.py -V)
	git push --tags
	python setup.py bdist_wheel
	python setup.py sdist
	@echo 'pypi.org Username: '
	@read username && twine upload dist/* -u $$username;
	@echo "Deploy successful! ✨ 🍰 ✨"


require_pyenv:
	@if ! [ -x "$$(command -v pyenv)" ]; then\
	  echo '\n\033[0;31m ❌ pyenv is not installed.  Follow instructions here: $(pyenv_instructions)\n\033[0m';\
	  exit 1;\
	else\
	  echo "\033[0;32m ✔️  pyenv installed\033[0m";\
	fi
	@if ! [ -d "$$(pyenv root)/plugins/pyenv-virtualenv" ]; then\
	  echo '\n\033[0;31m ❌ pyenv virtualenv is not installed.  Follow instructions here: $(pyenv_virt_instructions) \n\033[0m';\
	  exit 1;\
	else\
	  echo "\033[0;32m ✔️  pyenv-virtualenv installed\033[0m";\
	fi