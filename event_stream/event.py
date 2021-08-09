"""event object"""

import datetime
import json
import time
import logging


# class Author(object):
#
#     url = None
#     original_tweet_url = None
#     original_tweet_author = None
#     alternative_id = None
#
#
# class Subject(object):
#     # tweet data eg
#     pid = None
#     url = None
#     title = None
#     issued = None
#     author = None
#     data = None
#
#
# class Object(object):
#
#     pid = None
#     url = None
#     method = None
#     verification = None
#     data = None


class Event(object):
    """
    a representation of an json event to use
    """

    data = {
        "obj_id": None,
        "occurred_at": None,
        "subj_id": None,
        "id": None,
        "subj": {
            "pid": None,
            "url": None,
            "title": None,
            "issued": None,
            "author": {
                "url": None
            },
            "original-tweet-url": None,
            "original-tweet-author": None,
            "alternative-id": None,
        },
        "source_id": None,
        "obj": {
            "pid": None,
        },
        "timestamp": None,
        "relation_type": None
    }

    def set(self, key, value):
        """this will set a value to a given key in the data of this event
        this is equal to data['key'] = value
        if setting nested properties use data directly

        Arguments:
            key: a valid key for the data of this event
            value: the value to store
        """
        self.data[key] = value

    def get(self, key):
        """this will get a value to a given key in the data of this event
        this is equal to data['key']
        if access to nested properties is needed use data directly

        Arguments:
            key: a valid key for the data of this event
        """
        return self.data[key]
        # t = self.data
        # # todo check if key exist
        # for key in keys:
        #     t = t[key]
        # return t

    def from_json(self, json_msg):
        """set this event from json_msg

        Arguments:
            json_msg: loaded json
        """
        self.data = json_msg
        # self.data = json.loads(json_msg)

    def get_json(self):
        """return this event as json
            equal to json.dumps(data)
        """
        return json.dumps(self.data)

    def __init__(self):
        # "timestamp":"2019-01-10T17:21:51Z",
        self.set('timestamp', '{0:%Y-%m-%dT%H:%M:%SZ}'.format(datetime.datetime.now()))

    def __str__(self):
        return 'Event ' + self.data['id'] + ' doi ' + self.data['obj_id']