import numpy as np
import pandas as pd
import pytest
from utils.calibration import _validate_quotes, mse


def quotes():
    return pd.DataFrame({"Strike": [95.0, 100.0], "Price": [7.0, 4.0], "Type": ["C", "P"]})


def test_quote_validation_rejects_empty_data():
    with pytest.raises(ValueError, match="No option quotes"):
        _validate_quotes(quotes().iloc[:0])


def test_quote_validation_rejects_invalid_option_type():
    df = quotes()
    df.loc[0, "Type"] = "X"
    with pytest.raises(ValueError, match="Type values"):
        _validate_quotes(df)


def test_quote_validation_rejects_non_finite_prices():
    df = quotes()
    df.loc[0, "Price"] = np.nan
    with pytest.raises(ValueError, match="finite"):
        _validate_quotes(df)


def test_reported_mse_is_unpenalized_price_error():
    # With a tiny vol-of-vol, this parameter set satisfies Feller; the public
    # mse function reports only the observable market-price fitting error.
    from utils.lewis import model_price
    df = quotes()
    p = (0.04, 1.0, 0.04, 0.01, 0.0)
    predicted = model_price(100.0, df["Strike"].to_numpy(), 0.25, 0.02, 0.0,
                            p, df["Type"].to_numpy())
    expected = np.mean((predicted - df["Price"].to_numpy()) ** 2)
    assert mse(p, df, 100.0, 0.02, 0.0, 0.25) == pytest.approx(expected)
