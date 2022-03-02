# Learners Environment ![workflow](https://github.com/ait-cs-IaaS/learners/actions/workflows/cicd.yaml/badge.svg)


Webinterface for accessing CR exercises.



## Build

```bash
python3 -m build
```

## Run

```bash
gunicorn --bind 127.0.0.1:5000 learners:app
# or
flask run
```

## Develop

```bash
pip install -e .
```
