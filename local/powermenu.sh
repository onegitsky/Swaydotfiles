#!/bin/zsh

entries="⇠ Logout\n⭮ Reboot\n󰐥 Shutdown"

selected=$(echo -e $entries|wofi -a --hide-scroll --location=center -p "Power Menu" --width 250 --height 194 --dmenu --cache-file /dev/null | awk '{print tolower($2)}')

case $selected in
  logout)
    exec loginctl kill-session "${XDG_SESSION_ID}";;
  reboot)
    exec systemctl reboot;;
  shutdown)
	exec systemctl poweroff;;
esac
