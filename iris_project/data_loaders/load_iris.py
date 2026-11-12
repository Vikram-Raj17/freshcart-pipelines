try:
    from mage_ai.data_preparation.decorators import data_loader, test
except ImportError:  # Allows unit tests to run outside a Mage installation.
    def data_loader(func):
        return func
    def test(func):
        return func

from sklearn.datasets import load_iris


@data_loader
def load_iris_data(*args, **kwargs):
    """Return the Iris feature columns and target as a single DataFrame."""
    return load_iris(as_frame=True).frame


@test
def test_iris_loaded(output, *args):
    assert output is not None
    assert len(output) == 150
    assert "target" in output.columns
