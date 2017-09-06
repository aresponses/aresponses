# aresponses

an asyncio testing server for mocking external services

## Updating package on pypi

    git tag 0.1
    git push --tags
    python setup.py bdist_wheel
    python setup.py sdist
    twine upload dist/* -u username
    
