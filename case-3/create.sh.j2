#!/bin/bash

scriptPath=$(cd "$(dirname "${BASH_SOURCE[0]}")"; pwd -P)

PUB="$scriptPath"/src/publisher.py
SUB="$scriptPath"/src/subscriber.py

name=$1                     # pub/sub name, also log file name
type=$2                     # either `pub` or `sub`
topic=$3                    # topic name publishes and subscribes to
config={{ config }}         # qos config name
messages={{ messages }}     # total messages published
rate={{ rate }}             # publisher message sending rate (messages/sec)

source "{{ fastddsPath }}"

if [ "pub" == "$type" ]; then
    echo "Publisher created"
    nohup python3 "$PUB" --config="$config" --messages="$messages" \
        --topic="$topic" --rate="$rate" &> {{ logPath }}/"$name".log &
    exit 0
elif [ "sub" == "$type" ]; then
    echo "Subscriber created"
    nohup python3 "$SUB" --config="$config" --messages="$messages" \
        --topic="$topic" &> {{ logPath }}/"$name".log &
    exit 0
else
    echo "Wrong type (only pub, sub accepted)"
    exit 1
fi
