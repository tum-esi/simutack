FROM carlasim/carla:0.9.13

# Non-interactive mode to prevent user input requests
ARG DEBIAN_FRONTEND=noninteractive

# Switch to root user for setup
USER root

# Update nvidia GPG key
RUN rm /etc/apt/sources.list.d/cuda.list && \
    rm /etc/apt/sources.list.d/nvidia-ml.list && \
    apt-key del 7fa2af80 && \
    apt-get update && apt-get install -y --no-install-recommends wget && \
    wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2004/x86_64/cuda-keyring_1.0-1_all.deb && \
    dpkg -i cuda-keyring_1.0-1_all.deb && \
    apt-get update

# Install missing library
RUN apt-get update && \
    apt-get install -y libomp5 xdg-user-dirs xserver-xorg mesa-utils libvulkan1

# Switch back to carla user for execution
USER carla

# Set execution path
#WORKDIR /home/carla

# Run carla executable in headless mode (unset env variable is important for headless mode!)
CMD unset SDL_VIDEODRIVER && ./CarlaUE4.sh -vulkan -nosound -RenderOffScreen -carla-rpc-port=2000
