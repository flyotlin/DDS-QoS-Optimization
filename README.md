# DDS Qos Optimization
DDS Qos Optimization helps set up FastDDS publishers and subscribers on multiple hosts.

## Prerequisite
- FastDDS installed on all hosts (Physical Machines, VMs, Containers).

  Install in the same directory on all hosts.
  
  You can refer to [Linux installation from binaries](https://fast-dds.docs.eprosima.com/en/latest/installation/binaries/binaries_linux.html)
## How to use
1. Set up host(Physical Machines, VMs, Containers) configurations
  - `$ cd DDS-QoS-Optimization/source`
  - `$ cp inventory.yaml.Example inventory.yaml`
  - Fill in hosts IP, port, username, and path to ssh private key.
2. Set up experiment case configurations
  - `$ cd DDS-QoS-Optimization/source/config`
  - `$ mkdir case-[number]`
  - `$ cp configs.yaml.Example case-[number]/configs.yaml`
  - Edit configs.yaml (Details explained in [Experiment Case Configuration](#experiment-case-configuration))
3. Run the experiment case
  - `$ cd DDS-QoS-Optimization/source/script`
  - `$ bash run.sh [number] [number-of-trials] [sleep-time]`
4. Get number of messages sent/received and loss rate
  - `$ cd DDS-QoS-Optimization/source/script`
  - `$ python3 statistics.py -t [number-of-trials] -c [number]`

## How system works
By executing `playbook.yml`, you got several stages:
1. Set up the experiment
2. Set up publishers and subscribers on each hosts
  - By `create.sh` generated by template in stage 1, here we specify *name*, *topic*, *#messages*, *sending rate* to create pubs and subs.
  - But as for now, all publishers aren't sending anything yet.
3. Make all publishers start sending messages
  - Set `.flag` on all hosts to 1, so that all publishers start sending.
4. Collect publisher/subscriber logs from hosts to controlNode

## Experiment Case Configuration
### What need to be configured
1. **Case number**
2. **Publisher and Subscriber settings**
### Detail explained
- `repoUrl`: Git remote URL of *DDS-QoS-Optimization*
- `fastddsPath`: Absolute path to directory where FastDDS installed
- `repoPath`: Absolute path to where you want *DDS-QoS-Optimization* cloned on hosts by `playbook.yml`
- `case_num`: Experiment Case number
- `transport`: Currently not working, default transport in FastDDS is used.
- `controlNodeBasePath`
  - controlNode: where you execute `playbook.yml`
  - Absolute path to *DDS-QoS-Optimization* on controlNode.
- `wait_for_timeout`: Wait for publishers sent all messages in this Experiment Case
- `topicPrefix`: Set up a prefix for each topic
- `host[number]`:
  - `[number]` depends on how many hosts you got
  - in each `host[number]`, you can append an entity (publisher or subscriber)
  - **publisher**
    - in format: `p[number]:t[number]:[number-of-messages]:[sending-rate]`
    - e.g., `p1:t1:10000:1000`
  - **subscirber**
    - in format: `s[number]:t[number]:[number-of-messages]`
    - e.g., `s1:t1:10000`
  - Make sure the number of messages received by subscriber matches that from publisher to the same topic.
