# Trump Echo notes

## Research & Resources

Interesting answers to Quora question here: https://www.quora.com/What-are-some-NLP-techniques-that-can-be-used-to-find-similar-Twitter-messages

That referenced this paper: 
https://arxiv.org/pdf/1605.03481v2.pdf

Which has this code:
https://github.com/bdhingra/tweet2vec

Going to try to use that code.

Using a new anaconda environment I'm calling `vectoring`.

    ```
    conda create --name vectoring python=2
    source activate vectoring
    conda install theano lasagne numpy
    pip install tweepy
    ```

Ran into a dependency error around `downsample`, which is deprecated but still used by the old Lasagne version that Theano installs. Soooo did this:

    ```
    pip install --upgrade https://github.com/Theano/Theano/archive/master.zip
    pip install --upgrade https://github.com/Lasagne/Lasagne/archive/master.zip
    ```

See: https://lasagne.readthedocs.io/en/latest/user/installation.html for more info on this.

For the cosine distance:

    ```
    conda install scikit-learn
    ```


## Playing with the vector

Ran `./tweet2vec_encoder.sh` to generate test results
End up in `result/` folder

Copied `result/` to this repo's `making_vectors` directory 

Had to add new `jupyter` to the `vectoring` environment:

    ` conda install jupyter`
    
So I could use Python 2.

See the python notebook in `making_vectors` ... where I load in the `embeddings.npy` file using numpy.

This looks promising:
https://stackoverflow.com/questions/17627219/whats-the-fastest-way-in-python-to-calculate-cosine-similarity-given-sparse-mat


Also took the one-to-many comparison code from here: 
https://stackoverflow.com/questions/12118720/python-tf-idf-cosine-to-find-document-similarity
Particularly this part: 
    Hence to find the top 5 related documents, we can use argsort and some negative array slicing (most related documents have highest cosine similarity values, hence at the end of the sorted indices array) ...
    
Got this working.
    
Commented out some prediction lines in `encode_char.py` since we're not going to use the hashtag prediction -- just want the vector encoding of tweets.
    
## Prepping Trump Tweets

Inside trump_data, modified the `preprocess.py` from the original tweet2vec:

- added the twitter str_id to each row, separated by a tab character
- made the tokenizer handle periods better
- changed the 'write' mode to 'append' mode for the output file

Then, from `trump_data/` ran:

```
python preprocess.py 2009.json pre_prez_archive.txt
python preprocess.py 2010.json pre_prez_archive.txt
python preprocess.py 2011.json pre_prez_archive.txt
python preprocess.py 2012.json pre_prez_archive.txt
python preprocess.py 2013.json pre_prez_archive.txt
python preprocess.py 2014.json pre_prez_archive.txt
python preprocess.py 2015.json pre_prez_archive.txt
python preprocess.py 2016.json pre_prez_archive.txt
python preprocess.py 2017_pre0120.json pre_prez_archive.txt
```

Now I'm going to use a modified version of tweet2vec which removes the prediction functions since we're not doing any machine learning, just turning the tweets into vectors. It also accounts for the tab characters we've added (along with the twitter id_str values) in the data.

Repo for Quartz version is here: https://github.com/Quartz/tweet2vec

Over there, ran the modified `encode_char.py` which takes the following parameters:

`python encode_char.py [datafile] [modelpath] [resultpath]`

I'm just going to use the default model path to keep it happy. `best_model/`

So, from `tweet2vec/tweet2vec`:

```
source activate vectoring
python encode_char.py ../../botstudio-trump-echo/trump_data/pre_prez_archive.txt best_model/ ../../botstudio-trump-echo/trump_data/result/
```

And I got a 50 MB numpy file!

Heading over to the `vector_tinkering_all` notebook ...

## Tweeting with Tweepy

TRUMP_USER_ID = "25073877"
POTUS_USER_ID = "822215679726100480"





