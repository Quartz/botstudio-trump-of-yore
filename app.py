import numpy as np
import csv
import itertools
import re
import json
import time
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
from tweepy import API
from sklearn.metrics.pairwise import cosine_similarity

from tweet2vec.encode_one_tweet import encode
from trump_data.preprocess_one_tweet import preprocess
import config     # contains all the keys

TWITTER_USER = "66575819"
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
    print ("Similar documnents:")
    print (related_docs_indices)

    print ("Scores:")
    print similarities[0, related_docs_indices]

    top_hit = related_docs_indices[0]
    print ("top hit:")
    print (top_hit)
    
    top_hit_score = similarities[0, top_hit]
    print ("top hit score:")
    print (top_hit_score)
        
    print ("Top hit tweet:")
    print (tweet_list[top_hit])

    if (top_hit_score > 0.50):

        # split on the tab and take the second half [1]
        status_number = tweet_list[top_hit].split('\t')[1]

        print (status_number)
        return status_number
    
    else:
        
        print ("No tweet. Similary score too low.")
        return False
        
def tweetThis(new_tweet, historic_tweet_id):
    
    new_tweet_url = "https://twitter.com/%s/status/%s" % (new_tweet['user']['screen_name'], new_tweet['id_str'])
    historic_tweet_url = "https://twitter.com/%s/status/%s" % ('realDonaldTrump', historic_tweet_id)
    
    historic_tweet = api.get_status(historic_tweet_id)
    historic_tweet_date = historic_tweet.created_at.strftime('%B %Y')
    
    api.update_status(status='1/2 This new tweet by @realDonaldTrump ... %s' % new_tweet_url)
    time.sleep(1)
    api.update_status(status='2/2 ... looks, to me, like this tweet from %s: %s' % (historic_tweet_date, historic_tweet_url))
    

class StdOutListener(StreamListener):
    """ A listener handles tweets that are received from the stream.
    This is a basic listener that just prints received tweets to stdout.

    """
    def on_data(self, data):
        new_tweet = json.loads(data)
        
        # check to see if it's actually trump tweeting
        # (the 'follow' stream also picks up replies to 'follow' tweets)
        if new_tweet['user']['id_str'] == TWITTER_USER:
            
            print(new_tweet)
            
            # go see if the text matches any previous tweet
            historic_tweet_url = compareTweet(new_tweet['text'])
            
            if historic_tweet_url:
                tweetThis(new_tweet, historic_tweet_url)
            
            return True

    def on_error(self, status):
        print(status)
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


