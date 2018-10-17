python_version = 3.6.6
venv_prefix = aresponses
venv_name = $(venv_prefix)-$(python_version)

init:
	@if ! [ -x "$$(command -v pyenv)" ]; then\
	  @echo 'ERROR: pyenv is not installed.';\
	  @exit 1;\
	fi
	pyenv install $(python_version) -s
	@if ! [ -d "$$(pyenv root)/versions/$(venv_name)" ]; then\
		pyenv virtualenv $(python_version) $(venv_name);\
	fi;
	pyenv local $(venv_name)
	pip install --upgrade pip
	pip install -r requirements.txt --upgrade
	@echo "\nPython binary path: \n"
	@pyenv which python
	@echo "\n(Copy this path to tell PyCharm where the virtualenv is. You may have to click the refresh button in the pycharm file explorer.)\n"


autoformat:
	@black .

test:
	@pytest -n auto

lint:
	@pylava

deploy:
	pip install twine wheel
	git tag $$(python setup.py -V)
	git push --tags
	python setup.py bdist_wheel
	python setup.py sdist
	@echo 'pypi.org Username: '
	@read username && twine upload dist/* -u $$username;
