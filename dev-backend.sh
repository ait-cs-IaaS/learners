#!/usr/bin/env bash
gunicorn backend:app --worker-class gevent --bind 0.0.0.0:5000
