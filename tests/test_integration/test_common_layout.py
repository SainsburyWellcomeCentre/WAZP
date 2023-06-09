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

    Parameters
    ----------
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


unloaded_config_xfail = pytest.mark.xfail(
    raises=AssertionError,
    reason=(
        "Feature not yet implemented:"
        "When config has not been loaded, "
        "warnings should show in pages that are not Home"
    ),
    strict=False,
    # with strict=True
    # if the test passes unexpectedly,
    # it will fail the test suite
)


# Q for review: is there a way to have this with
# one fixture only?
# https://docs.pytest.org/en/latest/how-to/skipping.html#skip-xfail-with-parametrize
@pytest.mark.parametrize(
    ("page_name_and_title"),
    [
        pytest.param(fx, marks=mark)
        for fx, mark in [
            ("home_page_name_and_title", []),
            ("metadata_page_name_and_title", unloaded_config_xfail),
            ("roi_page_name_and_title", unloaded_config_xfail),
            ("pose_estimation_page_name_and_title", []),
            ("dashboard_page_name_and_title", unloaded_config_xfail),
        ]
    ],
)
def test_sidebar_links(
    dash_duo: DashComposite,
    page_name_and_title: tuple[str],
    timeout: float,
    request: pytest.FixtureRequest,
) -> None:
    """Check the sidebar links take to the corresponding pages
    and that no errors occur in the browser console

    The pages are checked via their title.

    Parameters
    ----------
    dash_duo : DashComposite
        Default fixture for Dash Python integration tests.
    page_name_and_title : tuple[str]
        name of the page in the dash registry and the main title shown on
        the page
    timeout : float
        maximum time to wait in seconds for a component
    request : pytest.FixtureRequest
        a special fixture providing information of the requesting test
        function. See [1]_

    References
    ----------
    .. [1] https://docs.pytest.org/en/6.2.x/reference.html#std-fixture-request
    """

    # get fixture value
    (page_name, page_title) = request.getfixturevalue(page_name_and_title)

    # start server
    dash_duo.start_server(app)

    # click sidebar link
    dash_duo.find_element(
        "#sidebar #link-" + page_name.replace(" ", "-"),
    ).click()

    # check page title is expected
    try:
        dash_duo.wait_for_text_to_equal("h1", page_title, timeout=timeout)

    except selenium.common.exceptions.TimeoutException:
        pytest.fail(
            f"Timeout waiting for page {page_name} "
            "to show a title with the text: "
            f"{page_title}"
        )

    dash_duo.find_element("#sidebar #link-Home").click()
    # TODO: if no config file has been loaded, check a warning is shown?
    # ...

    # NOTE: this is expected to fail for a few pages (hence the marked xfails)
    assert (
        dash_duo.get_logs() == []
    ), "There are errors in the browser console!"
