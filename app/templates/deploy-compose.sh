#!/bin/sh

docker-compose -f $YML -p $PROJECT pull
docker-compose -f $YML -p $PROJECT stop # down?
docker-compose -f $YML -p $PROJECT up -d
