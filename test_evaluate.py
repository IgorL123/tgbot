import joblib
import sklearn.datasets
import sklearn.feature_extraction.text
import sklearn.naive_bayes
import sklearn.metrics
import edit


def test_and_evaluate(test):
    vectorizer = joblib.load('C:\\Users\\Zeden\\Desktop\\model\\vectorizer.jbl')
    transformer = joblib.load('C:\\Users\\Zeden\\Desktop\\model\\transformer.jbl')
    model = joblib.load('C:\\Users\\Zeden\\Desktop\\model\\model.jbl')

    X = vectorizer.transform(test)
    X = transformer.transform(X)
    predictions = model.predict(X)

    print('-- Results --')
    print(predictions)


def main():
    #with open('/Users/Zeden/Desktop/dataset_RU.txt', 'r', encoding='utf8') as f:
        #train = f.readlines()
    train = open('/Users/Zeden/Desktop/123.txt','r', encoding='utf8')
    train = train.readlines()
    train = edit.simple_preprocess(train)
    print(train)
    #test_and_evaluate(train)


if __name__ == "__main__":main()