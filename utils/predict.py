from keras_preprocessing.sequence import pad_sequences
import numpy as np


def predict(texts, mdl, tokenizer):
    """
    Accepts array of texts (strings) and pre-trained deep learning model
    Returns array of predicted labels

    """
    # text = []
    sequences = tokenizer.texts_to_sequences(texts)
    pad = pad_sequences(sequences, maxlen=231) # hard-coded :)
    predictions = mdl.predict(pad)
    labels = np.argmax(predictions, axis=1)
    lbls_arr = []
    for lbl in labels:
        lbls_arr.append(lbl)
    return lbls_arr

