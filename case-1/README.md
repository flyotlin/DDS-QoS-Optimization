# Case 1
## How to Run
### Prepare fastdds environment
> On publisher/subscriber nodes

- `$ cd case-1/src`
- `$ fastddsgen -python SimpleString.idl`
- `$ cmake .`
- `$ make`
- `$ python3 subscriber.py <configName> <totalMsgs> <sendingRate> <topicName>`
- `$ python3 publisher.py <configName> <totalMsgs> <topicName>`

### Run the experiment
> On your own computer.

Prepare `inventory` from `inventory.Example` first!

- `$ cd dds-qos-optimization/case-1`
- `$ ansible-playbook -i inventory subscriber.yml`
  - Set up 3 subscribers each on 3 nodes
  - Notice `configName`/`totalMsgs`/`sendingRate` inside, others can be configured in `common_vars.yml`
- `$ ansible-playbook -i inventory publisher.yml`
  - Set up 3 publishers on 1 node
  - Notice `configName`/`totalMsgs` inside, others can be configured in `common_vars.yml`
- `$ ansible-playbook -i inventory collect.yml`
  - Collect logs from publisher and subscriber
  - Notice `localDest` inside

By following the above 4 instructions, you've gone through 1 trial.

## Publisher & Subscriber
### Publisher
- arguments
  - `configName`: yaml config name (e.g., OMG-Def)
  - `totalMsgs`: total messages (samples) sent
  - `sendingRate`: publish rate (messages/sec)
  - `topicName`: topic name to which publishes
### Subscriber
- arguments
  - `configName`: yaml config name (e.g., OMG-Def)
  - `totalMsgs`: total messages (samples) sent
  - `topicName`: topic name to which publishes
