import joblib
import numpy as np
import matplotlib.pyplot as plt
import sklearn.datasets
import sklearn.feature_extraction.text
import sklearn.naive_bayes
import sklearn.metrics
import sklearn.model_selection
import sklearn.pipeline
import common


def visualize_dataset(ds):
    # Print dataset
    # for i in range(5):
    #    print(ds.data[i])
    # print(ds.target_names)
    print('--- Information ---')
    print('Number of articles: ' + str(len(ds.data)))
    print('Number of categories: ' + str(len(ds.target_names)))
    # Count number of articles in each category
    plot_X = np.arange(20, dtype=np.int16)
    plot_Y = np.zeros(20)
    for i in range(len(ds.data)):
        plot_Y[ds.target[i]] += 1
    print('\n--- Class distribution ---')
    for i in range(len(plot_X)):
        print('{0}: {1:.0f}'.format(ds.target_names[plot_X[i]], plot_Y[i]))
    # Plot the balance of the dataset
    figure = plt.figure(figsize=(16, 10))
    figure.suptitle('Balance of data set', fontsize=16)
    plt.bar(plot_X, plot_Y, align='center', color='rgbkymc')
    plt.xticks(plot_X, ds.target_names, rotation=25, horizontalalignment='right')
    # plt.show()
    plt.savefig('C:\\Users\\Zeden\\Desktop\\model\\20-newsgroups-balance.png')


# Perform a grid search to find the best hyperparameters
def grid_search(train):
    # Create a pipeline
    clf_pipeline = sklearn.pipeline.Pipeline([
        ('v', sklearn.feature_extraction.text.CountVectorizer(strip_accents='ascii', stop_words='english')),
        ('t', sklearn.feature_extraction.text.TfidfTransformer()),
        ('c', sklearn.naive_bayes.MultinomialNB(fit_prior=True, class_prior=None))
    ])
    # Set parameters (name in pipeline + name of parameter)
    parameters = {
        'v__ngram_range': [(1, 1), (1, 2), (1, 3), (1, 4)],
        'v__lowercase': (True, False),
        't__use_idf': (True, False),
        'c__alpha': (0.3, 0.6, 1.0)}
    # Create a grid search classifier
    gs_classifier = sklearn.model_selection.GridSearchCV(clf_pipeline, parameters, cv=5, iid=False, n_jobs=2,
                                                         scoring='accuracy', verbose=1)

    # Start a search (Warning: takes a long time if the whole dataset is used)
    # Slice: (train.data[:4000], train.target[:4000])
    gs_classifier = gs_classifier.fit(train.data, train.target)
    # Print results
    print('---- Results ----')
    print('Best score: ' + str(gs_classifier.best_score_))
    for name in sorted(parameters.keys()):
        print('{0}: {1}'.format(name, gs_classifier.best_params_[name]))


# Train and evaluate a model
def train_and_evaluate(train):
    # Convert to bag of words
    count_vect = sklearn.feature_extraction.text.CountVectorizer(strip_accents='ascii', stop_words='english',
                                                                 lowercase=True, ngram_range=(1, 1))
    X = count_vect.fit_transform(train.data)
    # Convert from occurrences to frequencies
    # Occurrence count is a good start but there is an issue: longer documents will have higher average count values than shorter documents, even though they might talk about the same topics.
    # To avoid these potential discrepancies it suffices to divide the number of occurrences of each word in a document by the total number of words in the document: these new features are called tf for Term Frequencies.
    transformer = sklearn.feature_extraction.text.TfidfTransformer()
    X = transformer.fit_transform(X)
    # Create a model
    model = sklearn.naive_bayes.MultinomialNB(alpha=0.3, fit_prior=True, class_prior=None)
    # Train the model
    model.fit(X, train.target)
    # Save models
    joblib.dump(count_vect, 'C:\\Users\\Zeden\\Desktop\\model\\vectorizer.jbl')
    joblib.dump(transformer, 'C:\\Users\\Zeden\\Desktop\\model\\transformer.jbl')
    joblib.dump(model, 'C:\\Users\\Zeden\\Desktop\\model\\model.jbl')
    # Evaluate on training data
    print('-- Training data --')
    predictions = model.predict(X)
    accuracy = sklearn.metrics.accuracy_score(train.target, predictions)
    print('Accuracy: {0:.2f}'.format(accuracy * 100.0))
    print('Classification Report:')
    print(sklearn.metrics.classification_report(train.target, predictions, target_names=train.target_names))
    print('')
    # Evaluate with 10-fold CV
    print('-- 10-fold CV --')
    predictions = sklearn.model_selection.cross_val_predict(model, X, train.target, cv=10)
    accuracy = sklearn.metrics.accuracy_score(train.target, predictions)
    print('Accuracy: {0:.2f}'.format(accuracy * 100.0))
    print('Classification Report:')
    print(sklearn.metrics.classification_report(train.target, predictions, target_names=train.target_names))


# The main entry point for this module
def main():
    # Load train dataset
    # Load text files with categories as subfolder names
    # Individual samples are assumed to be files stored a two levels folder structure
    # The folder names are used as supervised signal label names. The individual file names are not important.
    train = sklearn.datasets.load_files('C:\\Users\\Zeden\\Desktop\\20news_bydate\\20news-bydate-train', shuffle=False,
                                        load_content=True, encoding='latin1')
    # Visualize dataset
    # visualize_dataset(train)
    # Preprocess data
    train.data = common.preprocess_data(train.data)
    # Print cleaned data
    # print(train.data[0])
    # Grid search
    # grid_search(train)
    # Train and evaluate
    train_and_evaluate(train)


# Tell python to run main method
if __name__ == "__main__": main()