from time import sleep

from dash.testing.composite import DashComposite

from wazp.app import app


def test_load_config_once(dash_duo: DashComposite, helpers) -> None:
    """
    ...

    Parameters:
        dash_duo: Default fixture for Dash Python integration tests.
    """
    dash_duo.start_server(app)

    #
    dash_duo.wait_for_text_to_equal("h1", "Home", timeout=4)
    helpers.debug_screenshot(dash_duo)
    upload_area = dash_duo.find_elements(
        "Select project config file", attribute="PARTIAL_LINK_TEXT"
    )
    assert len(upload_area) == 1, "Couldn't find the upload button."
    upload_area = upload_area[0]
    upload_area.click()
    # upload_area = "upload-project-config
    dash_duo.multiple_click(upload_area, 1)
