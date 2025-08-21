FROM python:3.13.5-slim-bookworm

# Install Dependencies
RUN pip3 install pytest==8.4.1

# Install Providers
RUN pip3 install openai==1.100.2
RUN pip3 install anthropic==0.64.0

# Create user
RUN useradd -ms /bin/bash appuser
USER appuser

# Copy repo and set working directory
COPY --chown=appuser:appuser . /home/appuser/app
WORKDIR /home/appuser/app

# Make packages in app directory available
ENV PYTHONPATH="/home/appuser/app"

ENTRYPOINT [ "pytest", "-v", "-s", "-p", "no:cacheprovider" ]
