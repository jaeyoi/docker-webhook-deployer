#!/bin/sh

docker pull $IMAGE
docker stop $CONTAINER
docker rm $CONTAINER
docker run -d -p $PORT --name $CONTAINER $IMAGE
