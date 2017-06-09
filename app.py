import numpy as np
import csv
import itertools
import re
import json
import time
import requests

from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
from tweepy import API
from sklearn.metrics.pairwise import cosine_similarity

from tweet2vec.encode_one_tweet import encode
from trump_data.preprocess_one_tweet import preprocess
import config     # contains all the keys

# TWITTER_USER = "66575819"  # testing account
TWITTER_USER = "25073877"
SIMILARITY_THRESHOLD = 0.55

auth = OAuthHandler(config.consumer_key, config.consumer_secret)
auth.set_access_token(config.access_token, config.access_token_secret)
api = API(auth)

def compareTweet(tweet):

    # encode the tweet into a vector
    single_item = encode(tweet).reshape(1,500)

    # find the similarities
    similarities = cosine_similarity(single_item, data, dense_output=False)

    # sort them into the top 5
    related_docs_indices = similarities[0].argsort()[:-5:-1]
    print ("Similar documnents: %s" % related_docs_indices)

    print ("Document scores: %s" % similarities[0, related_docs_indices])

    top_hit = related_docs_indices[0]
    print ("Top hit index: %s" % top_hit)
    
    top_hit_score = similarities[0, top_hit]
    print ("Top hit score: %s" % top_hit_score)
        
    print ("Top hit tweet: %s" % tweet_list[top_hit])

    if (top_hit_score > SIMILARITY_THRESHOLD):

        # split on the tab and take the second half [1]
        status_number = tweet_list[top_hit].split('\t')[1].strip('\n')
        return status_number
    
    else:
        
        print ("No tweet. Similary score too low.")
        return False
        
def tweetThis(new_tweet, historic_tweet_id):
    
    new_tweet_url = "https://twitter.com/%s/status/%s" % (new_tweet['user']['screen_name'], new_tweet['id_str'])
    historic_tweet_url = "https://twitter.com/%s/status/%s" % ('realDonaldTrump', historic_tweet_id)
    
    # get the full tweet from the twitter api    
    historic_tweet = api.get_status(historic_tweet_id)
    
    # calculate the historic tweet's month and year.
    historic_tweet_date = historic_tweet.created_at.strftime('%B %Y')
    
    # tweet the reply! Note that it has to start with @ to be a reply.
    my_tweet = api.update_status(status='@%s To my bot brain, that looks similar to this tweet from %s: %s' % (new_tweet['user']['screen_name'], historic_tweet_date, historic_tweet_url), in_reply_to_status_id=int(new_tweet['id']))
    
    print ("Tweeted: %s" % my_tweet.text)
    
    # send a note to slack
    phrase_for_slack = "In response to the first tweet, I found the second one from %s. %s %s" % (historic_tweet_date, new_tweet_url, historic_tweet_url)
    slackThis(phrase_for_slack)
    return True
    
def slackThis(phrase):
    
    payload = {
        "text": phrase,
        "icon_emoji": ":mantelpiece_clock:",
        "username": "Trump Of Yore Bot",
        "channel": "#bot-preschool"
    }

    # using http://docs.python-requests.org/en/master/user/quickstart/
    r = requests.post(config.SLACK_WEBHOOK_URL, json=payload)

    print "Slacked: %s" % phrase
    return True
    
    
class StdOutListener(StreamListener):
    """ A listener handles tweets that are received from the stream.
    This is a basic listener that just prints received tweets to stdout.

    """
    def on_data(self, data):
        new_tweet = json.loads(data)
        
        # check to see if it's actually trump tweeting
        # (the 'follow' stream also picks up replies to 'follow' tweets)
        if new_tweet['user']['id_str'] == TWITTER_USER:
            
            print("Detected tweet: %s" % new_tweet)
            
            # go see if the text matches any previous tweet
            historic_tweet_url = compareTweet(new_tweet['text'])
            
            if historic_tweet_url:
                tweetThis(new_tweet, historic_tweet_url)
            
            return True

    def on_error(self, status):
        print("ERROR FROM TWITTER: %s" % status)
        slackThis("Got an error from Twitter (%s). Killing the stream, and we're down for now. cc @johnkeefe" % status)
        return False   # got an error, kill the stream
        
        
if __name__ == '__main__':

    print ("Loading tweet archive ...")
    tweet_file = 'trump_data/pre_prez_archive.txt'
    with open(tweet_file, 'r') as f:
        tweet_list = f.readlines()

    print ("Loading vectors for tweets in archive ...")
    data = np.load('trump_data/result/embeddings.npy')

    # Set up Tweet listener
    print ("Listening for tweets ...")
    l = StdOutListener()
    stream = Stream(auth, l)
    stream.filter(follow=[TWITTER_USER])


