import argparse
import fastdds
import json
import os
import SimpleString
import time

from threading import Condition
from config import YamlConfig


class WriterListener(fastdds.DataWriterListener):
    FLAG_FILE = ".flag"
    SLEEP_TIME = 0.5

    def __init__(self, writer):
        self._writer = writer    # class Writer defined below
        super().__init__()

    def on_publication_matched(self, writer, info):
        if 0 < info.current_count_change:
            print("Publisher matched subscriber {}".format(info.last_subscription_handle), flush=True)
            self.monitor_flag(self.FLAG_FILE, self.SLEEP_TIME)
        else:
            print("Publisher unmatched subscriber {}".format(info.last_subscription_handle), flush=True)
            self._writer._cvDiscovery.acquire()
            self._writer._matched_reader -= 1
            self._writer._cvDiscovery.notify()
            self._writer._cvDiscovery.release()

    def monitor_flag(self, flag_name: str = ".flag", sleep_time: float = 0.5):
        pwd = os.path.abspath(os.path.dirname(__file__))
        while True:
            with open(os.path.join(pwd, "../", flag_name), "r") as f:
                flag = f.read()
                if "1" == flag:
                    self._writer._cvDiscovery.acquire()
                    self._writer._matched_reader += 1
                    self._writer._cvDiscovery.notify()
                    self._writer._cvDiscovery.release()
                    break
            time.sleep(sleep_time)



