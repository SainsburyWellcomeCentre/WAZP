from pathlib import Path

import pytest
from dash.testing.composite import DashComposite
from selenium.webdriver.chrome.options import Options


class Helpers:
    """A class to group helpful things when writing tests.

    Added as a pytest fixture.

    Example
    -------
    ```
    def test_my_thing(helpers)
        helpers.debug_screenshot()
    ```
    """

    @staticmethod
    def debug_screenshot(dash_duo: DashComposite, subdir: str = "") -> None:
        """Save a screenshot of the current state of the testing server.

        Useful for debugging and developing tests.
        Saves to .test_debug_screenshots or
        .test_debug_screenshots/<subdir> if `subdir` is provided.

        Parameters
        ----------
            dash_duo : DashComposite
                The current dash_duo fixture.
            subdir: str, optional
                A subdirectory name (to help you find the screenshots.)
        """
        screenshots_dirname = Path(".test_helper_screenshots")
        if subdir:
            screenshots_dirname /= subdir
        screenshots_dirname.mkdir(exist_ok=True)  # mkdir -p
        filename = screenshots_dirname / f"test-{dash_duo.session_id}.png"
        dash_duo.driver.save_screenshot(filename.as_posix())


@pytest.fixture
def helpers():
    return Helpers


def pytest_setup_options():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    return options


@pytest.fixture
def home_page_name_and_title():
    return ("Home", "Home")


@pytest.fixture
def metadata_page_name_and_title():
    return ("01 metadata", "Metadata")


@pytest.fixture
def roi_page_name_and_title():
    return ("02 roi", "ROI definition")


@pytest.fixture
def pose_estimation_page_name_and_title():
    return ("03 pose estimation", "Pose estimation inference")


@pytest.fixture
def dashboard_page_name_and_title():
    return ("04 dashboard", "Dashboard & data export")


@pytest.fixture
def timeout() -> float:
    """Maximum time to wait for a component
    to be located in layout

    Returns
    -------
    timeout : float
        maximum time to wait in seconds
    """
    return 4
