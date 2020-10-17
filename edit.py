import nltk
from nltk.stem import SnowballStemmer



def preprocess_data(docs):
    i = len(docs) - 1
    while i > 0:
        if docs[i] == '\n':
            docs.pop(i)
            i -= 1
        i -= 1
    #docs.pop(len(docs)-1)
    stemmer = SnowballStemmer('russian')
    stopwords = nltk.corpus.stopwords.words('russian')
    word = nltk.word_tokenize((' ').join(docs))  # Разбиение всего текста на слова
    n = [stemmer.stem(w).lower() for w in word if len(w) >1 and w.isalpha()] #Стемминг всех слов с исключением символов
    stopword = [stemmer.stem(w).lower() for w in stopwords] #Стемминг стоп-слов
    fdist = nltk.FreqDist(n)
    t = fdist.hapaxes()  #Слова которые встречаются один раз в тексте

    for i in range(len(docs)):
        docs[i] = nltk.word_tokenize(docs[i])
        docs[i] = [stemmer.stem(w).lower() for w in docs[i] if len(w) > 1 and w.isalpha()]
        word_stop = [w for w in docs[i] if w not in stopword]
        docs[i] = [w for w in word_stop if w not in t]

    for i in range(len(docs)):
        docsi = docs[i]
        s = ''
        for j in range(len(docsi)):
            s += docsi[j] + ' '
        docs[i] = s

    return docs

def simple_preprocess(sourse):
    sourse = sourse[0]
    from nltk.stem import SnowballStemmer
    import nltk
    stemmer = SnowballStemmer('russian')
    stop_words = nltk.corpus.stopwords.words('russian')
    words = nltk.word_tokenize(sourse)
    without_stop_words = [word for word in words if not word in stop_words]
    n = [stemmer.stem(w).lower() for w in without_stop_words if len(w) > 1 and w.isalpha()]
    s = ''
    for i in range(len(n)):
        s += n[i] + ' '
    return s

def get_target():
    with open('/Users/Zeden/Desktop/datacat.txt', 'r', encoding='utf8') as f:
        text = f.readlines()
    for i in range(len(text)):
        text[i] = text[i].strip()
        if text[i] == 'tech':
            text[i] = 0
        if text[i] == 'business':
            text[i] = 1
        if text[i] == 'sport':
            text[i] = 2
        if text[i] == 'entertainment':
            text[i] = 3
        if text[i] == 'politics':
            text[i] = 4
    return text


