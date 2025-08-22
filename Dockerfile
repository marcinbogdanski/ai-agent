FROM python:3.13.5-slim-bookworm

# DEVELOPMENT: Git
# - required for VSCode to highlight changes
RUN apt-get update && apt-get install -y -qq --no-install-recommends git \
    && rm -rf /var/lib/apt/lists/*
# DEVELOPMENT: Claude Code
# - npm for Claude Code, procps for IDE integration to work
RUN apt-get update && apt-get install -y -qq --no-install-recommends npm procps \
    && rm -rf /var/lib/apt/lists/*
# DEVELOPMENT: Claude Code usage monitor
RUN pip3 install claude-monitor

# Install Dependencies
RUN pip3 install pytest==8.4.1

# Install Providers
RUN pip3 install openai==1.100.2
RUN pip3 install anthropic==0.64.0

# Create user
RUN useradd -ms /bin/bash appuser
USER appuser

# DEVELOPMENT: Claude Code
RUN mkdir -p /home/appuser/.npm-global
RUN npm config set prefix /home/appuser/.npm-global
ENV PATH=/home/appuser/.npm-global/bin:$PATH
RUN npm install -g @anthropic-ai/claude-code

# Copy repo and set working directory
COPY --chown=appuser:appuser . /home/appuser/app
WORKDIR /home/appuser/app

# Make packages in app directory available
ENV PYTHONPATH="/home/appuser/app"

ENTRYPOINT [ "pytest", "-v", "-s", "-p", "no:cacheprovider" ]
