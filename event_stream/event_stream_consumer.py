import json
import logging
import os
import threading
import time
from .event_stream_base import EventStreamBase
from kafka import KafkaConsumer
from kafka.vendor import six
from multiprocessing import Queue, Pool


def throughput_statistics(v, time_delta, no_throughput_counter=0):
    """show and setup in own thread repeatedly how many events are processed
        restarts if counter of no throughput is 10 (10 timed eltas with no data processed)
    Arguments:
        v: the value
        time_delta: time delta we wan't to monitor
        no_throughput_counter: counter of no throughput
    """
    logging.warning("THROUGHPUT: %d / %d" % (v.value, time_delta))

    if v.value == 0:
        no_throughput_counter += 1
    else:
        no_throughput_counter = 0
    if no_throughput_counter == 10:
        logging.warning('Exit Container because of no data throughput')
        os.system("pkill -9 python")  # allows killing of multiprocessing programs

    with v.get_lock():
        v.value = 0

    threading.Timer(time_delta, throughput_statistics, args=[v, time_delta, no_throughput_counter]).start()


class EventStreamConsumer(EventStreamBase):
    """
    a base consumer class for consuming from kafka,
    uses multiprocessing to share workload
    """
    relation_type = ''
    state = "unlinked"
    topics = False
    consumer = False

    task_queue = Queue()
    process_number = 4
    log = "EventStreamConsumer " + str(id) + " "

    @staticmethod
    def start(i=0):
        """start the consumer
        """
        esc = EventStreamConsumer(i)
        logging.debug(EventStreamBase.log + 'Start %s' % str(i))
        esc.consume()

    def create_consumer(self):
        """create the consumer, connect to kafka
        """
        logging.debug(self.log + "rt: %s" % self.relation_type)

        if self.state == 'all':
            self.topics = self.build_topic_list()

        if isinstance(self.state, six.string_types):
            self.state = [self.state]

        if isinstance(self.relation_type, six.string_types):
            self.relation_type = [self.relation_type]

        if not self.topics:
            self.topics = list()
            for state in self.state:
                for relation_type in self.relation_type:
                    self.topics.append(self.get_topic_name(state=state, relation_type=relation_type))

        logging.debug(self.log + "get consumer for topic: %s" % self.topics)
        self.consumer = KafkaConsumer(group_id=self.group_id,
                                      bootstrap_servers=self.bootstrap_servers, api_version=self.api_version,
                                      consumer_timeout_ms=self.consumer_timeout_ms)

        for topic in self.topics:
            logging.debug(self.log + "consumer subscribe: %s" % topic)
            self.consumer.subscribe(topic)

        logging.debug(self.log + "consumer subscribed to: %s" % self.consumer.topics())

    def consume(self):
        """consume messages and add them to a queue to share with the worker processes

        """
        logging.warning(self.log + "start consume")
        self.running = True

        if not self.consumer:
            self.create_consumer()

        pool = Pool(self.process_number, self.worker, (self.task_queue,))

        while self.running:
            try:
                for msg in self.consumer:
                    logging.debug(self.log + 'msg in consumer ')
                    if self.counter:
                        with self.counter.get_lock():
                            self.counter.value += 1
                    self.task_queue.put(json.loads(msg.value.decode('utf-8')))

            except Exception as exc:
                self.consumer.close()
                logging.error(self.log + 'stream Consumer generated an exception: %s' % exc)
                logging.warning(self.log + "Consumer closed")
                break

        # keep alive
        if self.running:
            return self.consume()

        pool.close()
        logging.warning(self.log + "Consumer shutdown")

    def worker(self, queue):
        """worker function to get items from the queue

        Arguments:
            queue: the queue
        """
        logging.debug(self.log + "working %s" % os.getpid())
        while self.running:
            time.sleep(0.005)
            try:
                item = queue.get()
            except queue.Empty:
                time.sleep(0.1)
                pass
            else:
                logging.debug(self.log + "got %s item" % os.getpid())
                self.on_message(item)

    def on_message(self, json_msg):
        """the on message function to be implemented in own classes

        Arguments:
            json_msg: the message to do stuff with
        """
        logging.debug(self.log + "on message")

    def stop(self):
        """stop the consumer
        """
        self.running = False
        logging.debug(self.log + 'stop running consumer')


if __name__ == '__main__':
    EventStreamConsumer.start(0)
