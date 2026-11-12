try:
    from mage_ai.data_preparation.decorators import data_exporter, test
except ImportError:  # Allows imports outside Mage.
    def data_exporter(func):
        return func
    def test(func):
        return func

from pathlib import Path
import pandas as pd


@data_exporter
def save_results(model_output, **kwargs):
    """Write a compact prediction file after the model test gate passes."""
    output_path = Path(kwargs.get("output_path", "iris_predictions.csv"))
    result = pd.DataFrame({
        "actual": model_output["y_test"].to_numpy(),
        "predicted": model_output["predictions"],
    })
    result.to_csv(output_path, index=False)
    return {"path": str(output_path), "rows_written": len(result)}


@test
def test_saved_results(output, *args):
    assert output["rows_written"] == 30
    assert Path(output["path"]).exists()
