try:
    from mage_ai.data_preparation.decorators import transformer, test
except ImportError:  # Allows imports outside Mage.
    def transformer(func):
        return func
    def test(func):
        return func

import pandas as pd
from sklearn.metrics import confusion_matrix, classification_report


@transformer
def evaluate_model(model_output, **kwargs):
    labels = sorted(set(model_output["y_test"].tolist()))
    matrix = confusion_matrix(model_output["y_test"], model_output["predictions"], labels=labels)
    report = classification_report(
        model_output["y_test"],
        model_output["predictions"],
        labels=labels,
        output_dict=True,
        zero_division=0,
    )
    metrics = pd.DataFrame(report).transpose().reset_index(names="class")
    return {
        "confusion_matrix": matrix.tolist(),
        "labels": labels,
        "metrics": metrics,
        "test_accuracy": model_output["test_accuracy"],
    }


@test
def test_evaluation(output, *args):
    assert len(output["confusion_matrix"]) == 3
    assert output["test_accuracy"] >= 0.90
