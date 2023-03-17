"""Trivial smoke tests of import functionality.

Checks the package layout is OK, minimal checks that wazp.app.app is an app and
has been constructed.  """
import dash


def test_import_wazp() -> None:
    """Test that we can import wazp (verifies the __init__.py etc)."""
    import wazp

    print(dir(wazp))
    # assert wazp.__doc__ != "", "WAZP has no help!"


def test_valid_app() -> None:
    """Test that wazp.app.app is the correct object."""
    from wazp.app import app

    assert isinstance(app, dash.Dash), "WAZP app is invalid."
    assert app.callback_map != {}, "WAZP has no callbacks."
