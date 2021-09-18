#!/bin/bash
cd "$HOME" || exit
while true; do
	sudo -E python3 /opt/KeyboardMacro/Macros.py
	if zenity --question --title="Restart Macros?" --text="The Macro Program has stopped, do you wish to restart it?"  --width=200
	then
		zenity --info --title="Restarting..." --text="Macro Program is restarting."
		continue
	else
		zenity --info --title="Exiting..." --text="Macro Program is exiting."
		exit
	fi
done
