import os

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
        helpers.help_me()
    ```
    """

    @staticmethod
    def debug_screenshot(dash_duo: DashComposite, name: str = "") -> None:
        """Save a screenshot of the current state of the testing server.

        Useful for debugging and developing tests.
        Saves to .test_debug_screenshots or
        .test_debug_screenshots/<name> if `name` is provided.

        Parameters
        ----------
            dash_duo : DashComposite
                The current dash_duo fixture.
            name: str, optional
                A name (to help you find the screenshots.)
        """
        screenshots_dirname = ".test_helper_screenshots/"
        if name:
            screenshots_dirname += f"{name}/"
        os.makedirs(screenshots_dirname, exist_ok=True)  # mkdir -p
        filename = f"test-{dash_duo.session_id}.png"
        dash_duo.driver.save_screenshot(f"./{screenshots_dirname}/{filename}")


@pytest.fixture
def helpers():
    return Helpers


def pytest_setup_options():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    return options
