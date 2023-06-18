FROM ubuntu:20.04

# Non-interactive mode to prevent user input requests
ARG DEBIAN_FRONTEND=noninteractive

# Switch to bash (instead of /bin/sh)
SHELL ["/bin/bash", "-c"]

# Set permissions of /tmp directory to prevent errors for apt-get update
RUN chmod 1777 /tmp

# Install missing packages
RUN apt-get -y update
RUN apt-get install -y
RUN apt-get install -y build-essential libpng16-16 libtiff-dev libboost-all-dev rsync libssl-dev 
RUN apt-get install -y git cmake ninja-build wget
RUN apt-get install -y python3-dev python3-venv python3-pip

WORKDIR /autopilot
ADD tracks ./tracks/
ADD . .

# Install Python packages for application
RUN pip3 install --upgrade pip
RUN pip3 install --no-cache-dir -r python_requirements.txt

CMD ["python3","Autopilot.py"]
