from hct_equity.config import CONFIG_PATH, load_config

README_PATH = CONFIG_PATH.parents[1] / "README.md"


def test_readme_states_synthetic_note():
    assert load_config().synthetic_note in README_PATH.read_text()


def test_readme_states_citation():
    assert load_config().citation in README_PATH.read_text()
