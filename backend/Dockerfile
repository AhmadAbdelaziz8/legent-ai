FROM python:3.12-slim

# Install system dependencies for computer use tools
RUN apt-get update && \
    apt-get install -y \
    # UI Requirements for computer use
    xvfb \
    x11vnc \
    xterm \
    xdotool \
    scrot \
    imagemagick \
    sudo \
    mutter \
    # Network tools
    net-tools \
    netcat-openbsd \
    # Userland apps
    firefox-esr \
    x11-apps \
    gedit \
    galculator \
    pcmanfm \
    unzip \
    # Taskbar/panel
    tint2 \
    # Additional X11 packages
    xserver-xorg-video-dummy \
    xserver-xorg-core \
    && apt-get clean

# Install noVNC for web-based VNC access
RUN apt-get update && \
    apt-get install -y git && \
    git clone --branch v1.5.0 https://github.com/novnc/noVNC.git /opt/noVNC && \
    git clone --branch v0.12.0 https://github.com/novnc/websockify /opt/noVNC/utils/websockify && \
    ln -s /opt/noVNC/vnc.html /opt/noVNC/index.html && \
    apt-get clean

# Setup user for computer use
ENV USERNAME=computeruse
ENV HOME=/home/$USERNAME
RUN useradd -m -s /bin/bash -d $HOME $USERNAME
RUN echo "${USERNAME} ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers

WORKDIR /app

COPY requirements.txt .

RUN pip install uv && uv pip install --system --no-cache-dir -r requirements.txt

COPY . /app

# Set environment variables for computer use
ARG DISPLAY_NUM=1
ARG HEIGHT=768
ARG WIDTH=1024
ENV DISPLAY_NUM=$DISPLAY_NUM
ENV HEIGHT=$HEIGHT
ENV WIDTH=$WIDTH
ENV DISPLAY=:${DISPLAY_NUM}

EXPOSE 8000
EXPOSE 6080
EXPOSE 5900

# Copy and make startup scripts executable
COPY scripts/ /app/scripts/
RUN chmod +x /app/scripts/*.sh
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# The command to run when the container starts
CMD ["/app/entrypoint.sh"]