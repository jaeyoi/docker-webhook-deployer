#!/bin/bash
# Docker Deployer
#


set -e

VERSION="latest"
IMAGE="jaeyoi/docker-webhook-deployer:$VERSION"
CONTAINER_NAME="dwdc"
PORT=7000

# Use named volume
VOLUMES="-v webhooks:/etc/docker-webhook-deployer"


# Setup options for connecting to docker host
if [ -z "$DOCKER_HOST" ]; then
    DOCKER_HOST="/var/run/docker.sock"
fi
if [ -S "$DOCKER_HOST" ]; then
    DOCKER_ADDR="-v $DOCKER_HOST:$DOCKER_HOST -e DOCKER_HOST"
else
    DOCKER_ADDR="-e DOCKER_HOST -e DOCKER_TLS_VERIFY -e DOCKER_CERT_PATH"
fi


case "$1" in
  add-image|add-compose|remove|list)
    # Only allocate tty if we detect one
    if [ -t 1 ]; then
        DOCKER_RUN_OPTIONS="-t"
    fi
    if [ -t 0 ]; then
        DOCKER_RUN_OPTIONS="$DOCKER_RUN_OPTIONS -i"
    fi
    if [ $1 == "add-compose" ]; then
      docker cp $2 $CONTAINER_NAME:/opt/app/docker-compose.yml
      docker exec $DOCKER_RUN_OPTIONS $CONTAINER_NAME /opt/app/docker-webhook-deployer.py "$1" "/opt/app/docker-compose.yml"
    else
      docker exec $DOCKER_RUN_OPTIONS $CONTAINER_NAME /opt/app/docker-webhook-deployer.py "$@"
    fi
    ;;
  run)
    DOCKER_RUN_OPTIONS="--name $CONTAINER_NAME -p $PORT:$PORT"
    docker run -d $DOCKER_RUN_OPTIONS $DOCKER_ADDR $VOLUMES $IMAGE "$@"
    ;;
  stop)
    docker stop $CONTAINER_NAME
    docker rm $CONTAINER_NAME
    ;;
  logs)
    docker logs $CONTAINER_NAME
    ;;
  *)
    echo "Usage: docker-webhook-deployer {run|stop|add-image|add-compose|remove|list}." || true
    exit 1
    ;;
esac

exit 0
