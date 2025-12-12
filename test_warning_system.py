import numpy as np
import calcs


def test_empty_input():
    data = np.array([], dtype=float)

    labels, upper, lower = calcs.calculations(
        data=data,
        lookback_period=14,
        std_multiplier=2,
    )

    assert len(labels) == 0


def test_missing_values():
    raw = np.array([1.0, np.nan, 2.0, 3.0], dtype=float).reshape(-1, 1)

    cleaned, removed = calcs.clean_data(raw)

    assert cleaned.shape[0] <= raw.shape[0]
    assert not np.isnan(cleaned).any()


def test_sensitivity_parameter():
    data = np.array([10, 10, 10, 50, 10, 10], dtype=float)

    out_strict, _, _ = calcs.calculations(
        data=data,
        lookback_period=3,
        std_multiplier=2,
    )
    out_loose, _, _ = calcs.calculations(
        data=data,
        lookback_period=3,
        std_multiplier=10,
    )

    strict_count = np.sum(out_strict != 0)
    loose_count = np.sum(out_loose != 0)

    assert strict_count >= 1
    assert loose_count <= strict_count
