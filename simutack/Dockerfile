FROM ubuntu:20.04

# Non-interactive mode to prevent user input requests
ARG DEBIAN_FRONTEND=noninteractive

# Install some required packages
RUN apt-get -y update
RUN apt-get install -y apt-utils
RUN apt-get install -y git wget
RUN apt-get install -y cmake build-essential ninja-build
RUN apt-get install -y rsync libtiff-dev libpng16-16 libboost-all-dev libssl-dev
RUN apt-get install -y python3.8-dev python3.8-venv python3-pip 
RUN apt-get install -y npm

# Copy all necessary files into container (some are excluded with .dockerignore)
WORKDIR /simutack
ADD . .

# Install Python packages for application
RUN pip3 install --upgrade pip
RUN pip3 install --no-cache-dir -r python_requirements.txt

# Build Vue.js website
WORKDIR /simutack/webserver/simutack-web-ui
RUN chmod 777 .
ENV NODE_ENV=development

RUN npm install
RUN npm audit fix
RUN npm run build

# Start application
WORKDIR /simutack
CMD ["python3", "simutack", "-v", "--ip", "carla", "--port", "2000", "--carla-path", "/carla/PythonAPI/carla/dist/carla-0.9.13-py3.8-linux-x86_64.egg"]
