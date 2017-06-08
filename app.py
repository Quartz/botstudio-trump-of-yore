import numpy as np
import csv
import itertools
import re
from sklearn.metrics.pairwise import cosine_similarity

from tweet2vec.encode_one_tweet import encode
from trump_data.preprocess_one_tweet import preprocess

print ("Loading tweet archive ...")
tweet_file = 'trump_data/pre_prez_archive.txt'
with open(tweet_file, 'r') as f:
    tweet_list = f.readlines()

print ("Loading vectors for tweets in archive ...")
data = np.load('trump_data/result/embeddings.npy')

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

    if (top_hit_score > 0.60):

        # split on the tab and take the second half [1]
        status_number = tweet_list[top_hit].split('\t')[1]

        tweet_url = "https://twitter.com/realDonaldTrump/status/%s" % status_number
        print (tweet_url)
        return tweet_url
    
    else:
        
        print ("No tweet. Similary score too low.")

tweet = 'China just agreed that the U.S. will be allowed to sell beef, and other major products, into China once again. This is REAL news!'

compareTweet(tweet)

