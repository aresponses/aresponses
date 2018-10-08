init:
	@if ! [ -x "$$(command -v pyenv)" ]; then\
	  echo 'Error: pyenv is not installed.';\
	  exit 1;\
	fi
	pyenv install 3.6.6 -s
	export VENV_NAME="aresponses-3.6.6"; \
	if ! [ -d "$$(pyenv root)/versions/$${VENV_NAME}" ]; then\
		pyenv virtualenv 3.6.6 $${VENV_NAME};\
	fi; \
	pyenv local $${VENV_NAME}
	pip install --upgrade pip
	pip install -r requirements.txt --upgrade
#	pre-commit install

autoformat:
	black .

test:
	pytest

lint:
	pylava

deploy:
	git tag $$(python setup.py -V)
	git push --tags
	python setup.py bdist_wheel
	python setup.py sdist
	echo 'pypi.org Username: '
	read username && twine upload dist/* -u $$username;
