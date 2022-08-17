#!/bin/bash

configs=("OMG-Def" "OMG-Mod" "MS-1" "MS-10" "MS-100" "MS-1000")


for rate in "1000" "2000"
do
    for config in ${configs[@]}
    do
        for trialNum in {1..10}
        do
            printf "Start trial $trialNum with config $config, rate $rate\n"
            time ansible-playbook -v -i inventory.yaml playbook.yml -e "trialNum=$trialNum config=$config messages=20000 rate=$rate"
        done
    done
done
