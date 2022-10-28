# run.sh
# common_vars.yaml
# host{1..4}.yaml
import os
import yaml
import argparse

def load_yaml(config_path: str) -> dict:
    # config_path shoudl be relative to /source
    pwd = os.path.abspath(os.path.dirname(__file__))
    config_path = os.path.join(pwd, '../', config_path)

    with open(config_path, 'r') as f:
        return yaml.load(f, Loader=yaml.CLoader)


def dump_yaml(data: dict, path: str) -> None:
    # path should be relative to /source
    pwd = os.path.abspath(os.path.dirname(__file__))
    path = os.path.join(pwd, '../', path)

    with open(path, 'w') as f:
        yaml.dump(data, f, Dumper=yaml.CDumper)


def generate_set_up_vars(args) -> None:
    config = load_yaml(args.path)
    set_up_vars = {
        'repoUrl': config['repoUrl'],
        'repoPath': config['repoPath'],
        'fastddsPath': config['fastddsPath'],
        'config': args.config
    }
    set_up_vars['basePath'] = os.path.join(set_up_vars['repoPath'], f'case-{config["case_num"]}')
    set_up_vars['logPath'] = os.path.join(set_up_vars['basePath'], 'log')
    set_up_vars['srcPath'] = os.path.join(set_up_vars['basePath'], 'src')

    dump_yaml(set_up_vars, 'set_up_vars.yaml')


def generate_host_vars(args, num: int = 4) -> None:
    config = load_yaml(args.path)

    for i in range(num):
        host_vars = {}
        host_vars['basePath'] = os.path.join(config['repoPath'], f'case-{config["case_num"]}')
        host_vars['logPath'] = os.path.join(host_vars['basePath'], 'log')
        host_vars['entities'] = config[f'host{i+1}']
        host_vars['topicPrefix'] = config['topicPrefix']

        dump_yaml(host_vars, f'host{i+1}_vars.yaml')


def generate_control_vars(args) -> None:
    config = load_yaml(args.path)

    control_vars = {
        'basePath': os.path.join(config['repoPath'], f'case-{config["case_num"]}')
    }

    dump_yaml(control_vars, 'control_vars.yaml')


def generate_logs_vars(args) -> None:
    config = load_yaml(args.path)

    entities = []
    for i in range(4):
        entities.extend(config[f'host{i+1}'])

    basePath = os.path.join(config['repoPath'], f'case-{config["case_num"]}')
    logs_vars = {
        'wait_for_timeout': config['wait_for_timeout'],
        'logPath': os.path.join(basePath, 'log'),
        'entities': entities,
        'collectedLogPath': os.path.join(config['controlNodeBasePath'], 'logs', f'case-{config["case_num"]}', str(args.config), str(args.trial))
    }

    dump_yaml(logs_vars, 'logs_vars.yaml')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--path', '-p', required=True, help='experiment config path relative to /source')
    parser.add_argument('--trial', '-t', required=True, help='current trial num')
    parser.add_argument('--config', '-c', required=True, help='current config')
    args = parser.parse_args()

    generate_set_up_vars(args)
    generate_host_vars(args)
    generate_control_vars(args)
    generate_logs_vars(args)
