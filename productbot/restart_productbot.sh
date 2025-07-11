#!/bin/bash

pkill -ef productbot.py

echo
sleep 1

cd /home/bios/productbot

screen -dmS productbot -L -Logfile /home/bios/productbot/logs/productbot_screen.log /usr/bin/python3 /home/bios/productbot/productbot.py

echo "Restarted productbot"
