from dash.testing.composite import DashComposite

from wazp.app import app


def test_load_config_once(dash_duo: DashComposite) -> None:
    """
    ...

    Parameters:
        dash_duo: Default fixture for Dash Python integration tests.
    """
    dash_duo.start_server(app)
    dash_duo.wait_for_text_to_equal("h1", "Home", timeout=4)
    assert (
        dash_duo.get_logs() == []
    ), "There are errors in the browser console!"
