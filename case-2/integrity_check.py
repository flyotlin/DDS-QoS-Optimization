import os


pwd = os.path.abspath(os.path.dirname(__file__))
collected_logs_path = os.path.join(pwd, 'collected_logs')

configs = ["OMG-Def", "OMG-Mod", "MS-1", "MS-10", "MS-100", "MS-1000"]
trialNum = 10

pubs = [1, 4, 7, 8, 9, 10, 11, 12, 13, 14, 15, 17]
subs = [x for x in range(1, 18)]


def main():
    incomplete_logs = []

    for conf in configs:
        for trial in range(1, trialNum + 1):
            # check pub
            for i in pubs:
                path = os.path.join(collected_logs_path, conf, str(trial), 'pub', f'p{i}.log')
                if not os.path.isfile(path):
                    incomplete_logs.append(f'{conf}-{trial}-p{i}')
            # check sub
            for i in subs:
                path = os.path.join(collected_logs_path, conf, str(trial), 'sub', f's{i}.log')
                if not os.path.isfile(path):
                    incomplete_logs.append(f'{conf}-{trial}-s{i}')

    print('Inpcomplete Logs:')
    print(incomplete_logs)


if __name__ == '__main__':
    main()
