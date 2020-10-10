import joblib
import numpy as np
import sklearn.datasets
import sklearn.feature_extraction.text
import sklearn.naive_bayes
import sklearn.metrics
import common


# Test and evaluate a model
def test_and_evaluate(test):
    # Load models
    vectorizer = joblib.load('C:\\Users\\Zeden\\Desktop\\model\\vectorizer.jbl')
    transformer = joblib.load('C:\\Users\\Zeden\\Desktop\\model\\transformer.jbl')
    model = joblib.load('C:\\Users\\Zeden\\Desktop\\model\\model.jbl')
    # Convert to bag of words
    X = vectorizer.transform(test.data)
    # Convert from occurrences to frequencies
    X = transformer.transform(X)
    # Make predictions
    predictions = model.predict(X)
    print('-- Results --')
    accuracy = sklearn.metrics.accuracy_score(test.target, predictions)
    print('Accuracy: {0:.2f}'.format(accuracy * 100.0))
    print('Classification Report:')
    print(sklearn.metrics.classification_report(test.target, predictions, target_names=test.target_names))


# The main entry point for this module
def main():
    # Load test dataset
    # Load text files with categories as subfolder names
    # Individual samples are assumed to be files stored a two levels folder structure
    # The folder names are used as supervised signal label names. The individual file names are not important.
    test = sklearn.datasets.load_files('C:\\Users\\Zeden\\Desktop\\20news_bydate\\20news-bydate-test', shuffle=False,
                                       load_content=True, encoding='latin1')
    # Preprocess data
    test.data = common.preprocess_data(test.data)

    # Test and evaluate
    test_and_evaluate(test)


# Tell python to run main method
if __name__ == "__main__": main()