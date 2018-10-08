[![build status](https://travis-ci.org/CircleUp/aresponses.svg)](https://travis-ci.org/CircleUp/aresponses)

# aresponses

an asyncio testing server for mocking external services

## Features
 - Fast mocks using actual network connections
 - allows mocking some types of network issues
 - use regular expression matching for domain, path, or method 
 - works with https requests as well (by switching them to http requests)
 - works with callables
 
## Usage

*aresponses.add(host_pattern, path_pattern, method_pattern, response)*

Host, path, or method may be either strings (exact match) or regular expressions.

When a request is received the first matching response will be returned (based on the order it was received in.

Requires Python 3.6 or greater.

## Example
```python
import pytest
import aiohttp

@pytest.mark.asyncio
async def test_foo(aresponses):
    # text as response (defaults to status 200 response)
    aresponses.add('foo.com', '/', 'get', 'hi there!!')

    # custom status code response
    aresponses.add('foo.com', '/', 'get', aresponses.Response(text='error', status=500))

    # passthrough response (makes an actual network call)
    aresponses.add('httpstat.us', '/200', 'get', aresponses.passthrough)

    # custom handler response
    def my_handler(request):
        return aresponses.Response(status=200, text=str(request.url))

    aresponses.add('foo.com', '/', 'get', my_handler)

    url = 'http://foo.com'
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            text = await response.text()
            assert text == 'hi there!!'

        async with session.get(url) as response:
            text = await response.text()
            assert text == 'error'
            assert response.status == 500

        async with session.get('https://httpstat.us/200') as response:
            text = await response.text()
        assert text == '200 OK'

        async with session.get(url) as response:
            text = await response.text()
            assert text == 'http://foo.com/'
```

```python
import aiohttp
import pytest
import aresponses

@pytest.mark.asyncio
async def test_foo(event_loop):
    async with aresponses.ResponsesMockServer(loop=event_loop) as arsps:
        arsps.add('foo.com', '/', 'get', 'hi there!!')
        arsps.add(arsps.ANY, '/', 'get', arsps.Response(text='hey!'))
        
        async with aiohttp.ClientSession(loop=event_loop) as session:
            async with session.get('http://foo.com') as response:
                text = await response.text()
                assert text == 'hi'
            
            async with session.get('https://google.com') as response:
                text = await response.text()
                assert text == 'hey!'
        
```


## Contributing

### Dev environment setup
  - **install pyenv and pyenv-virtualenv**  - Makes it easy to install specific verisons of python and switch between them. Make sure you install the virtualenv bash hook
  - `git clone git@github.com:CircleUp/aresponses.git`
  - `cd aresponses`
  - `make init` - creates the virtualenvironment and installs all the requirements
  
### Submitting a feature request  
  - **`git checkout -b my-feature-branch`** 
  - **make some cool changes**
  - **`make autoformat`** - do the tests pass?
  - **`make test`** - do the tests pass?
  - **`make lint`** - is the code linter happy?
  - **create pull request**

### Updating package on pypi
    git tag 0.1
    git push --tags
    python setup.py bdist_wheel
    python setup.py sdist
    twine upload dist/* -u username

## Changelog

#### 1.1.1
- regex fix for Python 3.7.0

#### 1.1.0
- Added passthrough option to permit live network calls
- Added example of using a callable as a response

#### 1.0.0

- Added an optional `match_querystring` argument that lets you match on querystring as well


## Contributors
* Bryce Drennan, CircleUp <aresponses@brycedrennan.com>
* Marco Castelluccio, Mozilla <mcastelluccio@mozilla.com>
* Jesse Vogt, CircleUp <jesse.vogt@gmail.com>
* Pavol Vargovcik, Kiwi.com <pavol.vargovcik@gmail.com>
