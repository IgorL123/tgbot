import joblib
import numpy as np
import matplotlib.pyplot as plt
import sklearn.datasets
import sklearn.feature_extraction.text
import sklearn.naive_bayes
import sklearn.metrics
import sklearn.model_selection
import sklearn.pipeline
from edit import preprocess_data
from edit import get_target


# Perform a grid search to find the best hyperparameters
def grid_search(train):
    target = get_target()
    clf_pipeline = sklearn.pipeline.Pipeline([
        ('v', sklearn.feature_extraction.text.CountVectorizer(strip_accents='ascii', stop_words='english')),
        ('t', sklearn.feature_extraction.text.TfidfTransformer()),
        ('c', sklearn.naive_bayes.MultinomialNB(fit_prior=True, class_prior=None))
    ])
    parameters = {
        'v__ngram_range': [(1, 1), (1, 2), (1, 3), (1, 4)],
        'v__lowercase': (True, False),
        't__use_idf': (True, False),
        'c__alpha': (0.3, 0.6, 1.0)}
    gs_classifier = sklearn.model_selection.GridSearchCV(clf_pipeline, parameters, cv=5, iid=False, n_jobs=2,
                                                         scoring='accuracy', verbose=1)
    gs_classifier = gs_classifier.fit(train, target)
    print('---- Results ----')
    print('Best score: ' + str(gs_classifier.best_score_))
    for name in sorted(parameters.keys()):
        print('{0}: {1}'.format(name, gs_classifier.best_params_[name]))


def train_and_evaluate(train,target):
    count_vect = sklearn.feature_extraction.text.CountVectorizer(strip_accents='ascii', ngram_range=(1, 1))
    X = count_vect.fit_transform(train)
    transformer = sklearn.feature_extraction.text.TfidfTransformer()
    X = transformer.fit_transform(X)
    #target = get_target()

    model = sklearn.naive_bayes.MultinomialNB(alpha=0.3, fit_prior=True, class_prior=None)
    model.fit(X, target)

    joblib.dump(count_vect, 'C:\\Users\\Zeden\\Desktop\\model1\\vectorizer.jbl')
    joblib.dump(transformer, 'C:\\Users\\Zeden\\Desktop\\model1\\transformer.jbl')
    joblib.dump(model, 'C:\\Users\\Zeden\\Desktop\\model1\\model.jbl')

    print('-- Training data --')
    predictions = model.predict(X)
    accuracy = sklearn.metrics.accuracy_score(target, predictions)
    print('Accuracy: {0:.2f}'.format(accuracy * 100.0))
    print('Classification Report:')
    print(sklearn.metrics.classification_report(target, predictions))
    print('')


def main():
    target = sklearn.datasets.load_files('C:\\Users\\Zeden\\Desktop\\pp', shuffle=False,load_content=True)

    with open('/Users/Zeden/Desktop/32.txt', 'r', encoding='utf8') as f:
        train = f.readlines()
    train = preprocess_data(train)
    train.pop(len(train)-1)
    #grid_search(train)
    train_and_evaluate(train, target.target)


if __name__ == "__main__": main()