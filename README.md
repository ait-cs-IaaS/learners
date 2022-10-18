# Learners Environment ![workflow](https://github.com/ait-cs-IaaS/learners/actions/workflows/build.yaml/badge.svg)

Webinterface for accessing CR exercises.

## Build

```bash
python3 -m build
```

## Install

```bash
#pip
pip install ait-learners

#docker
docker pull ghcr.io/ait-cs-iaas/learners
```

## Run

```bash
gunicorn --bind 127.0.0.1:5000 learners:app
# or
flask run
# or
docker-compose up -d
```

## Develop

```bash
pip install -e .
```
