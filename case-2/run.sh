#!/bin/bash

configs=("OMG-Def" "OMG-Mod" "MS-1" "MS-10" "MS-100" "MS-1000")
messages=30000
logDirname="collected_logs"

for rate in "1000" "2000"; do
    for i in {1..2}; do
        for config in ${configs[@]}; do
            for trialNum in {1..10}; do
                printf "Start trial $trialNum with config $config, rate $rate\n"
                time ansible-playbook -v -i inventory.yaml playbook.yml -e "trialNum=$trialNum config=$config messages=$messages rate=$rate logDirname=$logDirname-$messages-$rate-$i max_timeout=50"
            done
        done
    done
done
