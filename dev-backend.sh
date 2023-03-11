#!/usr/bin/env bash
gunicorn backend:app --worker-class gevent --bind localhost:5000
