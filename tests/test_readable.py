import pandas as pd
import pytest

from hct_equity import readable
from hct_equity.config import load_labels

LABELS = load_labels()


def test_every_format_kind_has_a_formatter():
    assert set(LABELS.formats.values()) <= set(readable.FORMATTERS)


@pytest.mark.parametrize(
    ("kind", "value", "text"),
    [
        ("percent", 0.274, "27%"),
        ("percent_one_decimal", 0.6192, "61.9%"),
        ("percent_value", 58.7, "59%"),
        ("points", 0.088, "+8.8 points"),
        ("points", -0.061, "−6.1 points"),
        ("count", 6687, "6,687"),
        ("one_decimal", 9.79, "9.8"),
        ("three_decimals", 0.6481, "0.648"),
        ("signed_three_decimals", 0.0081, "+0.008"),
    ],
)
def test_formatters_write_plain_numbers(kind, value, text):
    assert readable.FORMATTERS[kind](value) == text


def test_combined_index_reads_as_patient_groups():
    table = pd.DataFrame(
        {"ric": [0.18, 0.82]}, index=pd.MultiIndex.from_tuples([(0, 1), (1, 0)], names=["frail", "severe"])
    )
    index = readable.relabel_index(table.index, LABELS)
    assert list(index) == ["Fit, severe", "Frail, not severe"]
    assert index.name == LABELS.combined_index_name


def test_unstacked_values_become_column_labels():
    columns = pd.Index([0, 1], name="severe")
    assert list(readable.relabel_columns(columns, LABELS)) == ["Not severe", "Severe"]


def test_threshold_columns_use_the_template():
    columns = pd.Index([0.2, 0.4], name="threshold")
    assert list(readable.relabel_columns(columns, LABELS)) == ["Threshold 20%", "Threshold 40%"]


def test_readable_table_has_no_codes():
    table = pd.DataFrame({"ric": [0.18], "risk_mac": [0.274]}, index=pd.Index([0], name="frail"))
    html = readable.readable(table, LABELS).to_html()
    assert "Got RIC" in html
    assert "27%" in html
    assert "Fit" in html
    assert "risk_mac" not in html


def test_series_is_shown_as_a_one_column_table():
    series = pd.Series([0.474, 0.413], index=pd.Index([0, 1], name="ric"), name="event_rate")
    html = readable.readable(series, LABELS).to_html()
    assert "MAC" in html
    assert "47%" in html


def test_cell_format_overrides_column_formats():
    table = pd.DataFrame({0: [6687], 1: [3610]}, index=pd.Index([0], name="ric")).rename_axis(columns="severe")
    html = readable.readable(table, LABELS, cell_format="count").to_html()
    assert "6,687" in html


def test_lower_first_keeps_acronyms():
    assert readable.lower_first("Not severe") == "not severe"
    assert readable.lower_first("RIC") == "RIC"
