#!/usr/bin/env bash

cleanup() {
    echo "Stopping processes..."
    kill -TERM "$gunicorn_pid" "$yarn_pid"
    wait
    echo "Processes stopped."
    exit
}

trap cleanup INT

cd frontend
yarn dev &
yarn_pid=$!
cd ..

python -m venv venv
source venv/bin/activate

while [ "$#" -gt 0 ]; do
  case "$1" in
    -init)
        pip install -e .
  esac
done

mkdir /tmp/learners

gunicorn backend:app --worker-class gevent --bind unix:/tmp/learners/learners.sock &
gunicorn_pid=$!


wait -n

cleanup