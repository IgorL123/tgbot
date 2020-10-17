# -*- coding: UTF-8 -*-
def canonize(source):
    stop_symbols = '/\.,!?:;-\n\r()'

    stop_words = (u'это', u'как', u'так',
                  u'и', u'в', u'над',
                  u'к', u'до', u'не',
                  u'на', u'но', u'за',
                  u'то', u'с', u'ли',
                  u'а', u'во', u'от',
                  u'со', u'для', u'о',
                  u'же', u'ну', u'вы',
                  u'бы', u'что', u'кто',
                  u'он', u'она')

    return ([x for x in [y.strip(stop_symbols) for y in source.lower().split()] if x and (x not in stop_words)])

def canonize1(sourse):
    from nltk.stem import SnowballStemmer
    import nltk
    stemmer = SnowballStemmer('russian')
    stop_words = nltk.corpus.stopwords.words('russian')
    words = nltk.word_tokenize(sourse)
    without_stop_words = [word for word in words if not word in stop_words]
    n = [stemmer.stem(w).lower() for w in without_stop_words if len(w) > 1 and w.isalpha()]
    return n

def genshingle(source):
    import binascii
    shingleLen = 2 # длина шингла
    out = []
    for i in range(len(source) - (shingleLen - 1)):
        out.append(binascii.crc32(' '.join([x for x in source[i:i + shingleLen]]).encode('utf-8')))

    return out


def compaire(source1, source2):
    same = 0
    for i in range(len(source1)):
        if source1[i] in source2:
            same += 1

    return same * 2 / float(len(source1) + len(source2)) * 100


def main():
    text1 = u'Банк России приступил к масштабным вливаниям рублей в российскую банковскую систему, на которую легло бремя покрытия «дыры» в бюджете. По итогам двух операций репо в понедельник, 12 октября, ЦБ закачал в банки 620 млрд рублей, следует из данных на сайте регулятора.Из этой суммы 20 млрд рублей банки получили в виде кредитов на один год, а основную часть - 600 млрд - на 28 дней/.'
    text2 = u'ЦБ начинает масштабные вливания рублей в российскую банковскую систему. По итогам двух операций репо 12 октября ЦБ закачал в банки 620 миллиардов рублей, 20 млрд рублей из которых банки получили в виде кредитов на 1 год, а основную часть - 600 млрд - на 28 дней. '
    text3 = u'Друзья, про классных российских креативщиков поговорили, расскажите теперь про крутых российских бренд-менеджеров? Кто сейчас строит лучшие бренды? Кто покупает и производит самые креативные кампании? Кто каждый раз безошибочно выбирает лучшую идею из трех и не дает своим коллегам убить ее комментариями? '
    cmp1 = genshingle(canonize1(text1))
    cmp2 = genshingle(canonize1(text2))
    print(cmp1)
    print(cmp2)
    c1 =(canonize1(text1))
    c2 = (canonize1(text2))
    print(compaire(cmp1, cmp2))
    print(compaire(c1,c2))


main()