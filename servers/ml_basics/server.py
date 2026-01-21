import pickle
from pathlib import Path
from typing import List, Optional, Union

import pandas as pd
from mcp.server.fastmcp import FastMCP
from sklearn.cluster import KMeans
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.metrics import accuracy_score, mean_squared_error, silhouette_score
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier

mcp = FastMCP("ml_basics", log_level="ERROR")


def _load_data(file_path: str) -> pd.DataFrame:
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File '{file_path}' not found.")
    return pd.read_csv(path)


@mcp.tool()
def train_regression(
    data_file: str,
    target_column: str,
    feature_columns: Optional[List[str]] = None,
    test_size: float = 0.2,
    random_state: int = 42,
    output_model_path: Optional[str] = None,
) -> str:
    """
    Train a linear regression model.
    """
    try:
        df = _load_data(data_file)
        if feature_columns is None:
            feature_columns = [col for col in df.columns if col != target_column]
        X = df[feature_columns]
        y = df[target_column]
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=random_state
        )
        model = LinearRegression()
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        mse = mean_squared_error(y_test, y_pred)
        if output_model_path:
            with open(output_model_path, "wb") as f:
                pickle.dump(model, f)
            model_saved = f" Model saved to {output_model_path}."
        else:
            model_saved = ""
        return (
            f"Linear regression trained. "
            f"MSE on test set: {mse:.4f}. "
            f"Coefficients: {model.coef_}. Intercept: {model.intercept_:.4f}."
            f"{model_saved}"
        )
    except Exception as e:
        return f"Error training regression model: {str(e)}"


@mcp.tool()
def train_classification(
    data_file: str,
    target_column: str,
    feature_columns: Optional[List[str]] = None,
    model_type: str = "logistic_regression",
    test_size: float = 0.2,
    random_state: int = 42,
    output_model_path: Optional[str] = None,
) -> str:
    """
    Train a classification model.
    """
    try:
        df = _load_data(data_file)
        if feature_columns is None:
            feature_columns = [col for col in df.columns if col != target_column]
        X = df[feature_columns]
        y = df[target_column]
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=random_state, stratify=y
        )
        if model_type == "logistic_regression":
            model = LogisticRegression(random_state=random_state)
        elif model_type == "decision_tree":
            model = DecisionTreeClassifier(random_state=random_state)
        else:
            return f"Error: unknown model_type '{model_type}'. Choose 'logistic_regression' or 'decision_tree'."
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        acc = accuracy_score(y_test, y_pred)
        if output_model_path:
            with open(output_model_path, "wb") as f:
                pickle.dump(model, f)
            model_saved = f" Model saved to {output_model_path}."
        else:
            model_saved = ""
        return (
            f"{model_type} trained. "
            f"Accuracy on test set: {acc:.4f}. "
            f"Number of classes: {len(model.classes_)}."
            f"{model_saved}"
        )
    except Exception as e:
        return f"Error training classification model: {str(e)}"


@mcp.tool()
def train_clustering(
    data_file: str,
    feature_columns: Optional[List[str]] = None,
    n_clusters: int = 3,
    random_state: int = 42,
    output_labels_path: Optional[str] = None,
) -> str:
    """
    Perform K‑Means clustering.
    """
    try:
        df = _load_data(data_file)
        if feature_columns is None:
            # Use all numeric columns
            numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
            if len(numeric_cols) == 0:
                return "Error: No numeric columns found for clustering."
            feature_columns = numeric_cols
        X = df[feature_columns]
        model = KMeans(n_clusters=n_clusters, random_state=random_state, n_init=10)
        labels = model.fit_predict(X)
        silhouette = silhouette_score(X, labels) if len(set(labels)) > 1 else 0.0
        if output_labels_path:
            out_df = df.copy()
            out_df["cluster"] = labels
            out_df.to_csv(output_labels_path, index=False)
            labels_saved = f" Cluster labels saved to {output_labels_path}."
        else:
            labels_saved = ""
        return (
            f"K‑Means clustering completed. "
            f"Number of clusters: {n_clusters}. "
            f"Silhouette score: {silhouette:.4f}. "
            f"Inertia: {model.inertia_:.2f}."
            f"{labels_saved}"
        )
    except Exception as e:
        return f"Error performing clustering: {str(e)}"


