## based on tweet2vec/encode_char.py

import os
import numpy as np
import lasagne
import theano
import theano.tensor as T
import sys
import batch_char as batch
import cPickle as pkl
import io
import re

from t2v import tweet2vec, init_params, load_params
from settings_char import N_BATCH, MAX_LENGTH, MAX_CLASSES

def invert(d):
    out = {}
    for k,v in d.iteritems():
        out[v] = k
    return out

def classify(tweet, t_mask, params, n_classes, n_chars):
    # tweet embedding
    emb_layer = tweet2vec(tweet, t_mask, params, n_chars)
    # Dense layer for classes
    l_dense = lasagne.layers.DenseLayer(emb_layer, n_classes, W=params['W_cl'], b=params['b_cl'], nonlinearity=lasagne.nonlinearities.softmax)

    return lasagne.layers.get_output(l_dense), lasagne.layers.get_output(emb_layer)

def encode_to_vector(incoming_tweet_text):

    model_path = "tweet2vec/best_model"

    print("Preparing Data...")
    # Test data
    Xt = []
    Xc = incoming_tweet_text.encode('utf-8').rstrip('\n')  # change unicode to utf-8, as was the file
    print (Xc)
    Xt.append(Xc[:MAX_LENGTH])

    # Model
    print("Loading model params...")
    params = load_params('%s/best_model.npz' % model_path)

    print("Loading dictionaries...")
    with open('%s/dict.pkl' % model_path, 'rb') as f:
        chardict = pkl.load(f)
    with open('%s/label_dict.pkl' % model_path, 'rb') as f:
        labeldict = pkl.load(f)
    n_char = len(chardict.keys()) + 1
    n_classes = min(len(labeldict.keys()) + 1, MAX_CLASSES)
    inverse_labeldict = invert(labeldict)

    print("Building network...")
    # Tweet variables
    tweet = T.itensor3()
    t_mask = T.fmatrix()

    # network for prediction
    predictions, embeddings = classify(tweet, t_mask, params, n_classes, n_char)

    # Theano function
    print("Compiling theano functions...")
    # JK/QUARTZ Disabling the prediction function, because we just need the vectoring
    # predict = theano.function([tweet,t_mask],predictions)
    encode = theano.function([tweet,t_mask],embeddings)

    # Test
    print("Encoding...")
    # JK/QUARTZ Disabling the prediction lines, because we just need the vectoring
    # out_pred = []
    out_emb = []
    numbatches = len(Xt)/N_BATCH + 1
    for i in range(numbatches):
        xr = Xt[N_BATCH*i:N_BATCH*(i+1)]
        x, x_m = batch.prepare_data(xr, chardict, n_chars=n_char)
        # JK/QUARTZ Disabling the prediction function, because we just need the vectoring
        # p = predict(x,x_m)
        e = encode(x,x_m)
        # JK/QUARTZ Disabling the prediction lines, because we just need the vectoring
        # ranks = np.argsort(p)[:,::-1]

        for idx, item in enumerate(xr):
            # JK/QUARTZ Disabling the prediction lines, because we just need the vectoring
            # out_pred.append(' '.join([inverse_labeldict[r] if r in inverse_labeldict else 'UNK' for r in ranks[idx,:5]]))
            out_emb.append(e[idx,:])

    # Return vector as numpy array
    print("Returning...")
    return np.asarray(out_emb)

