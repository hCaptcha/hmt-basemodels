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
pytest tests
```

Lint the python files:
```
yapf --diff ./basemodels/__init__.py ./test.py
mypy ./basemodels/__init__.py ./test.py --ignore-missing-imports
```
## How to use model
Using the new model (based on pydantic library)
```python
import basemodels
from pydantic.v1 import ValidationError

model = {
    'job_mode': 'batch',
    'request_type': 'image_label_area_select',
    'unsafe_content': False,
    'task_bid_price': 1,
    ...
}
# Validate model on creation
try:
   manifest = basemodels.Manifest(**model)
except ValidationError as e:
   print(e.json())
# Or creating model without validation
manifest = basemodels.Manifest.construct(**model)
# See https://pydantic-docs.helpmanual.io/usage/models/#creating-models-without-validation
```
## Note for maintainers: Deploying to PyPi

A build will automatically be deployed to PyPi from master if tagged with a version number.  This version number should  match the version in the `setup.py` file.

The tags will need to be pushed to master via a user that has the proper privileges (see the contributors of this repo).

Versioning should follow the [semver](https://semver.org/) versioning methodology and not introduce breaking changes on minor or patch-level changes.

### Manual deploy to PyPi
In root folder
- `virtualenv -p python3 venv`
- `source venv/bin/activate`
- `pipenv install --dev`
- `pip install twine`
- `python3 setup.py sdist bdist_wheel`
- `twine upload dist/*`


## Have a question?

Open an issue!

## License

MIT © HUMAN Protocol 2020


