import argparse
import os


class BaseLog:
    def __init__(self, file_path: str, magic: str) -> None:
        self.raw_lines = self._read_file(file_path)
        self.validate(magic)
        self.clean_lines = self.clean(self.raw_lines)

    def _read_file(self, file_path: str) -> list:
        with open(file_path, 'r') as f:
            return f.read().strip().split('\n')

    def validate(self, magic: str) -> None:
        if magic != self.raw_lines[0]:
            raise Exception(f'Incorrect Log Type. Expect: [{magic}]. Actual: [{self.raw_lines[0]}]')

    def clean(self, lines: list) -> list:
        """Clean the irrelevant information, Overriden by Subclasses"""
        pass

    def get_nsamples(self) -> int:
        """Get Number of Samples Sent/Received"""
        return len(self.clean_lines)


class PubLog(BaseLog):
    def __init__(self, file_path: str) -> None:
        magic = "Start publisher."
        super().__init__(file_path, magic)

    def clean(self, lines: list) -> list:
        for (idx, line) in enumerate(lines):
            if "Sending Hello World!" in line:
                start_idx = idx
                break
        for (idx, line) in enumerate(reversed(lines)):
            if "Sending Hello World!" in line:
                end_idx = len(lines) - idx - 1
                break
        return lines[start_idx: end_idx + 1]


class SubLog(BaseLog):
    def __init__(self, file_path: str) -> None:
        magic = "Creating Subscriber."
        super().__init__(file_path, magic)

    def clean(self, lines: list) -> list:
        for (idx, line) in enumerate(lines):
            if "Received Hello World!" in line:
                start_idx = idx
                break
        for (idx, line) in enumerate(reversed(lines)):
            if "Received Hello World!" in line:
                end_idx = len(lines) - idx - 1
                break
        return lines[start_idx: end_idx + 1]


def main(args: list):
    pwd = os.path.abspath(os.path.dirname(__file__))
    config_name = args.config

    pub_logs = []
    for i in range(1, 11):
        for j in range(1, 4):
            path = f"{pwd}/logs/{config_name}/{i}/pub/pub_SimpleStringTopic_{j}.log"
            log = PubLog(path)
            pub_logs.append(log)

    sub_logs = []
    for i in range(1, 11):
        for j in range(1, 4):
            path = f"{pwd}/logs/{config_name}/{i}/sub/sub_SimpleStringTopic_{j}.log"
            sub_logs.append(SubLog(path))

    pub_samples = 0
    for log in pub_logs:
        pub_samples += log.get_nsamples()

    sub_samples = 0
    for log in sub_logs:
        sub_samples += log.get_nsamples()

    print(pub_samples, sub_samples)
    loss_rate = (pub_samples - sub_samples) / pub_samples
    print(f'Loss Rate: {loss_rate}')
    avg_loss_rate = loss_rate / 10
    print(f'Average Loss Rate: {avg_loss_rate}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", "-c", help="specify qos config name")

    args = parser.parse_args()
    main(args)
