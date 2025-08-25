#!/usr/bin/env bash

docker build -t ai-agent .

docker run -it --rm \
  -e MY_ANTHROPIC_API_KEY=${MY_ANTHROPIC_API_KEY} \
  ai-agent
