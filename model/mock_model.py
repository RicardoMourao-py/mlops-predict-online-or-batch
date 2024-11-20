"""
Module implementing a mock model for demonstration purposes.
"""
import pickle
from abc import ABC, abstractmethod

from sklearn.base import BaseEstimator
from sklearn.linear_model import LogisticRegression

class Model(BaseEstimator, ABC):
    """Abstract class defining the behavior of a model."""

    @abstractmethod
    def fit(self, X, y):
        """Abstract method to train the model."""
        raise NotImplementedError("The fit method must be implemented in subclasses.")

    @abstractmethod
    def predict(self, X):
        """Abstract method to make predictions with the trained model."""
        raise NotImplementedError("The predict method must be implemented in subclasses.")
    
    @abstractmethod
    def predict_proba(self, X):
        """Abstract method to make probabilities predictions with the trained model."""
        raise NotImplementedError("The predict method must be implemented in subclasses.")

class MockModel(Model):
    """Class implementing a RandomForestClassifier model."""

    def __init__(self):
        """Initializer of the class."""
        self.model = LogisticRegression(
           C=0.01,
           solver='newton-cg',
           max_iter=100
        )

    def fit(self, X, y):
        """Trains the model with input data X and labels y."""
        self.model.fit(X, y)

    def predict(self, X):
        """Makes predictions with the trained model using input data X."""
        return self.model.predict(X)
    
    def predict_proba(self, X):
        """Makes probabilities predictions with the trained model using input data X."""
        return self.model.predict_proba(X)

    def save(self, filename):
        """Saves the model to a file using pickle."""
        with open(filename, 'wb') as file:
            pickle.dump(self.model, file)
        print(f"Model saved successfully at {filename}")

    @classmethod
    def load(cls, filename):
        """Loads the model from a file using pickle."""
        with open(filename, 'rb') as file:
            model = pickle.load(file)
        instance = cls()
        instance.model = model
        return instance