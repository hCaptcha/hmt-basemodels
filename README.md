# <img height="60px" src="./static/human.svg" alt="human" />

This repository features the basemodels for job manifest data
consumed by hmt-escrow.

### Docker

In order to get going you need [Docker](https://www.docker.com/) installed on your computer.

### Getting started

First build the image that contains all the code and dependencies:

```
docker-compose build
```

Run the tests:
```
docker-compose run basemodels ./bin/test
```

Lint the python files:
```
docker-compose run basemodels ./bin/lint
```

### Manual
Setup the environment
```
virtualenv -p python3 venv
source venv/bin/activate
```
Run the tests:
```
python test.py
```

Lint the python files:
```
yapf --diff ./basemodels/__init__.py ./test.py
mypy ./basemodels/__init__.py ./test.py --ignore-missing-imports
```

## Note for maintainers: Deploying to PyPi

A build will automatically be deployed to PyPi from master if tagged with a version number.  This version number should  match the version in the `setup.py` file.

The tags will need to be pushed to master via a user that has the proper privileges (see the contributors of this repo).

Versioning should follow the [semver](https://semver.org/) versioning methodology and not introduce breaking changes on minor or patch-level changes.

## Have a question?

Join our [Telegram](https://t.me/hcaptchachat) channel, we will gladly answer your questions.

## License

MIT © HUMAN Protocol
