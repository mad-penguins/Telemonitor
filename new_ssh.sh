#!/bin/bash

ip=`echo $SSH_CONNECTION | cut -d " " -f 1`

#echo $ip

python3 /home/user/Telebot/send.py --ssh $USER $ip
