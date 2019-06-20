#!/bin/bash                          

i3status -c /etc/i3status.conf | while :
do
    read line
    echo $line | python /home/mihai/git/netatmo-indicator/i3wm_wrapper.py /home/mihai/.netatmo-credentials.yaml || exit 1
    #echo "blaaa" | $netatmo || exit 1
done
