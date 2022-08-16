import argparse
import os
import fastdds
import SimpleString
import signal
import threading
import time

from config import YamlConfig


class ReaderListener(fastdds.DataReaderListener):
    def __init__(self, reader):
        self._reader = reader
        super().__init__()

    def on_subscription_matched(self, reader, info):
        if 0 < info.current_count_change:
            print(f"Subscriber matched publisher {info.last_publication_handle}", flush=True)
        else:
            print(f"Subscriber unmatched publisher {info.last_publication_handle}", flush=True)

    def on_data_available(self, reader: fastdds.DataReader):
        info = fastdds.SampleInfo()
        data = SimpleString.SimpleString()
        reader.take_next_sample(data, info)

        print(f"Received {data.data()}: {data.index()}/{self._reader.totalMsgs}", flush=True)
        self._reader.samples_received += 1

        ###
        # Terminates either on enough samples received or idling too long
        ###

        # Idling too long
        if 1 == self._reader.samples_received:
            self.monitor(os.getpid())

        # Received enough samples
        if self._reader.samples_received >= self._reader.totalMsgs:
            print("Killed on received enough samples", flush=True)
            os.kill(os.getpid(), signal.SIGINT)

    def monitor(self, ppid: int, timeout: int = 10):
        def monitor_job(index):
            old_index = -1
            while True:
                if index() == old_index:
                    break
                old_index = index()
                time.sleep(timeout)
            print("Killed by monitor", flush=True)
            os.kill(ppid, signal.SIGINT)

        monitor_thread = threading.Thread(target=monitor_job, args=(lambda: self._reader.samples_received, ))
        monitor_thread.start()


class Reader:
    def __init__(
            self,
            config: YamlConfig,
            totalMsgs: int = 10,
            topicName: str = "SimpleStringType") -> None:
        self.config = config
        self.totalMsgs = totalMsgs
        self.topicName = topicName

        print(os.getpid(), flush=True)
        self.samples_received = 0

        self.participant = self.create_participant()
        self.topic = self.create_topic(name=self.topicName)
        self.subscriber = self.create_subscriber()
        self.reader = self.create_datareader()

    def run(self):
        signal.signal(signal.SIGINT, self.signal_handler)
        print("Press Ctrl+C to stop", flush=True)
        signal.pause()
        self.delete()

    def delete(self):
        factory: fastdds.DomainParticipantFactory = fastdds.DomainParticipantFactory.get_instance()
        self.participant.delete_contained_entities()
        factory.delete_participant(self.participant)

    def signal_handler(self, sig, frame):
        print("Interrupted!", flush=True)

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


def main(args: list):
    print("Creating Subscriber.", flush=True)

    configName = args.config
    totalMsgs = args.messages
    topicName = args.topic

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
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", "-c", help="specify config name", default="OMG-Def")
    parser.add_argument("--messages", "-m", help="specify total number of messages sent by a publisher", type=int, default=10000)
    parser.add_argument("--topic", "-t", help="specify topic name to which publisher publishes", default="SimpleStringTopic_1")

    args = parser.parse_args()
    main(args)
    exit()
