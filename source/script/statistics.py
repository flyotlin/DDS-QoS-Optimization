###
# ALL PATHs ARE RELATIVE TO /source
###

import argparse
import os
import yaml


pwd = os.path.abspath(os.path.dirname(__file__))

CONFIGS = ["OMG-Def", "OMG-Mod", "MS-1", "MS-10", "MS-100", "MS-1000"]
CONFIG_PATH = os.path.join(pwd, '../config/case-{case}/configs.yaml')     # string format template
LOG_PATH = '../logs/case-{case}'                    # string format template


def get_topics(case: int, hosts_num: int = 4) -> dict:
    """
    topics Example:
        `topics = {'t1': ['p1', 's1', 's2', 's3']}`
    """
    topics = {}

    with open(CONFIG_PATH.format(case=case), 'r') as f:
        config = yaml.load(f, Loader=yaml.CLoader)

    for i in range(1, hosts_num + 1):
        host = config[f'host{i}']
        for entity in host:
            e, t = entity.split(':')

            if t not in topics:
                topics[t] = [e]
            else:
                topics[t].append(e)

    return topics


def get_stats(config: str, topics: dict, trial: int, case: int) -> dict:
    """
    stat Example:
        `stats = {'t1': {'sent': [10000], 'received': [9000], 'pub': ['p1'], 'sub': ['s1', 's2', 's3'], 'pub_num': 1, 'sub_num': 3, 'loss_rate': 0.22, 'throughput': 0.92}}`
    """
    stats = {}
    pwd = os.path.abspath(os.path.dirname(__file__))
    log_path = os.path.join(pwd, '../', LOG_PATH.format(case=case), config)

    for k, v in topics.items(): # 每個 topic
        stats[k] = {
            'sent': [],     # 每個 trial send 多少
            'received': [], # 每個 trial receive 多少
            'pubs': [],     # topic 下有哪些 pub
            'subs': [],     # topic 下有哪些 sub
            'pubs_num': -1, #
            'subs_num': -1,
            'loss_rate': -1,
            'throughput': -1
        }

        # get pubs, subs first (or this would repeat 10 times)
        for entity in v:
            if entity.startswith('p'):
                stats[k]['pubs'].append(entity)
            elif entity.startswith('s'):
                stats[k]['subs'].append(entity)
        stats[k]['pubs_num'] = len(stats[k]['pubs'])
        stats[k]['subs_num'] = len(stats[k]['subs'])

        # get sent/received from 10 trials
        for i in range(1, trial + 1):   # 做10次
            sent = 0    # in this trial
            received = 0    # in this trial

            # accumulate sent/received from pubs/subs
            for p in stats[k]['pubs']:
                sent += get_sent(os.path.join(log_path, str(i), f'{p}.log'))
            for s in stats[k]['subs']:
                received += get_received(os.path.join(log_path, str(i), f'{s}.log'))

            # put back to stats
            stats[k]['sent'].append(sent)
            stats[k]['received'].append(received)

        # calculate loss rate
        total_sent = 0
        total_received = 0
        for s in stats[k]['sent']:
            total_sent += (s * stats[k]['subs_num'])
        for r in stats[k]['received']:
            total_received += (r * stats[k]['pubs_num'])

        stats[k]['loss_rate'] = ((total_sent - total_received) / total_sent) / trial

    return stats


def get_sent(path: str) -> int:
    sent = 0

    try:
        with open(path, 'r') as f:
            lines = f.read().strip().split('\n')
            for line in lines:
                if line.startswith('Sending '):
                    sent += 1
    except Exception:
        print(f'Not found error: {path}')

    return sent


def get_received(path: str) -> int:
    received = 0

    try:
        with open(path, 'r') as f:
            lines = f.read().strip().split('\n')
            for line in lines:
                if line.startswith('Received '):
                    received += 1
    except Exception:
        print(f'Not found error: {path}')

    return received


def main(args: argparse.Namespace):
    topics = get_topics(args.case)

    for config in CONFIGS:
        stats = get_stats(config, topics, args.trial, args.case)

        print(f'\n\n\n{config}:\n')
        for k, v in stats.items():
            print(sum(v["sent"]) / len(v["sent"]))
            print(sum(v["received"]) / len(v["received"]))
            print(f'Topic {k} loss rate: {v["loss_rate"]}')


def get_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument('--trial', '-t', required=True, type=int)
    parser.add_argument('--case', '-c', required=True)

    args = parser.parse_args()
    return args


if __name__ == '__main__':
    args = get_args()
    main(args)
