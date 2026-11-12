try:
    from mage_ai.data_preparation.decorators import transformer, test
except ImportError:  # Allows local testing without Mage.
    def transformer(func):
        return func
    def test(func):
        return func

from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score


@transformer
def train_model(df, **kwargs):
    """Fit a decision tree and return model, predictions, and test accuracy."""
    max_depth = int(kwargs.get("max_depth", 3))
    if max_depth < 1:
        raise ValueError("max_depth must be at least 1")

    features = [c for c in df.columns if c not in ("target", "split")]
    train_df = df[df["split"] == "train"]
    test_df = df[df["split"] == "test"]
    if train_df.empty or test_df.empty:
        raise ValueError("Both train and test partitions must contain rows")

    model = DecisionTreeClassifier(max_depth=max_depth, random_state=42)
    model.fit(train_df[features], train_df["target"])
    predictions = model.predict(test_df[features])
    accuracy = float(accuracy_score(test_df["target"], predictions))

    return {
        "model": model,
        "features": features,
        "X_test": test_df[features].copy(),
        "y_test": test_df["target"].copy(),
        "predictions": predictions,
        "test_accuracy": accuracy,
        "max_depth": max_depth,
    }


@test
def test_accuracy_gate(output, *args):
    """Do not allow a low-quality model to reach the exporter."""
    assert output["test_accuracy"] >= 0.90, (
        f"test_accuracy={output['test_accuracy']:.4f} is below 0.90"
    )
