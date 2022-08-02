import fastdds
import os
import SimpleString
import sys
import time

from threading import Condition
from config import YamlConfig


class WriterListener(fastdds.DataWriterListener):
    def __init__(self, writer):
        self._writer = writer    # class Writer defined below
        super().__init__()

    def on_publication_matched(self, writer, info):
        if 0 < info.current_count_change:
            print("Publisher matched subscriber {}".format(info.last_subscription_handle))
            self._writer._cvDiscovery.acquire()
            self._writer._matched_reader += 1
            self._writer._cvDiscovery.notify()
            self._writer._cvDiscovery.release()
        else:
            print("Publisher unmatched subscriber {}".format(info.last_subscription_handle))
            self._writer._cvDiscovery.acquire()
            self._writer._matched_reader -= 1
            self._writer._cvDiscovery.notify()
            self._writer._cvDiscovery.release()


class Writer:
    def __init__(
            self,
            config: YamlConfig = None,
            totalMsgs: int = 10,
            sendingRate: int = 10,
            topicName: str = "SimpleStringTopic") -> None:
        self.config = config
        self.totalMsgs = totalMsgs
        self.sendingRate = sendingRate
        self.topicName = topicName

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
        print(f"Sending {data.data()} : {data.index()}")
        self.index = self.index + 1

    def wait_discovery(self):
        self._cvDiscovery.acquire()
        print("Writer is waiting discovery...")
        self._cvDiscovery.wait_for(lambda: self._matched_reader != 0)
        self._cvDiscovery.release()
        print("Writer discovery finished...")

    def run(self):
        self.wait_discovery()
        for _ in range(self.totalMsgs):
            time.sleep(1 / self.sendingRate)
            self.write()
        self.delete()

    def delete(self):
        factory: fastdds.DomainParticipantFactory = fastdds.DomainParticipantFactory.get_instance()
        self.participant.delete_contained_entities()
        factory.delete_participant(self.participant)

    def create_participant(self, domain_id: int = 0) -> fastdds.DomainParticipant:
        factory: fastdds.DomainParticipantFactory = fastdds.DomainParticipantFactory.get_instance()
        self.participant_qos = fastdds.DomainParticipantQos()
        factory.get_default_participant_qos()
        return factory.create_participant(domain_id, self.participant_qos)

    def create_topic(self, name: str) -> fastdds.Topic:
        self.topic_data_type = SimpleString.SimpleStringPubSubType()
        self.topic_data_type.setName("SimpleStringType")
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
        self.topic_qos.history(history)

        # Reliability
        reliability = fastdds.ReliabilityQosPolicy()
        if self.config.reliability.kind == "BEST_EFFORT":
            reliability.kind = fastdds.BEST_EFFORT_RELIABILITY_QOS
        elif self.config.reliability.kind == "RELIABLE":
            reliability.kind = fastdds.RELIABLE_RELIABILITY_QOS
        reliability.max_blocking_time = fastdds.Time_t(self.config.reliability.max_blocking_time, 0)
        self.topic_qos.reliability(reliability)

        # ResourceLimits
        resourceLimits = fastdds.ResourceLimitsQosPolicy()
        resourceLimits.max_samples = self.config.resourceLimits.max_samples
        resourceLimits.max_instances = self.config.resourceLimits.max_instances
        resourceLimits.max_samples_per_instance = self.config.resourceLimits.max_samples_per_instance
        self.topic_qos.resource_limits(resourceLimits)


def main(argv: list):
    print("Start publisher.")

    configName = argv[0]
    totalMsgs = int(argv[1])
    sendingRate = int(argv[2])
    topicName = argv[3]

    pwd = os.path.abspath(os.path.dirname(__file__))
    config_name = configName + ".yaml"
    config = YamlConfig.create_from_yaml(os.path.join(pwd, '../../configs/', config_name))

    writer = Writer(
        config=config,
        totalMsgs=totalMsgs,
        sendingRate=sendingRate,
        topicName=topicName
    )
    writer.run()


if __name__ == '__main__':
    # TODO: refactor to argparse
    if 5 != len(sys.argv):
        print("Incorrect number of arguments")
        exit()
    main(sys.argv[1:])
    exit()
