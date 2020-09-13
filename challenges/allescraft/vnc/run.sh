#!/usr/bin/env sh

VNC_PASSWORD=${VNC_PASSWORD:-ALLES}

Xvfb :0 -screen 0 1280x720x16 +extension GLX +extension RENDER &
sleep .5

export DISPLAY=:0.0

mkdir -p ~/.vnc
x11vnc -storepasswd "${VNC_PASSWORD}" ~/.vnc/passwd
x11vnc -q -usepw -bg -forever -shared -display :0

exec python3 /home/minecraft/minecraft.py run "${MINECRAFT_VERSION}" "${HOME}"
