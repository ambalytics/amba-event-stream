import json
import logging
import os

from .event_stream_base import EventStreamBase

from kafka import KafkaConsumer, KafkaProducer
from kafka.vendor import six

from multiprocessing import Process, Queue, current_process, freeze_support, Pool


# idee
# import eventstream reader
# class inherince
# override for each message method, use var as string?
#     -> goal of eventstream
#
# o1 here is function, do everything else (mulitple threads etc)
#
# o2 here is a class you can ran as you wish
#
# o3 (1+2) eventstream class has functions to do multithreads with the class
#
# consumer
# producer
# consumer producer
#
# -> event stream problem (handle multiple or just one each?)
# eventstreap processor process producer1, consumer2,

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

    def create_consumer(self):
        """create the consumer, connect to kafka
        """
        logging.warning(self.log + "rt: %s" % self.relation_type)

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

        # self.topic_name = 'tweets'
        logging.warning(self.log + "get consumer for topic: %s" % self.topics)
        # consumer.topics()
        self.consumer = KafkaConsumer(group_id=self.group_id,
                                      bootstrap_servers=self.bootstrap_servers, api_version=self.api_version,
                                      consumer_timeout_ms=self.consumer_timeout_ms)

        for topic in self.topics:
            logging.warning(self.log + "consumer subscribe: %s" % topic)
            self.consumer.subscribe(topic)

        logging.warning(self.log + "consumer subscribed to: %s" % self.consumer.topics())

    def consume(self):
        """consume messages and add them to a queue to share with the worker processes

        """
        logging.warning(self.log + "start consume")
        self.running = True

        if not self.consumer:
            self.create_consumer()

        # Start worker processes
        # for i in range(self.process_number):
        #     Process(target=self.on_message, args=(self.task_queue, )).start()
        pool = Pool(self.process_number, self.worker, (self.task_queue,))

        while self.running:
            try:
                for msg in self.consumer:
                    logging.debug(self.log + 'msg in consumer ')
                    with self.counter.get_lock():
                        self.counter.value += 1
                    # logging.warning('msg in consumer %s' % msg.value)
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
        while True:
            item = queue.get(True)
            logging.debug(self.log + "got %s item" % os.getpid())
            self.on_message(item)

    def on_message(self, json_msg):
        """the on message function to be implemented in own classes

        Arguments:
            json_msg: the message to do stuff with
        """
        logging.warning(self.log + "on message")

    def stop(self):
        """stop the consumer
        """
        self.running = False
        logging.warning(self.log + 'stop running consumer')


if __name__ == '__main__':
    e = EventStreamConsumer(1)
    e.consume()
