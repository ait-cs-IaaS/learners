#!/bin/bash

gunicorn --bind 0.0.0.0:${LEARNERS_PORT:-8080} learners:app
