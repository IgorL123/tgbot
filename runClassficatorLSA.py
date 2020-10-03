import numpy
from numpy import *
import nltk
import scipy
from nltk.corpus import brown
from nltk.stem import SnowballStemmer
from scipy.spatial.distance import pdist
from scipy.cluster import hierarchy
import matplotlib.pyplot as plt
stemmer = SnowballStemmer('russian')
stopwords = nltk.corpus.stopwords.words('russian')
#Тестовый набор документов из коротких новостей
docs =[
    "Британская полиция знает о местонахождении основателя WikiLeaks",# Документ № 0
    "В суде США начинается процесс против россиянина, рассылавшего спам",# Документ №1
    "Церемонию вручения Нобелевской премии мира бойкотируют 19 стран",# Документ №2
    "В Великобритании основатель арестован основатель сайта Wikileaks Джулиан Ассандж",# Документ №3
    "Украина игнорирует церемонию вручения Нобелевской премии",# Документ №4
    "Шведский суд отказался рассматривать апелляцию основателя Wikileaks",# Документ №5
    "НАТО и США разработали планы обороны стран Балтии против России",# Документ №6
    "Полиция Великобритании нашла основателя WikiLeaks, но, не арестовала",# Документ №7
    "В Стокгольме и Осло сегодня состоится вручение Нобелевских премий"# Документ №8
]
word=nltk.word_tokenize((' ').join(docs))# Разбиение всего текста на слова
n=[stemmer.stem(w).lower() for w in word if len(w) >1 and w.isalpha()]#Стемминг всех слов с исключением символов
stopword = [stemmer.stem(w).lower() for w in stopwords]#Стемминг стоп-слов
fdist=nltk.FreqDist(n)
t=fdist.hapaxes()#Слова которые встречаются один раз в тексте
#Построение частотной матрицы А
d={};c=[]
for i in range(0,len(docs)):
    word=nltk.word_tokenize(docs[i])
    word_stem=[stemmer.stem(w).lower()  for w in word if len(w)>1 and  w.isalpha()]
    word_stop=[ w for w in word_stem if w not in stopword]
    words=[ w for w in word_stop if w not in t]
    for w in words:
        if w not in c:
            c.append(w)
            d[w]= [i]
        elif w in c:
            d[w]= d[w]+[i]
a=len(c); b=len(docs)
A = numpy.zeros([a,b])
c.sort()
for i, k in enumerate(c):
    for j in d[k]:
        A[i,j] += 1
# TF-IDF нормализация матрицы А
wpd = sum(A, axis=0)
dpw= sum(asarray(A > 0,'i'), axis=1)
rows, cols = A.shape
for i in range(rows):
    for j in range(cols):
             m=float(A[i,j])/wpd[j]
             n=log(float(cols) /dpw[i])
             A[i,j] =round(n*m,2)
#Сингулярное разложение нормализованной матрицы А
U, S,Vt = numpy.linalg.svd(A)
rows, cols = U.shape
for j in range(0,cols):
           for i  in range(0,rows):
               U[i,j]=round(U[i,j],4)
print('Первые 2 столбца ортогональной матрицы U слов')
for i, row in enumerate(U):
    print(c[i], row[0:2])
res1=-1*U[:,0:1]; res2=-1*U[:,1:2]
data_word=[]
for i in range(0,len(c)):# Подготовка исходных данных в виде вложенных списков координат
    data_word.append([res1[i][0],res2[i][0]])
plt.figure()
plt.subplot(221)
dist = pdist(data_word, 'euclidean')# Вычисляется евклидово расстояние (по умолчанию)
plt.hist(dist, 500, color='green', alpha=0.5)# Диаграмма евклидовых расстояний
Z = hierarchy.linkage(dist, method='average')# Выделение кластеров
plt.subplot(222)
hierarchy.dendrogram(Z, labels=c, color_threshold=.25, leaf_font_size=8, count_sort=True,orientation='right')
print('Первые 2 строки ортогональной матрицы Vt документов')
rows, cols = Vt.shape
for j in range(0,cols):
    for i  in range(0,rows):
        Vt[i,j]=round(Vt[i,j],4)
print(-1*Vt[0:2, :])
res3=(-1*Vt[0:1, :]);res4=(-1*Vt[1:2, :])
data_docs=[];name_docs=[]
for i in range(0,len(docs)):
    name_docs.append(str(i))
    data_docs.append([res3[0][i],res4[0][i]])
plt.subplot(223)
dist = pdist(data_docs, 'euclidean')
plt.hist(dist, 500, color='green', alpha=0.5)
Z = hierarchy.linkage(dist, method='average')
plt.subplot(224)
hierarchy.dendrogram(Z, labels=name_docs, color_threshold=.25, leaf_font_size=8, count_sort=True)
#plt.show()
print('Первые 3 столбца ортогональной матрицы U слов')
for i, row in enumerate(U):
    print(c[i], row[0:3])
res1=-1*U[:,0:1]; res2=-1*U[:,1:2];res3=-1*U[:,2:3]
data_word_xyz=[]
for i in range(0,len(c)):
    data_word_xyz.append([res1[i][0],res2[i][0],res3[i][0]])
plt.figure()
plt.subplot(221)
dist = pdist(data_word_xyz, 'euclidean')# Вычисляется евклидово расстояние (по умолчанию)
plt.hist(dist, 500, color='green', alpha=0.5)#Диаграмма евклидовых растояний
Z = hierarchy.linkage(dist, method='average')# Выделение кластеров
plt.subplot(222)
hierarchy.dendrogram(Z, labels=c, color_threshold=.25, leaf_font_size=8, count_sort=True,orientation='right')
print('Первые 3 строки ортогональной матрицы Vt документов')
rows, cols = Vt.shape
for j in range(0,cols):
    for i  in range(0,rows):
        Vt[i,j]=round(Vt[i,j],4)
print(-1*Vt[0:3, :])
res3=(-1*Vt[0:1, :]);res4=(-1*Vt[1:2, :]);res5=(-1*Vt[2:3, :])
data_docs_xyz=[];name_docs_xyz=[]
for i in range(0,len(docs)):
    name_docs_xyz.append(str(i))
    data_docs_xyz.append([res3[0][i],res4[0][i],res5[0][i]])
plt.subplot(223)
dist = pdist(data_docs_xyz, 'euclidean')
plt.hist(dist, 500, color='green', alpha=0.5)
Z = hierarchy.linkage(dist, method='average')
plt.subplot(224)
hierarchy.dendrogram(Z, labels=name_docs_xyz, color_threshold=.25, leaf_font_size=8, count_sort=True)
plt.show()