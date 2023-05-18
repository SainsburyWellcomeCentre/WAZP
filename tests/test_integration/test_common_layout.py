import pytest
import selenium
from dash.testing.composite import DashComposite

from wazp.app import app


def test_components_created(
    dash_duo: DashComposite,
    timeout: float,
) -> None:
    """Check that the components that are common to all pages are created.

    The components common to all pages are:
    - the page content container, and
    - the sidebar.

    Parameters:
        dash_duo : DashComposite
            Default fixture for Dash Python integration tests.
        timeout : float
            maximum time to wait in seconds for a component
    """

    # start server
    dash_duo.start_server(app)

    # wait for main content container to be rendered
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
    ), f"There are {len(dash_duo.get_logs())} errors"
    " in the browser console!"


# @pytest.mark.xfail(
#     raises=AssertionError,
#     reason=(
#         "Feature not yet implemented:"
#         "When config has not been loaded, "
#         "warnings should show in pages that are not Home"
#     ),
#     strict=True,
#     # with strict=True
#     # if the test passes unexpectedly,
#     # it will fail the test suite
# )
@pytest.mark.parametrize(
    "page_name",
    [
        pytest.param(
            name,
            marks=pytest.mark.xfail(
                reason=(
                    "Feature not yet implemented:"
                    "When config has not been loaded, "
                    "warnings should show in pages that are not Home"
                )
            ),
        )
        for name in [
            "Home",
            "01 metadata",
            "02 roi",
            "03 pose estimation",
            "04 dashboard",
        ]
    ],
)
def test_sidebar_links(
    dash_duo: DashComposite,
    page_name: str,
    map_page_name_to_title: dict,
    timeout: float,
) -> None:
    """Check the sidebar links take to pages with the expected title
    and that no errors occur in the browser console

    Parameters:
        dash_duo : DashComposite
            Default fixture for Dash Python integration tests.
        page : str
            ....
        map_page_name_to_title: dictionary : dict
            dictionary with page names as keys, and page titles as values
        timeout : float
            maximum time to wait in seconds for a component
    """

    # start server
    dash_duo.start_server(app)

    # click through links in sidebar
    # for page in dash.page_registry.values():

    # click thru each page
    dash_duo.find_element(
        "#sidebar #link-" + page_name.replace(" ", "-"),
    ).click()

    # check page title
    try:
        dash_duo.wait_for_text_to_equal(
            "h1", map_page_name_to_title[page_name], timeout=timeout
        )

    except selenium.common.exceptions.TimeoutException:
        pytest.fail(
            f"Timeout waiting for page {page_name} "
            "to show a title with the text: "
            f"{map_page_name_to_title[page_name]}"
        )

    # TODO: if no config file has been loaded, check a warning is shown?
    # ...

    # NOTE: this is expected to fail
    assert (
        dash_duo.get_logs() == []
    ), "There are errors in the browser console!"
