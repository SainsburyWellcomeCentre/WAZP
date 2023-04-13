from dash.testing.composite import DashComposite
import pytest
from wazp.app import app


@pytest.mark.skip(
    reason="don't commit this but skip locally for sam's chromedriver problems"
)
def test_start_server_no_errors(dash_duo: DashComposite) -> None:
    """A minimal smoke test: launching the wazp webapp should startup, and
    display the page content without error.

    Parameters:
        dash_duo: Default fixture for Dash Python integration tests.
    """
    dash_duo.start_server(app)
    dash_duo.wait_for_text_to_equal("h1", "Home", timeout=4)
    assert (
        dash_duo.get_logs() == []
    ), "There are errors in the browser console!"
