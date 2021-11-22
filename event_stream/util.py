import time
import logging
import re
import requests
from requests import Session
from urllib3.exceptions import ReadTimeoutError, SSLError, NewConnectionError


class Util:

    @staticmethod
    def normalize(string):
        """normalize a string

        Arguments:
            string: the string to be normalized
        """
        return (re.sub('[^a-zA-Z ]+', '', string)).casefold().strip()

    @staticmethod
    def get_response(url, s, r=0):
        """get a response from a given url using a given session s, a session can be used for headers,
        this function is cached up to 100 elements

            Arguments:
                url: the url to get
                s: the session to use
        """
        try:
            url = url.replace('arxiv.org', 'export.arxiv.org')  # arxiv wants this url to be used by machines
            result = s.get(url, stream=False, timeout=5)
        except (ConnectionRefusedError, SSLError, ReadTimeoutError, requests.exceptions.TooManyRedirects,
                requests.exceptions.ConnectionError,
                requests.exceptions.ReadTimeout, NewConnectionError, requests.exceptions.SSLError, ConnectionError):
            logging.warning('Percolator error, reset session')
            s = Session()
            # get the response for the provided url
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.104 Safari/537.36'
            }
            s.headers.update(headers)
            if r < 3:
                logging.warning('retry in ' + str(pow(2, r)) + 's')
                time.sleep(pow(2, r))
                Util.get_response(url, s, r + 1)
            else:
                return None
        else:
            return result
        return None
