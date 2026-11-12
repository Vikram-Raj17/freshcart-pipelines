try:
    from mage_ai.data_preparation.decorators import transformer, test
except ImportError:  # Allows unit tests to run outside a Mage installation.
    def transformer(func):
        return func
    def test(func):
        return func

from sklearn.model_selection import train_test_split

TEST_SIZE = 0.2
RANDOM_STATE = 42


@transformer
def transform(df, *args, **kwargs):
    """Add a reproducible 80/20 train/test label without changing source rows."""
    if "target" not in df.columns:
        raise ValueError("Input DataFrame must contain a 'target' column")

    out = df.copy()
    train_idx, test_idx = train_test_split(
        out.index,
        test_size=TEST_SIZE,
        random_state=RANDOM_STATE,
        stratify=out["target"],
    )
    out["split"] = "train"
    out.loc[test_idx, "split"] = "test"
    return out


@test
def test_split_counts(output, *args):
    assert (output["split"] == "train").sum() == 120
    assert (output["split"] == "test").sum() == 30
