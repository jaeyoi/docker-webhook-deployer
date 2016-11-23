#!/bin/sh

docker pull $IMAGE
docker stop $CONTAINER
docker run -d -p $PORT:$PORT --name $CONTAINER $IMAGE
