import matplotlib

matplotlib.use("Agg")

from hct_equity import fairness, fairness_plots  # noqa: E402
from hct_equity.config import load_config  # noqa: E402
from tests.test_fairness import COLUMNS, scored_frame  # noqa: E402

NOTE = "Synthetic test note"
STYLE = load_config().fairness.plot


def test_calibration_plot_has_one_line_per_group_and_a_diagonal():
    deciles = fairness.calibration_by_decile(scored_frame(), COLUMNS, 12, 5)
    fig = fairness_plots.plot_calibration(deciles, COLUMNS, STYLE, NOTE)
    assert len(fig.axes[0].lines) == 3
    assert NOTE in fig.axes[0].get_title()


def test_dca_plot_has_one_panel_per_group():
    dca = fairness.dca_by_group(scored_frame(), COLUMNS, 12, [0.2, 0.4, 0.6])
    fig = fairness_plots.plot_dca_by_group(dca, COLUMNS, STYLE, NOTE)
    titled = [ax for ax in fig.axes if ax.get_visible()]
    assert [ax.get_title() for ax in titled] == ["A", "B"]
    assert NOTE in fig.get_suptitle()
