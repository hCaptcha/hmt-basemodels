# <img height="60px" src="./static/human.svg" alt="human" />

This repository features the basemodels for job manifest data
consumed by hmt-escrow.

### Docker

In order to get going you need [Docker](https://www.docker.com/) installed on your computer.

### Getting started

Run the tests:
```
bin/test
```

Lint the python files:
```
bin/lint
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

## Have a question?

Join our [Telegram](https://t.me/hcaptchachat) channel, we will gladly answer your questions.

## License

MIT © HUMAN Protocol
