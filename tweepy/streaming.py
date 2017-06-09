from __future__ import absolute_import, print_function

from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream

import config     # contains all the keys
import json

class StdOutListener(StreamListener):
    """ A listener handles tweets that are received from the stream.
    This is a basic listener that just prints received tweets to stdout.

    """
    def on_data(self, data):
        new_tweet = json.loads(data)
        if new_tweet['user']['id_str'] == "66575819":
            print(new_tweet)
            return True

    def on_error(self, status):
        print(status)
        return False   # got an error, kill the stream

if __name__ == '__main__':
    l = StdOutListener()
    auth = OAuthHandler(config.consumer_key, config.consumer_secret)
    auth.set_access_token(config.access_token, config.access_token_secret)

    stream = Stream(auth, l)
    stream.filter(follow=['66575819'])