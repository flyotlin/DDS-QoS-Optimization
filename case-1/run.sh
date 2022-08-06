#!/bin/bash

SLEEP_TIME=80
CONFIG=$1

for i in {1..10}
do
    echo "Start deploy pubs/subs in $i-th trial..."
    ansible-playbook -i inventory subscriber.yml -e "configName=$CONFIG"
    ansible-playbook -i inventory publisher.yml -e "configName=$CONFIG"

    echo "Sleeping now in $i-th trial..."
    sleep "$SLEEP_TIME"

    echo "Start collecting logs in $i-th trial..."
    ansible-playbook -i inventory collect.yml -e "times=$i config=$CONFIG"
done
