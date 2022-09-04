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
    config = load_yaml(args.config)
    set_up_vars = {
        'repoUrl': config['repoUrl'],
        'repoPath': config['repoPath'],
    }
    set_up_vars['basePath'] = os.path.join(set_up_vars['repoPath'], f'case-{config["case_num"]}')
    set_up_vars['logPath'] = os.path.join(set_up_vars['basePath'], 'log')

    dump_yaml(set_up_vars, 'set_up_vars.yaml')


def generate_host_vars(args) -> None:
    pass


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', '-c', required=True, help='experiment config path relative to /source')
    args = parser.parse_args()

    generate_set_up_vars(args)
    generate_host_vars(args)
