import psycopg2
from Bayes import NaiveBayesModel
from Bayes import classify_one
from pprint import pprint


def f(cat, weit):
    for i in weit:
        if i[0] == cat:
            return i[1]


con = psycopg2.connect(database="postgres", user="postgres", password="abcd0987", host="127.0.0.1", port="5433")
cur = con.cursor()
cur.execute('SELECT * from LASTPOST3')
rows = cur.fetchall()
model = '\\Users\\Zeden\\Desktop\\model_filefinal'

bad_docs = []
good_docs = []
for row in rows:
    print("--------------------------------- New Text ---------------------------------")
    pprint(row[3])
    cat = input('b or g:')
    if cat == 'g': good_docs.append(row[3])
    if cat == 'b': bad_docs.append(row[3])


def stat(docs):
    weights = {
        '0': 0,
        '10': 0,
        '20': 0,
        '30': 0,
        '40': 0,
        '50': 0,
        '60': 0,
        '70': 0,
        '80': 0,
        '90': 0,
        '100': 0,
        '200': 0,
        '300': 0,
        '400': 0,
        '500': 0,
        '600': 0,
        '700': 0,
        '800': 0,
        '900': 0,
        '1000': 0,
        '1100': 0,
        '1200': 0,
        '1300': 0,
        '1400': 0,
        '1500': 0
    }
    stat2 = {
        '0': 0,
        '10': 0,
        '20': 0,
        '30': 0,
        '40': 0,
        '50': 0,
        '60': 0,
        '70': 0,
        '80': 0,
        '90': 0,
        '100': 0,
        '200': 0,
        '300': 0,
        '400': 0,
        '500': 0,
        '600': 0,
        '700': 0,
        '800': 0,
        '900': 0,
        '1000': 0,
        '1100': 0,
        '1200': 0,
        '1300': 0,
        '1400': 0,
        '1500': 0
    }
    for i in range(len(docs)):
        leng = len(docs[i])
        cat, weit = classify_one(docs[i], model)
        if leng < 100:
            if leng < 10:
                stat2['0'] = + 1
                weights['0'] += f(cat, weit)
            else:
                leng = leng // 10
                stat2[str(leng) + '0'] += 1
                weights[str(leng) + '0'] += f(cat, weit)

        else:
            if leng >= 1500:
                stat2['1500'] += 1
                weights['1500'] += f(cat, weit)
            else:
                leng = leng // 100
                stat2[str(leng) + '00'] += 1
                weights[str(leng) + '00'] += f(cat, weit)
    for i in weights:
        try:
            weights[i] = weights[i] / stat2[i]
        except ZeroDivisionError:
            weights[i] = 0

    print('Length : Amount : log of Probability')
    for i in stat2:
        print(f'{i} : {stat2[i]} : {weights[i]}')

stat(good_docs)
stat(bad_docs)
stat(bad_docs + good_docs)
