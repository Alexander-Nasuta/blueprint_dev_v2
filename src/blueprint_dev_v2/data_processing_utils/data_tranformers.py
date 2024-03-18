import pandas as pd

from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.preprocessing import MinMaxScaler


class ColumnDropper(BaseEstimator, TransformerMixin):
    def __init__(self, target: list):
        self.target = target

    def fit(self, target):
        return self

    def transform(self, x: pd.DataFrame) -> pd.DataFrame:
        return x.drop(self.target, axis=1)


class DropIncompleteRow(BaseEstimator, TransformerMixin):
    def __init__(self, target: list[str]):
        self.target = target

    def fit(self, target):
        return self

    def transform(self, x: pd.DataFrame) -> pd.DataFrame:
        return x.dropna(subset=self.target)


class FillNaNWithMean(BaseEstimator, TransformerMixin):
    def __init__(self, target: str):
        self.target = target

    def fit(self, target):
        return self

    def transform(self, x: pd.DataFrame) -> pd.DataFrame:
        x[self.target].fillna(x[self.target].mean(), inplace=True)
        return x


class FillNaNWithMedian(BaseEstimator, TransformerMixin):
    def __init__(self, target: str):
        self.target = target

    def fit(self, target):
        return self

    def transform(self, x: pd.DataFrame) -> pd.DataFrame:
        x[self.target].fillna(x[self.target].median(), inplace=True)
        return x


class FillNaNWithValue(BaseEstimator, TransformerMixin):
    def __init__(self, target: str, value: float):
        self.target = target
        self.value = value

    def fit(self, target):
        return self

    def transform(self, x: pd.DataFrame) -> pd.DataFrame:
        x[self.target].fillna(self.value, inplace=True)
        return x


class Discretisation(BaseEstimator, TransformerMixin):
    def __init__(self, target: str, bins: int, labels: list[str]):
        self.target = target
        self.bins = bins
        self.labels = labels

    def fit(self, target):
        return self

    def transform(self, x: pd.DataFrame) -> pd.DataFrame:
        x[self.target] = pd.cut(x[self.target],
                                bins=self.bins,
                                labels=self.labels)
        return x


class OneHotEncodePd(BaseEstimator, TransformerMixin):
    def __init__(self, target: str, prefix: str, sep: str, required_columns=None):
        if required_columns is None:
            required_columns = []
        self.target = target
        self.prefix = prefix
        self.sep = sep
        self.required_columns = required_columns

    def fit(self, target):
        return self

    def transform(self, x: pd.DataFrame) -> pd.DataFrame:
        # Perform in-place one-hot encoding
        df_encoded = pd.get_dummies(x, columns=[self.target], prefix=self.prefix,
                                    prefix_sep=self.sep, dtype=float)

        # Replace the original 'Category' column with the one-hot encoded columns
        x[df_encoded.columns] = df_encoded

        # Drop the original 'Category' column
        x.drop(columns=[self.target], inplace=True)

        # Ensure all required columns are present, adding them with 0s if necessary
        for column in self.required_columns:
            if column not in x.columns:
                x[column] = 0.0

        return x


class NormalizeCols(BaseEstimator, TransformerMixin):
    def __init__(self, target: str, feature_range: tuple):
        self.target = target
        self.feature_range = feature_range

    def fit(self, target):
        return self

    def transform(self, x: pd.DataFrame) -> pd.DataFrame:
        df = x.copy()  # don't modify original df
        min_max_scaler = MinMaxScaler(feature_range=(self.feature_range[0], self.feature_range[1]))
        df[self.target] = min_max_scaler.fit_transform(df[[self.target]])
        return df
