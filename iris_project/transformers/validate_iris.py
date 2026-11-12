try:
    from mage_ai.data_preparation.decorators import transformer, test
except ImportError:  # Allows unit tests to run outside a Mage installation.
    def transformer(func):
        return func
    def test(func):
        return func


@transformer
def validate_iris(df, *args, **kwargs):
    """Validate input data and pass it through unchanged."""
    if df.isna().any().any():
        raise ValueError("Iris data contains missing values")
    if "target" not in df.columns or df["target"].nunique() != 3:
        raise ValueError("Iris data must contain exactly three target classes")
    return df.copy()


@test
def test_iris_quality(output, *args):
    assert not output.isna().any().any()
    assert output["target"].nunique() == 3
