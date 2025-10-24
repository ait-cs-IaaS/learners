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

python3 -m venv venv
source venv/bin/activate

while [ "$#" -gt 0 ]; do
  case "$1" in
    -init)
        pip install -e .
  esac
done

mkdir /tmp/portal

# gunicorn backend:app --worker-class gevent --bind unix:/tmp/portal/portal.sock &
# gunicorn backend:app --worker-class gevent --bind 0.0.0.0:5000 &
# gunicorn_pid=$!
flask run --host=0.0.0.0 --debug


wait -n

cleanup
