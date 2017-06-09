from __future__ import absolute_import, print_function

from tweepy import OAuthHandler
from tweepy import API
import datetime

import config     # contains all the keys

if __name__ == '__main__':
    auth = OAuthHandler(config.consumer_key, config.consumer_secret)
    auth.set_access_token(config.access_token, config.access_token_secret)
    api = API(auth)

    tweet = api.get_status('134001566503026688')
    print (tweet)
    print (tweet.created_at.strftime('%B %Y'))