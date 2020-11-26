#!/bin/bash

source wait-for-database.sh
export DOCKER_ID=$(cat /proc/self/cgroup | grep -e docker | head -n 1 | cut -d/ -f3)

exec "$@"