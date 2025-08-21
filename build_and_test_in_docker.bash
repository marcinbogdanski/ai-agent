#!/usr/bin/env bash

docker build -t ai-agent .

docker run -it --rm \
  --env-file=../secrets.env \
  ai-agent