@mcp.tool()
def predict(
    model_file: str,
    data_file: str,
    output_predictions_path: Optional[str] = None,
) -> str:
    """
    Make predictions using a saved model.
    """
    try:
        with open(model_file, "rb") as f:
            model = pickle.load(f)
        df = _load_data(data_file)
        predictions = model.predict(df)
        if output_predictions_path:
            out_df = df.copy()
            out_df["prediction"] = predictions
            out_df.to_csv(output_predictions_path, index=False)
            saved = f" Predictions saved to {output_predictions_path}."
        else:
            saved = ""
        return f"Predictions generated. First few: {predictions[:5]}.{saved}"
    except Exception as e:
        return f"Error making predictions: {str(e)}"


@mcp.tool()
def evaluate_model(
    model_file: str,
    data_file: str,
    target_column: str,
    metric: str = "auto",
) -> str:
    """
    Evaluate a model's performance.
    """
    try:
        with open(model_file, "rb") as f:
            model = pickle.load(f)
        df = _load_data(data_file)
        X = df.drop(columns=[target_column])
        y = df[target_column]
        preds = model.predict(X)
        # Determine metric
        if metric == "auto":
            # Guess based on model type
            if hasattr(model, "predict_proba"):
                metric = "accuracy"
            elif hasattr(model, "inertia_"):
                metric = "silhouette"
            else:
                metric = "mse"
        if metric == "mse":
            score = mean_squared_error(y, preds)
            return f"Mean Squared Error: {score:.4f}"
        elif metric == "accuracy":
            score = accuracy_score(y, preds)
            return f"Accuracy: {score:.4f}"
        elif metric == "silhouette":
            # Need feature matrix X (original features)
            score = silhouette_score(X, preds) if len(set(preds)) > 1 else 0.0
            return f"Silhouette score: {score:.4f}"
        else:
            return f"Error: unknown metric '{metric}'. Choose 'mse', 'accuracy', or 'silhouette'."
    except Exception as e:
        return f"Error evaluating model: {str(e)}"


@mcp.tool()
def save_model(model_object: str, file_path: str) -> str:
    """
    Save a model to disk (placeholder).
    """
    return "This tool is a placeholder; models are saved automatically during training."


@mcp.tool()
def load_model(file_path: str) -> str:
    """
    Load a model from disk (placeholder).
    """
    try:
        with open(file_path, "rb") as f:
            model = pickle.load(f)
        return f"Model loaded from {file_path}. Type: {type(model).__name__}."
    except Exception as e:
        return f"Error loading model: {str(e)}"


@mcp.tool()
def split_data(
    data_file: str,
    target_column: str,
    test_size: float = 0.2,
    random_state: int = 42,
    output_train_path: Optional[str] = None,
    output_test_path: Optional[str] = None,
) -> str:
    """
    Split a dataset into training and testing sets.
    """
    try:
        df = _load_data(data_file)
        X = df.drop(columns=[target_column])
        y = df[target_column]
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=random_state
        )
        train_df = pd.concat([X_train, y_train], axis=1)
        test_df = pd.concat([X_test, y_test], axis=1)
        if output_train_path:
            train_df.to_csv(output_train_path, index=False)
        if output_test_path:
            test_df.to_csv(output_test_path, index=False)
        saved = ""
        if output_train_path and output_test_path:
            saved = f" Training data saved to {output_train_path}, test data to {output_test_path}."
        elif output_train_path:
            saved = f" Training data saved to {output_train_path}."
        elif output_test_path:
            saved = f" Test data saved to {output_test_path}."
        return f"Data split complete. Train size: {len(train_df)}, test size: {len(test_df)}.{saved}"
    except Exception as e:
        return f"Error splitting data: {str(e)}"


if __name__ == "__main__":
    mcp.run()
