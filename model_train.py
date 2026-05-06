import joblib
import numpy as np
from sklearn import datasets, svm, metrics
from sklearn.model_selection import train_test_split

def train_model():
    print("Loading digits dataset...")
    # Loading scikit-learn's built-in digits dataset (8x8 images)
    digits = datasets.load_digits()

    # Flatten the images to turn them into data (n_samples, n_features)
    n_samples = len(digits.images)
    data = digits.images.reshape((n_samples, -1))

    # Split data to train and test
    X_train, X_test, y_train, y_test = train_test_split(
        data, digits.target, test_size=0.5, shuffle=False
    )

    print("Training Support Vector Classifier model...")
    # Create a classifier: a support vector classifier
    classifier = svm.SVC(gamma=0.001)

    # Learn the digits on the train subset
    classifier.fit(X_train, y_train)

    # Predict the value of the digit on the test subset
    predicted = classifier.predict(X_test)

    # Calculate accuracy
    accuracy = metrics.accuracy_score(y_test, predicted)
    print(f"Model trained. Accuracy: {accuracy:.4f}")

    # Save the model
    joblib.dump(classifier, 'model.pkl')
    print("Model saved as model.pkl")

if __name__ == "__main__":
    train_model()
