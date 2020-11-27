import psycopg2
from Bayes import NaiveBayesModel
from rnn_pred import rnn_prediction
from nltk.stem import SnowballStemmer
import nltk
import re
import database
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def canonize(sourse):
    stemmer = SnowballStemmer('russian')
    stop_words = nltk.corpus.stopwords.words('russian')
    words = nltk.word_tokenize(sourse)
    without_stop_words = [word for word in words if not word in stop_words]
    n = [stemmer.stem(w).lower() for w in without_stop_words if len(w) > 1 and w.isalpha()]
    r = re.compile("[а-яА-Я]+")
    s = [w for w in filter(r.match, n)]
    s = ' '.join(s)
    return s


def clean_data():
    con = psycopg2.connect(database="postgres", user="postgres", password="abcd0987", host="127.0.0.1", port="5433")
    cur = con.cursor()
    cur.execute("SELECT id,post from TEMPDATA")
    rows = cur.fetchall()
    for row in rows:
        cur.execute("UPDATE TEMPDATA SET post = %s WHERE id = %s", (canonize(row[1]), rows[0]))
    con.commit()
    con.close()


def delete_equal_posts(probability_sim=0.35, show=False):
    con = psycopg2.connect(database="postgres", user="postgres", password="abcd0987", host="127.0.0.1", port="5433")
    cur = con.cursor()
    cur.execute("SELECT postid,post,id from DATA")
    rows = cur.fetchall()
    for i in range(len(rows)):
        cur.execute("UPDATE DATA SET postid = %s WHERE id = %s", (i, rows[i][2]))
    source = []
    for row in rows:
        source.append(canonize(row[1]))
    vectorizer = CountVectorizer().fit_transform(source)
    vectors = vectorizer.toarray()
    csim = cosine_similarity(vectors)
    """Получили матрицу косинусного сходства каждого документа с каждым:
     значение a[i][j] соответсвует вероятности сходства документа i с документом j"""

    for i in range(len(csim[0])):
        for j in range(i + 1, len(csim[0])):
            if csim[i][j] > probability_sim:
                if show:
                    print('---------------------------------------------------------------------------')
                    print(rows[i][1])
                    print(rows[j][1])
                ind = i if len(rows[j][1]) > len(rows[i][1]) else j
                cur.execute('DELETE from DATA where postid = %s', (ind,))

    con.commit()
    con.close()


def delete_short_posts(len_to_delete=90):
    con = psycopg2.connect(database="postgres", user="postgres", password="abcd0987", host="127.0.0.1", port="5433")
    cur = con.cursor()
    cur.execute("SELECT postid,post,id from TEMPDATA")
    rows = cur.fetchall()
    for i in range(len(rows)):
        if len(rows[i][1]) < len_to_delete:
            cur.execute('DELETE from TEMPDATA where id = %s', (rows[i][2],))

    con.commit()
    con.close()


def delete_spam():
    from Bayes import classify_one
    model = '\\Users\\Zeden\\Desktop\\model_spam'
    con = psycopg2.connect(database="postgres", user="postgres", password="abcd0987", host="127.0.0.1", port="5433")
    cur = con.cursor()
    cur.execute('SELECT id,post from TEMPDATA')
    rows = cur.fetchall()
    for row in rows:
        text = row[1]
        cat, q = classify_one(text, model)
        if cat == 'spam':
            cur.execute('DELETE from TEMPDATA where id = %s', (row[0],))

    con.commit()
    con.close()


def predict_category():
    from Bayes import classify_one
    model = '\\Users\\Zeden\\Desktop\\model_filefinal'
    con = psycopg2.connect(database="postgres", user="postgres", password="abcd0987", host="127.0.0.1", port="5433")
    cur = con.cursor()
    cur.execute('SELECT id,post from DATA')
    rows = cur.fetchall()
    for row in rows:
        text = row[1]
        cat, q = classify_one(text, model)
        for i in q:
            if i[0] == cat:
                q = i[1]
        cur.execute("UPDATE DATA SET category = %s, weights = %s WHERE id = %s", (cat, q, row[0]))
    con.commit()
    con.close()


def process_data(spam=True, equal=True, short=True, bayes=False, rnn=True, probability_sim=0.35, len_to_delete=90):
    if spam:
        delete_spam()
    if short:
        delete_short_posts(len_to_delete)

    database.insert_to_database()

    if equal:
        delete_equal_posts(probability_sim)
    try:
        if bayes:
            predict_category()
    except ValueError:
        pass
    if rnn:
        rnn_prediction()
