#! /bin/bash

# Variables
trial_num=10
sleep_time=80
case_num=2

# set working directory
cd "$(dirname "$0")" && cd ../
pwd

for config in {"OMG-Def","OMG-Mod","MS-1","MS-10","MS-100","MS-1000"}; do
    for i in $(seq "$trial_num"); do
        python3 script/generate.py -p config/case-"$case_num"/configs.yaml -t "$i" -c "$config"
        ansible-playbook -i inventory.yaml playbook.yml
    done
done
