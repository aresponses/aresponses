# aresponses

an asyncio testing server for mocking external services

## Features
 - Fast mocks using actual network connections
 - allows mocking some types of network issues
 - use regular expression matching for domain, path, or method 
 - works with https requests as well (by switching them to http requests)
 
## Usage

*aresponses.add(host_pattern, path_pattern, method_pattern, response)*

Host, path, or method may be either strings (exact match) or regular expressions.

When a request is received the first matching response will be returned (based on the order it was received in.

Requires Python 3.6 or greater.

## Example
```python
import pytest
from aresponses import aresponses
from aiohttp import web

@pytest.mark.asyncio
async def test_bad_redirect(aresponses):
    aresponses.add('foo.com', '/', 'get', web.Response(text='hi', status=200))
    aresponses.add('foo.com', '/', 'get', web.Response(text='hi', status=301))
    
    url = 'http://foo.com'
    async with aiohttp.ClientSession(loop=event_loop) as session:
        async with session.get(url) as response:
            text = await response.text()
        print(text)  # 'hi'
        
        async with session.get(url) as response:
            # exception thrown about improper redirect
            text = await response.text()
        
        
    
```

## Todo
 - add passthrough option
 - make api identical to `responses`
 - allow response to be a function handler
 - request capture mode?
 - better story about how exceptions are handled

## Contributing

### Dev environment setup
  - **install pyenv**  - Makes it easy to install specific verisons of python and switch between them.
  - **install python 3.6.2** using pyenv - `pyenv install 3.6.2`
  - **install direnv** - Manages virtual environments and automatically enables them when switching directories
  - **clone (forked) github repo** -
  - **cd to project folder** - after typing `direnv allow`, direnv will create a virtualenvironment and switch you to it
  - **`pip install -r requirements.txt`** - install all the requirements
  
### Submitting a feature request  
  - **`git checkout -b my-feature-branch`** 
  - **make some cool changes**
  - **`pytest`** - do the tests pass?
  - **`pylama`** - is the code linter happy?
  - **create pull request**

### Updating package on pypi
    git tag 0.1
    git push --tags
    python setup.py bdist_wheel
    python setup.py sdist
    twine upload dist/* -u username
    
## Contibuters
Bryce Drennan, CircleUp <aresponses@brycedrennan.com>
