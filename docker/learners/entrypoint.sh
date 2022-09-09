#!/bin/bash

# if [[ ! -f ${LEARNERS_CONFIG} ]]; then
#   wget --output-document=${LEARNERS_CONFIG} --quiet https://raw.githubusercontent.com/ait-cs-IaaS/learners/${LEARNERS_VERSION}/learners_config.yml
#   sed -i 's#sqlite:///learners_tracker.db#sqlite:////opt/learners/data/learners_tracker.db#g' ${LEARNERS_CONFIG}
# fi

gunicorn --bind 0.0.0.0:${LEARNERS_PORT:-8080} learners:app
