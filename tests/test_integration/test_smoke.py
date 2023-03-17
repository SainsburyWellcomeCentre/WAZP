"""Smoke tests which start the server and check we can navigate pages."""
import os

import pytest
from dash.testing.composite import DashComposite

from wazp.app import app


@pytest.mark.parametrize(
    "page, title",
    [
        ("", "Home"),
        ("/01-metadata", "Metadata"),
        ("/02-roi", "ROI definition"),
        ("/03-pose-estimation", "Pose estimation inference"),
        ("/04-dashboard", "Dashboard"),
    ],
)
def test_start_server_open_page_no_errors(
    dash_duo: DashComposite, page: str, title: str
) -> None:
    dash_duo.start_server(app)
    if page:
        dash_duo.wait_for_page(dash_duo.server_url + page, timeout=4)
    dash_duo.wait_for_text_to_equal("h1", title, timeout=4)

    errors = dash_duo.get_logs()
    if errors:
        screenshots_dirname = ".test_fail_screenshots/smoke"
        os.makedirs(screenshots_dirname, exist_ok=True)  # mkdir -p
        filename = f"test-{dash_duo.session_id}{page.replace('/', '-')}.png"
        dash_duo.driver.save_screenshot(f"./{screenshots_dirname}/{filename}")
        assert False, f"There are {len(errors)} errors in the browser console!"
