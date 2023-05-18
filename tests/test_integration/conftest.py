import pytest
from selenium.webdriver.chrome.options import Options


def pytest_setup_options():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    return options


# @pytest.fixture
# def map_page_name_to_title() -> dict:
#     """Map page names to page head titles

#     Returns
#     -------
#     dict
#         dictionary with page names as keys, and page titles as values
#     """
#     return {
#         "Home": "Home",
#         "01 metadata": "Metadata",
#         "02 roi": "ROI definition",
#         "03 pose estimation": "Pose estimation inference",
#         "04 dashboard": "Dashboard & data export",
#     }


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
