# -*- coding: UTF-8 -*-
from multiprocessing import Pool
import time
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import CountVectorizer


def canonize(sourse):
    from nltk.stem import SnowballStemmer
    import nltk
    stemmer = SnowballStemmer('russian')
    stop_words = nltk.corpus.stopwords.words('russian')
    words = nltk.word_tokenize(sourse)
    without_stop_words = [word for word in words if not word in stop_words]
    n = [stemmer.stem(w).lower() for w in without_stop_words if len(w) > 1 and w.isalpha()]
    s = ''
    for i in range(len(n)):
        s += str(n[i]) + ' '
    return s


def vect_2_sentence(sourse1, sourse2):
    sourse = [sourse1, sourse2]
    vertorizer = CountVectorizer().fit_transform(sourse)
    vectors = vertorizer.toarray()
    return vectors


def similarity(vec1, vec2):
    vec1 = vec1.reshape(1,-1)
    vec2 = vec2.reshape(1, -1)

    return cosine_similarity(vec1, vec2)[0][0]


def main():
    start_time = time.time()
    text1 = u'Банк России приступил к масштабным вливаниям рублей в российскую банковскую систему, на которую легло бремя покрытия «дыры» в бюджете. По итогам двух операций репо в понедельник, 12 октября, ЦБ закачал в банки 620 млрд рублей, следует из данных на сайте регулятора.Из этой суммы 20 млрд рублей банки получили в виде кредитов на один год, а основную часть - 600 млрд - на 28 дней/.'
    text2 = u'ЦБ начинает масштабные вливания рублей в российскую банковскую систему. По итогам двух операций репо 12 октября ЦБ закачал в банки 620 миллиардов рублей, 20 млрд рублей из которых банки получили в виде кредитов на 1 год, а основную часть - 600 млрд - на 28 дней. '
    text3 = u'Друзья, про классных российских креативщиков поговорили, расскажите теперь про крутых российских бренд-менеджеров? Кто сейчас строит лучшие бренды? Кто покупает и производит самые креативные кампании? Кто каждый раз безошибочно выбирает лучшую идею из трех и не дает своим коллегам убить ее комментариями? '
    c1 = canonize(text1)
    c2 = canonize(text2)
    vec1 = vect_2_sentence(c1, c2)
    print(similarity(vec1[0], vec1[1]))
    print("--- %s seconds ---" % (time.time() - start_time))

main()