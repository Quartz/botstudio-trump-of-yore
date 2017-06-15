# Trump Echo notes

Contemporaneous  

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
    pip install boto3
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

## Getting Tweet Images

So working on how to *display* both old and new tweets. Couldn't get the user experience to be very good (see images in notes_images).

Then in talking with Chris Zarate, we had the idea of getting screenshots of both tweets and combining them into a single image. He already had been working on a screen-shot system running on AWS Lambda, and modified it to accept two tweet urls. Then it returns a url to the combined image.

To do this, I need to connect ot the Lambda function in the AWS system. So installed [boto3](https://boto3.readthedocs.io/en/latest/guide/quickstart.html#installation), the AWS SDK for python.

    `pip install boto3`
    
Aaaand ... we decided not to do this. But here's some code on how I was going to do it:

```
    # set up a json payload for sending to aws lambda
    payload_setup = {}
    payload_setup['urls'] = [new_tweet_url, historic_tweet_url]
    payload_json = json.dumps(payload_setup)
        #=> {"urls": ["url_for_top_tweet", "url_for_bottom_tweet"]}
```

## Just going to reply to Trump's tweets

## Installing on EC2

Had to install conda. See: https://www.continuum.io/downloads#linux

```
    wget "https://repo.continuum.io/archive/Anaconda2-4.4.0-Linux-x86_64.sh"
    bash Anaconda2-4.4.0-Linux-x86_64.sh
```

(Answer 'yes' to adding the path to `.bashrc`, which is not the default)

Did all the installs above.

Added my `config.py` file to the top level of the repo.

To avoid this error/warning when running the app ...

`WARNING (theano.configdefaults): g++ not detected ! Theano will be unable to execute optimized C-implementations (for both CPU and GPU) and will default to Python implementations. Performance will be severely degraded. To remove this warning, set Theano flags cxx to an empty string.`

... I added a file at the user home level called `.theanorc` containing this:

```
[global]
floatX = float32
device = cpu
cxx = ""
```




I'm going to use `forever` to run my python script, just like I do with node. But using `-c` to run a command.
- `-l` is the log file
-  `-m` is the max number of retries (don't want to upset Twitter)
- `-c` is the command

Note that I'm doing this command after `source activate vectoring` to start my conda environment.


```
cd botstudio-trump-of-yore
source activate vectoring
forever start -a -l /home/ubuntu/botstudio-trump-of-yore/forever.log -o /home/ubuntu/botstudio-trump-of-yore/out.log -m 1 -c python app.py
```

