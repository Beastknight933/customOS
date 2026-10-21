# Horizon OS Live Environment Startup
if [[ -z "$DISPLAY" ]] && [[ "$(tty)" == "/dev/tty1" || "$(tty)" == "/dev/ttyS0" ]]; then
    /usr/local/bin/horizon-install
fi
