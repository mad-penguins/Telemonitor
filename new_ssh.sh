#!/bin/bash

ip=`echo $SSH_CONNECTION | cut -d " " -f 1`

echo $ip
