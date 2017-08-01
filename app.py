import numpy as np
import csv
import itertools
import re
import json
import time
import requests
import random
import boto3
import urllib, cStringIO
import io

from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
from tweepy import API
from sklearn.metrics.pairwise import cosine_similarity

from tweet2vec.encode_one_tweet import encode_to_vector
from trump_data.preprocess_one_tweet import preprocess
import config     # contains all the keys

TWITTER_USER = "25073877"  # realDonaldTrump
# TWITTER_USER = "66575819"  # testing sandbox account
MUTE_FOR_TESTING = False;

SIMILARITY_THRESHOLD = 0.55
LOOKS_LIKE_WORDS = ['matches up with', 'looks like', 'is similar to', 'evokes', 'resembles', 'is mathematically similar to', 'is akin to', 'seems to match', 'might match', 'is reminiscent of', 'feels like']

## setup for Twitter via tweepy 
auth = OAuthHandler(config.consumer_key, config.consumer_secret)
auth.set_access_token(config.access_token, config.access_token_secret)
api = API(auth)

## setup for AWS via boto3
client = boto3.client('lambda', region_name='us-east-1')

def compareTweet(tweet):
    
    # preprocess the incoming tweet (using preprocess_one_tweet.py)
    print ("Preprocessing this tweet ...")
    processed_tweet = preprocess(tweet)

    # encode the tweet into a vector (using encode_one_tweet.py)
    # and then reshape it for the comparison
    print ("Encoding the tweet into a vector ...")
    single_item = encode_to_vector(processed_tweet).reshape(1,500)

    # find the similarities
    print ("Calculating similarities ...")
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
    
    interstitial_phrase = random.choice(LOOKS_LIKE_WORDS)
    
    # tweet the reply! Note that it has to start with @ to be a reply.
    compose_tweet = '@%s According to me, this tweet %s this one from %s: %s' % (new_tweet['user']['screen_name'], interstitial_phrase, historic_tweet_date, historic_tweet_url)
    
    if not MUTE_FOR_TESTING:
                
        # tweet it!
        my_tweet = api.update_status(status=compose_tweet, in_reply_to_status_id=int(new_tweet['id']))
        
        print ("Tweeted: %s" % my_tweet.text)
        
    # get the composite image of the two tweets
    print("Getting the composite image ...")
    image_data = getTweetImages(new_tweet_url, historic_tweet_url)
    
    if image_data:
    
        # set up the picture tweet
        picture_tweet = 'According to me, the top tweet %s the bottom one from %s.' % (interstitial_phrase, historic_tweet_date)
        
        if not MUTE_FOR_TESTING:
            
            # tweet the image tweet
            print("Posting tweet with composite image ...")
            api.update_with_media(filename="old_new_trump_tweets.jpg", status=picture_tweet, file=image_data)
            print("Tweeted image tweet: %s" % picture_tweet)
    
    # send a note to slack
    phrase_for_slack = "In response to the first tweet, I found the second one from %s. %s %s" % (historic_tweet_date, new_tweet_url, historic_tweet_url)
    slackThis(phrase_for_slack)
    print("End processing.")
    return True
    
def slackThis(phrase):
    
    payload = {
        "text": phrase,
        "icon_emoji": ":mantelpiece_clock:",
        "username": "Trump Of Yore Bot",
        "channel": "#bot-preschool"
    }

    if not MUTE_FOR_TESTING:
        # using http://docs.python-requests.org/en/master/user/quickstart/
        r = requests.post(config.SLACK_WEBHOOK_URL, json=payload)

        print "Slacked: %s" % phrase
        return True
    
def getTweetImages(new_url, old_url):
    
    # this function first sends the tweet URLs to a service built by quartz to 
    # take screenshots of images and tweets
    
    # set up a json payload for sending to aws lambda
    payload_setup = {}
    payload_setup['urls'] = [new_url, old_url]
    payload_json = json.dumps(payload_setup)
        #=> {"urls": ["url_for_top_tweet", "url_for_bottom_tweet"]}
    
    print("Getting the composite image URL from Quartz composite-bot service ...")
    
    # this triggers (invokes) the screenshot function    
    lambda_response = client.invoke(
        FunctionName='composite-bot',
        InvocationType='RequestResponse',
        Payload=payload_json
        )
        
    # the response contains an image URL
    lambda_response_json = json.load(lambda_response['Payload'])    
    image_url = lambda_response_json
    
    print("Got URL %s ..." % image_url)
    
    if image_url is not None:
    
        print("Downloading image from there ...")
        
        # now actually get the image
        image = cStringIO.StringIO(urllib.urlopen(image_url).read())

        return image
        
    else: 
        
        print("No URL, so can't get image ...")
        print("Skipping the image tweet ...")
        
        return false

# from tweepy ... this is what fires when a matching tweet is detected    
class StdOutListener(StreamListener):
    
    def on_data(self, data):
        new_tweet = json.loads(data)


        
        # check to see if it's actually trump tweeting
        # (the 'follow' stream also picks up replies to 'follow' tweets)
        if new_tweet['user']['id_str'] == TWITTER_USER:
            
            print("Detected tweet: %s" % new_tweet)
            
            # check to see if it's a retweet, which we're not processing
            if re.match(u'^RT ', new_tweet['text']) or new_tweet['is_quote_status'] or new_tweet['in_reply_to_status_id'] is not None:
                print("Looks like a retweet. Ending process.")
                return True
            
            else:                
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


