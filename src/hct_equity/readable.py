"""Human-readable notebook tables: plain labels, no 0/1 codes, numbers formatted for reading."""

from collections.abc import Callable, Hashable

import pandas as pd
from pandas.io.formats.style import Styler

from hct_equity.config import FormatKind, Labels

MINUS = "−"


def percent(value: float) -> str:
    return f"{value:.0%}"


def percent_one_decimal(value: float) -> str:
    return f"{value:.1%}"


def percent_value(value: float) -> str:
    return f"{value:.0f}%"


def points(value: float) -> str:
    return f"{100 * value:+.1f} points".replace("-", MINUS)


def count(value: float) -> str:
    return f"{value:,.0f}"


def one_decimal(value: float) -> str:
    return f"{value:.1f}"


def two_decimals(value: float) -> str:
    return f"{value:.2f}"


def three_decimals(value: float) -> str:
    return f"{value:.3f}"


def signed_three_decimals(value: float) -> str:
    return f"{value:+.3f}".replace("-", MINUS)


FORMATTERS: dict[FormatKind, Callable[[float], str]] = {
    "percent": percent,
    "percent_one_decimal": percent_one_decimal,
    "percent_value": percent_value,
    "points": points,
    "count": count,
    "one_decimal": one_decimal,
    "two_decimals": two_decimals,
    "three_decimals": three_decimals,
    "signed_three_decimals": signed_three_decimals,
}


def value_label(labels: Labels, level: str | None, value: Hashable) -> str:
    return labels.values.get(level or "", {}).get(str(value), str(value))


def lower_first(text: str) -> str:
    """Lowercases a leading capital in a word, but keeps acronyms such as RIC."""
    return text[:1].lower() + text[1:] if text[1:2].islower() else text


def row_label(labels: Labels, names: list[str | None], key: Hashable) -> str:
    """Joins the levels of one row key, e.g. (0, 1) -> "Fit, severe"."""
    parts = key if isinstance(key, tuple) else (key,)
    words = [value_label(labels, name, part) for name, part in zip(names, parts, strict=True)]
    return ", ".join([words[0], *map(lower_first, words[1:])])


def relabel_index(index: pd.Index, labels: Labels) -> pd.Index:
    names = list(index.names)
    name = labels.combined_index_name if len(names) > 1 else labels.index_names.get(names[0] or "", names[0])
    return pd.Index([row_label(labels, names, key) for key in index], name=name)


def relabel_columns(columns: pd.Index, labels: Labels) -> pd.Index:
    template = labels.column_templates.get(columns.name or "")
    if template:
        return pd.Index([template.format(value=value) for value in columns])
    if columns.name in labels.values:
        return pd.Index([value_label(labels, columns.name, value) for value in columns])
    return pd.Index([labels.columns.get(str(column), str(column)) for column in columns])


def column_formatters(columns: pd.Index, labels: Labels, cell_format: FormatKind | None) -> list[Callable | None]:
    kinds = [cell_format or labels.formats.get(str(column)) for column in columns]
    return [FORMATTERS[kind] if kind else None for kind in kinds]


def readable(table: pd.DataFrame | pd.Series, labels: Labels, cell_format: FormatKind | None = None) -> Styler:
    """Relabels rows and columns from config/labels.json and formats each number for reading."""
    frame = table.to_frame() if isinstance(table, pd.Series) else table
    formatters = column_formatters(frame.columns, labels, cell_format)
    shown = frame.set_axis(relabel_index(frame.index, labels), axis=0)
    shown = shown.set_axis(relabel_columns(frame.columns, labels), axis=1)
    styler = shown.style
    for column, formatter in zip(shown.columns, formatters, strict=True):
        styler = styler.format(formatter, subset=[column]) if formatter else styler
    return styler
