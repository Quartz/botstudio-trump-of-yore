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