class Writer:
    def __init__(
            self,
            config: YamlConfig = None,
            totalMsgs: int = 10,
            sendingRate: int = 10,
            topicName: str = "SimpleStringTopic",
            context: dict = {}) -> None:
        self.config = config
        self.totalMsgs = totalMsgs
        self.sendingRate = sendingRate
        self.topicName = topicName
        self.msg = "RErRxZp9fprLbyZD1GXtKujEMyIfxI15AyB5sxVRaN96kB4auk9a8NJ69gYlpMySpZ9jXWFuf1hOGaUVaHZr4zhoHh5wSOT6tUhu7UZpIaainlUBgL3N6xZSuczTKVL4Q7DgBW7mm2mOwKeJLQnosqGIPZb1V89z4toJUu7nTHKxx3TGQLjNOLnm7Hs3A6jlWkawQeEbnuoZUdDYsBHU4cZz7Hr7y0TqoZJWCjIYpyLCV3PaAqNYXLYloqQr9YM"

        self.context = context
        self.context["message"] = self.msg

        self._matched_reader = 0
        self._cvDiscovery = Condition()
        self.index = 1

        self.participant = self.create_participant()
        self.topic = self.create_topic(name=self.topicName)
        self.publisher = self.create_publisher()
        self.writer = self.create_datawriter()

    def write(self, msg: str = "Hello World!"):
        data = SimpleString.SimpleString()
        data.index(self.index)
        data.data(msg)

        self.writer.write(data)
        print(f"Sending {data.data()} : {data.index()}", flush=True)
        self.index = self.index + 1

    def wait_discovery(self):
        self._cvDiscovery.acquire()
        print("Writer is waiting discovery...", flush=True)
        self._cvDiscovery.wait_for(lambda: self._matched_reader != 0)
        self._cvDiscovery.release()
        print("Writer discovery finished...", flush=True)

    def run(self):
        self.wait_discovery()
        for _ in range(self.totalMsgs):
            time.sleep(1 / self.sendingRate)
            self.write(self.msg)
        self.delete()

    def delete(self):
        factory: fastdds.DomainParticipantFactory = fastdds.DomainParticipantFactory.get_instance()
        self.participant.delete_contained_entities()
        factory.delete_participant(self.participant)

    def create_participant(self, domain_id: int = 0) -> fastdds.DomainParticipant:
        self.context["domainID"] = domain_id

        factory: fastdds.DomainParticipantFactory = fastdds.DomainParticipantFactory.get_instance()
        self.participant_qos = fastdds.DomainParticipantQos()
        factory.get_default_participant_qos()
        return factory.create_participant(domain_id, self.participant_qos)

    def create_topic(self, name: str) -> fastdds.Topic:
        self.topic_data_type = SimpleString.SimpleStringPubSubType()
        self.topic_data_type.setName("SimpleStringType")
        self.context["topicTypeName"] = "SimpleStringType"

        self.type_support = fastdds.TypeSupport(self.topic_data_type)
        self.participant.register_type(self.type_support)

        self.topic_qos = fastdds.TopicQos()
        self.participant.get_default_topic_qos(self.topic_qos)
        self.apply_customized_topic_qos()
        return self.participant.create_topic(name, self.topic_data_type.getName(), self.topic_qos)

    def create_publisher(self) -> fastdds.Publisher:
        self.publisher_qos = fastdds.PublisherQos()
        self.participant.get_default_publisher_qos(self.publisher_qos)
        return self.participant.create_publisher(self.publisher_qos)

    def create_datawriter(self) -> fastdds.DataWriter:
        self.listener = WriterListener(self)
        self.writer_qos = fastdds.DataWriterQos()
        self.publisher.get_default_datawriter_qos(self.writer_qos)
        return self.publisher.create_datawriter(self.topic, self.writer_qos, self.listener)

    def apply_customized_topic_qos(self):
        if self.config is None:
            return

        # History
        history = fastdds.HistoryQosPolicy()
        if self.config.history.kind == "KEEP_ALL":
            history.kind = fastdds.KEEP_ALL_HISTORY_QOS
        elif self.config.history.kind == "KEEP_LAST":
            history.kind = fastdds.KEEP_LAST_HISTORY_QOS
        history.depth = self.config.history.depth

        self.context["history"] = {
            "kind": history.kind,
            "depth": history.depth
        }
        self.topic_qos.history(history)

        # Reliability
        reliability = fastdds.ReliabilityQosPolicy()
        if self.config.reliability.kind == "BEST_EFFORT":
            reliability.kind = fastdds.BEST_EFFORT_RELIABILITY_QOS
        elif self.config.reliability.kind == "RELIABLE":
            reliability.kind = fastdds.RELIABLE_RELIABILITY_QOS
        reliability.max_blocking_time = fastdds.Time_t(self.config.reliability.max_blocking_time, 0)

        self.context["reliability"] = {
            "kind": reliability.kind,
            "max_blocking_time": reliability.max_blocking_time.to_ns()
        }
        self.topic_qos.reliability(reliability)

        # ResourceLimits
        resourceLimits = fastdds.ResourceLimitsQosPolicy()
        resourceLimits.max_samples = self.config.resourceLimits.max_samples
        resourceLimits.max_instances = self.config.resourceLimits.max_instances
        resourceLimits.max_samples_per_instance = self.config.resourceLimits.max_samples_per_instance

        self.context["resourceLimits"] = {
            "max_samples": resourceLimits.max_samples,
            "max_instances": resourceLimits.max_instances,
            "max_samples_per_instance": resourceLimits.max_samples_per_instance
        }
        self.topic_qos.resource_limits(resourceLimits)


def dump_context_as_json(name: str, context: dict):
    with open(name + ".conf", "w") as f:
        json.dump(context, f, indent=2)


def main(args: list):
    print("Start publisher.", flush=True)

    configName = args.config
    totalMsgs = args.messages
    sendingRate = args.rate
    topicName = args.topic

    pwd = os.path.abspath(os.path.dirname(__file__))
    config_name = configName + ".yaml"
    config = YamlConfig.create_from_yaml(os.path.join(pwd, '../../configs/', config_name))

    context = {"configName": configName, "totalMsgs": totalMsgs, "sendingRate": sendingRate, "topicName": topicName}
    writer = Writer(
        config=config,
        totalMsgs=totalMsgs,
        sendingRate=sendingRate,
        topicName=topicName,
        context=context
    )
    dump_context_as_json(args.name, context)
    writer.run()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--name", "-n", help="Publisher's name")
    parser.add_argument("--config", "-c", help="specify config name", default="OMG-Def")
    parser.add_argument("--messages", "-m", help="specify total number of messages sent by a publisher", type=int, default=10000)
    parser.add_argument("--rate", "-r", help="specify publisher sending rate", type=int, default=100)
    parser.add_argument("--topic", "-t", help="specify topic name to which publisher publishes", default="SimpleStringTopic_1")

    args = parser.parse_args()
    main(args)
    exit()
