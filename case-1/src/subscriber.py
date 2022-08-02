import os
import fastdds
import SimpleString
import signal
import sys

from config import YamlConfig


class ReaderListener(fastdds.DataReaderListener):
    def __init__(self, reader):
        self._reader = reader
        super().__init__()

    def on_subscription_matched(self, reader, info):
        if 0 < info.current_count_change:
            print(f"Subscriber matched publisher {info.last_publication_handle}")
        else:
            print(f"Subscriber unmatched publisher {info.last_publication_handle}")

    def on_data_available(self, reader: fastdds.DataReader):
        info = fastdds.SampleInfo()
        data = SimpleString.SimpleString()
        reader.take_next_sample(data, info)

        print(f"Received {data.data()}: {data.index()}")
        self._reader.samples_received += 1

        # Terminates the program once received enough samples
        print(self._reader.samples_received, self._reader.totalMsgs)
        if self._reader.samples_received >= self._reader.totalMsgs:
            os.kill(os.getpid(), signal.SIGINT)


class Reader:
    def __init__(
            self,
            config: YamlConfig,
            totalMsgs: int = 10,
            topicName: str = "SimpleStringType") -> None:
        self.config = config
        self.totalMsgs = totalMsgs
        self.topicName = topicName

        print(os.getpid())
        self.samples_received = 0

        self.participant = self.create_participant()
        self.topic = self.create_topic(name=self.topicName)
        self.subscriber = self.create_subscriber()
        self.reader = self.create_datareader()

    def run(self):
        signal.signal(signal.SIGINT, self.signal_handler)
        print("Press Ctrl+C to stop")
        signal.pause()
        self.delete()

    def delete(self):
        factory: fastdds.DomainParticipantFactory = fastdds.DomainParticipantFactory.get_instance()
        self.participant.delete_contained_entities()
        factory.delete_participant(self.participant)

    def signal_handler(self, sig, frame):
        print("Interrupted!")

    def create_participant(self, domain_id: int = 0) -> fastdds.DomainParticipant:
        factory: fastdds.DomainParticipantFactory = fastdds.DomainParticipantFactory.get_instance()
        self.participant_qos = fastdds.DomainParticipantQos()
        factory.get_default_participant_qos(self.participant_qos)
        return factory.create_participant(domain_id, self.participant_qos)

    def create_topic(self, name: str) -> fastdds.Topic:
        self.topic_data_type = SimpleString.SimpleStringPubSubType()
        self.topic_data_type.setName("SimpleStringType")
        self.type_support = fastdds.TypeSupport(self.topic_data_type)
        self.participant.register_type(self.type_support)

        self.topic_qos = fastdds.TopicQos()
        self.participant.get_default_topic_qos(self.topic_qos)
        return self.participant.create_topic(name, self.topic_data_type.getName(), self.topic_qos)

    def create_subscriber(self) -> fastdds.Subscriber:
        self.subscriber_qos = fastdds.SubscriberQos()
        self.participant.get_default_subscriber_qos(self.subscriber_qos)
        return self.participant.create_subscriber(self.subscriber_qos)

    def create_datareader(self) -> fastdds.DataReader:
        self.listener = ReaderListener(self)
        self.reader_qos = fastdds.DataReaderQos()
        self.subscriber.get_default_datareader_qos(self.reader_qos)
        return self.subscriber.create_datareader(self.topic, self.reader_qos, self.listener)


def main(argv: list):
    print("Creating Subscriber.")

    configName = argv[0]
    totalMsgs = int(argv[1])
    topicName = argv[2]

    pwd = os.path.abspath(os.path.dirname(__file__))
    config_name = configName + ".yaml"
    config = YamlConfig.create_from_yaml(os.path.join(pwd, '../../configs/', config_name))

    reader = Reader(
        config=config,
        totalMsgs=totalMsgs,
        topicName=topicName
    )
    reader.run()


if __name__ == '__main__':
    # TODO: refactor to argparse
    if 4 != len(sys.argv):
        print("Incorrect number of arguments")
        exit()
    main(sys.argv[1:])
    exit()
