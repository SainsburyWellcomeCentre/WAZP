import dash
import pytest
import selenium
from dash.testing.composite import DashComposite

from wazp.app import app


@pytest.fixture
def map_page_name_to_title():
    """Map page names to page head titles

    Returns
    -------
    dict
        dictionary with page names as keys, and page titles as values
    """
    return {
        "Home": "Home",
        "01 metadata": "Metadata",
        "02 roi": "ROI definition",
        "03 pose estimation": "Pose estimation inference",
        "04 dashboard": "Dashboard & data export",
    }


@pytest.fixture()
def timeout():
    """Maximum time to wait for a component
    to be located in layout

    Returns
    -------
    timeout : float
        maximum time to wait in seconds
    """
    return 4  # Q for review: is this overkill?


def test_components_created(
    dash_duo: DashComposite,
    timeout: float,
) -> None:
    """Check that the components common to all pages are created.

    The components common to all pages are the page content container and
    the sidebar.

    Parameters:
        dash_duo : DashComposite
            Default fixture for Dash Python integration tests.
        timeout : float
            maximum time to wait in seconds for a component
    """

    # start server
    dash_duo.start_server(app)

    # wait for main content to be rendered
    try:
        dash_duo.wait_for_element("#page-content", timeout=timeout)
    except selenium.common.exceptions.TimeoutException:
        pytest.fail("Main content component not generated")

    # wait for sidebar to be rendered
    try:
        dash_duo.wait_for_text_to_equal(
            "#sidebar h2", "WAZP 🐝", timeout=timeout
        )
    except selenium.common.exceptions.TimeoutException:
        pytest.fail("Sidebar component not generated")

    # check there are no errors in browser console
    assert (
        dash_duo.get_logs() == []
    ), "There are errors in the browser console!"


@pytest.mark.xfail(
    raises=AssertionError,
    reason=(
        "Feature not yet implemented:"
        "When config has not been loaded, "
        "warnings should show in pages that are not Home"
    ),
    strict=True,
    # with strict=True
    # if the test passes unexpectedly,
    # it will fail the test suite
)
def test_sidebar_links(
    dash_duo: DashComposite,
    map_page_name_to_title: dict,
    timeout: float,
) -> None:
    """Check the sidebar links take to pages with the expected title
    and that no errors occur in the browser console

    Parameters:
        dash_duo : DashComposite
            Default fixture for Dash Python integration tests.
        map_page_name_to_title: dictionary : dict
            dictionary with page names as keys, and page titles as values
        timeout : float
            maximum time to wait in seconds for a component
    """

    # start server
    dash_duo.start_server(app)

    # click through links in sidebar
    for page in dash.page_registry.values():

        # click thru each page
        dash_duo.find_element(
            "#sidebar #link-" + page["name"].replace(" ", "-"),
        ).click()

        # check page title
        try:
            dash_duo.wait_for_text_to_equal(
                "h1", map_page_name_to_title[page["name"]], timeout=timeout
            )

        except selenium.common.exceptions.TimeoutException:
            pytest.fail(
                f'Timeout waiting for page {page["name"]} '
                "to show a title with the text: "
                f'{map_page_name_to_title[page["name"]]}'
            )

        # click back to home
        # Q for review: I do this to make the starting point consistent...
        # but is it required? should I use fixtures instead?
        dash_duo.find_element("#sidebar #link-Home").click()

        # TODO: if no config file has been loaded, check a warning is shown?
        # ...

    # NOTE: this is expected to fail
    assert (
        dash_duo.get_logs() == []
    ), "There are errors in the browser console!"
