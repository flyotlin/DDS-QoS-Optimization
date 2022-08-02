import yaml


class HistoryQosConf:
    def __init__(self, kind: str, depth: int) -> None:
        self.kind = kind
        self.depth = depth


class ReliabilityQosConf:
    def __init__(self, kind: str, max_blocking_time: int) -> None:
        self.kind = kind
        self.max_blocking_time = max_blocking_time


class ResourceLimitsQosConf:
    def __init__(self, max_samples: int, max_instances: int, max_samples_per_instance: int) -> None:
        self.max_samples = max_samples
        self.max_instances = max_instances
        self.max_samples_per_instance = max_samples_per_instance

        self.allocated_samples = 100
        self.extra_samples = 1


# class YamlConfig is used by Publisher/Subscriber for internal QoS setting
class YamlConfig:
    def __init__(
            self,
            history: HistoryQosConf,
            reliability: ReliabilityQosConf,
            resourceLimits: ResourceLimitsQosConf) -> None:
        self.history = history
        self.reliability = reliability
        self.resourceLimits = resourceLimits

    @classmethod
    def create_from_yaml(cls, path: str):
        config = cls.load_yaml_as_dict(path)

        history = cls.create_history(config)
        reliability = cls.create_reliability(config)
        resourceLimits = cls.create_resourceLimits(config)

        return YamlConfig(history, reliability, resourceLimits)

    @classmethod
    def load_yaml_as_dict(cls, path: str) -> dict:
        with open(path, 'r') as f:
            return yaml.load(f, Loader=yaml.CLoader)

    @classmethod
    def create_history(cls, config: dict) -> HistoryQosConf:
        kind = config['History']['kind']
        depth = 1 if config['History']['depth'] == -1 else config['History']['depth']
        return HistoryQosConf(kind, depth)

    @classmethod
    def create_reliability(cls, config: dict) -> ReliabilityQosConf:
        kind = config['Reliability']['kind']
        max_blocking_time = config['Reliability']['max_blocking_time']
        return ReliabilityQosConf(kind, max_blocking_time)

    @classmethod
    def create_resourceLimits(cls, config: dict) -> ResourceLimitsQosConf:
        max_samples = config['ResourceLimits']['max_samples']
        max_instances = config['ResourceLimits']['max_instances']
        max_samples_per_instance = config['ResourceLimits']['max_samples_per_instance']
        return ResourceLimitsQosConf(max_samples, max_instances, max_samples_per_instance)
