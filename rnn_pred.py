import numpy as np
import json
import psycopg2
from gensim.models.phrases import Phraser
from tensorflow.keras.models import load_model
from tensorflow.keras import preprocessing
from tensorflow.keras.preprocessing.text import tokenizer_from_json
from data_process import canonize


def ngrams_preprocess(corpus, ngrams=1, grams_join=" "):
    lst_corpus = []
    for string in corpus:
        lst_words = string.split()
        lst_grams = [grams_join.join(lst_words[i:i + ngrams]) for i in range(0, len(lst_words), ngrams)]
        lst_corpus.append(lst_grams)

    bigram = Phraser.load('\\Users\\Zeden\\Desktop\\bigram')
    trigram = Phraser.load('\\Users\\Zeden\\Desktop\\trigram')
    lst_ngrams_detectors = [bigram, trigram]
    if len(lst_ngrams_detectors) != 0:
        for detector in lst_ngrams_detectors:
            lst_corpus = list(detector[lst_corpus])
    return lst_corpus


def tokenize(corpus, ngrams=1, grams_join=" "):
    lst_corpus = ngrams_preprocess(corpus, ngrams=ngrams, grams_join=grams_join)
    with open('\\Users\\Zeden\\Desktop\\tokenizer.json') as f:
        data = json.load(f)
        tokenizer = tokenizer_from_json(data)
    lst_text2seq = tokenizer.texts_to_sequences(lst_corpus)
    X = preprocessing.sequence.pad_sequences(lst_text2seq, maxlen=15, padding="post", truncating="post")
    return X


def rnn_prediction():
    con = psycopg2.connect(database="postgres", user="postgres", password="abcd0987", host="127.0.0.1", port="5433")
    cur = con.cursor()
    cur.execute('SELECT id,post from DATA')
    rows = cur.fetchall()
    documents = [canonize(row[1]) for row in rows]
    doc = tokenize(documents)
    model = load_model('\\Users\\Zeden\\Desktop\\my_model.h5')
    predicted_prob = model.predict(doc)
    mapping = {0: 'business', 1: 'entertainment', 2: 'politics', 3: 'sport', 4: 'tech'}
    predicted = [mapping[np.argmax(pred)] for pred in
                 predicted_prob]
    for i in range(len(predicted)):
        cat = predicted[i]
        q = float(round(np.max(predicted_prob[i]), 3))
        cur.execute("UPDATE DATA SET category = %s, weights = %s WHERE id = %s", (cat, q, rows[i][0]))
    con.commit()
    con.close()


rnn_prediction()