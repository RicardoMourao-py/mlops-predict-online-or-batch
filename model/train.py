import pandas as pd
import numpy as np

from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, OrdinalEncoder
from sklearn.base import TransformerMixin, BaseEstimator

from mock_model import MockModel

class CustomCategoricalImputer(BaseEstimator, TransformerMixin):
    """Imputador personalizado para valores ausentes em colunas categóricas."""
    
    def __init__(self, categorical_features):
        self.categorical_features = categorical_features
    
    def fit(self, X, y=None):
        """Ajusta o imputador aos dados de treinamento."""
        return self
    
    def transform(self, X):
        """Transforma os dados substituindo os valores ausentes nas colunas categóricas."""
        imputed_X = X.copy()
        for col in self.categorical_features:
            value_counts = imputed_X[col].value_counts(normalize=True)
            imputed_X[col] = imputed_X[col].apply(lambda x: np.random.choice(value_counts.index, p=value_counts.values) if pd.isnull(x) else x)
        return imputed_X

class ModelTrainer:
    """Classe para treinar e salvar o modelo."""

    def __init__(self, data_file_path):
        self.data_file_path = data_file_path

    def load_data(self):
        """Carrega os dados a partir do arquivo CSV."""
        return pd.read_csv(self.data_file_path)

    def preprocess_data(self, df):
        """Realiza o pré-processamento dos dados."""
        # Lista de colunas numéricas
        numerical_features = ['idade_inicio_problema_atual']
        # Lista de colunas categóricas (excluindo as colunas mencionadas)
        categorical_features = [col for col in df.columns if col not in ['resultado_teste_genetico', 'Paciente','idade_inicio_problema_atual']]
        # Pipeline for numeric features
        numeric_transformer = Pipeline(steps=[
            ('imputer', SimpleImputer(strategy='mean')),  # Impute NaN with mean
            ('scaler', StandardScaler())                # Scale numeric features
        ])

        categorical_transformer = Pipeline(steps=[
            ('imputer', CustomCategoricalImputer(categorical_features)),  # Imputer customizado
            ('encoder', OrdinalEncoder(handle_unknown="use_encoded_value", unknown_value=-1))     
        ])
        # Apply preprocessing pipelines
        preprocessor = ColumnTransformer(
            transformers=[
                ('num', numeric_transformer, numerical_features),
                ('cat', categorical_transformer, categorical_features)
            ])

        return preprocessor

    def train_and_save_model(self):
        """Treina o modelo e o salva."""
        # Carrega os dados
        df = self.load_data()
        # Pré-processamento dos dados
        X_data = df.drop(['Paciente', 'resultado_teste_genetico'], axis=1)
        y_data = df['resultado_teste_genetico']
        preprocessor = self.preprocess_data(df)
        X_data_preprocessed = preprocessor.fit_transform(X_data)
        # Divide os dados em conjunto de treinamento e teste
        X_train, X_test, y_train, y_test = train_test_split(X_data_preprocessed, y_data, test_size=0.2, random_state=42)
        # Treinamento do modelo
        model = MockModel()
        model.fit(X_train, y_train)
        # Salvando o modelo
        filename = "models/classifier.pkl"
        model.save(filename)

if __name__ == "__main__":
    data_file_path = 'data/dados_simulados.csv'
    trainer = ModelTrainer(data_file_path)
    trainer.train_and_save_model()