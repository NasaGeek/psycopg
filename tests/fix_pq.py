import re
import operator
import pytest


def pytest_report_header(config):
    try:
        from psycopg3 import pq

        return [
            f"libpq available: {pq.version()}",
            f"libpq wrapper implementation: {pq.__impl__}",
        ]
    except Exception:
        # you will die of something else
        pass


def pytest_configure(config):
    # register libpq marker
    config.addinivalue_line(
        "markers",
        "libpq(version_expr): run the test only with matching libpq"
        " (e.g. '>= 10', '< 9.6')",
    )


@pytest.fixture
def pq(request):
    """The libpq module wrapper to test."""
    from psycopg3 import pq

    for m in request.node.iter_markers(name="libpq"):
        check_libpq_version(pq.version(), m.args)

    return pq


def check_libpq_version(got, want):
    """
    Verify if the libpq version is a version accepted.

    This function is called on the tests marked with something like::

        @pytest.mark.libpq(">= 12")

    and skips the test if the requested version doesn't match what's loaded.

    """
    # convert 90603 to (9, 6, 3), 120003 to (12, 0, 3)
    got, got_fix = divmod(got, 100)
    got_maj, got_min = divmod(got, 100)
    if got_maj >= 10:
        got = (got_maj, got_fix)
    else:
        got = (got_maj, got_min, got_fix)

    # Parse a spec like "> 9.6"
    if len(want) != 1:
        pytest.fail("libpq marker doesn't specify a version")
    want = want[0]
    m = re.match(
        r"^\s*(>=|<=|>|<)\s*(?:(\d+)(?:\.(\d+)(?:\.(\d+))?)?)?\s*$", want
    )
    if m is None:
        pytest.fail(f"bad libpq spec: {want}")

    # convert "9.6" into (9, 6, 0), "10.3" into (10, 0, 3)
    want_maj = int(m.group(2))
    want_min = int(m.group(3) or "0")
    want_fix = int(m.group(4) or "0")
    if want_maj >= 10:
        if want_fix:
            pytest.fail(f"bad libpq version in {want}")
        want = (want_maj, want_min)
    else:
        want = (want_maj, want_min, want_fix)

    op = getattr(
        operator, {">=": "ge", "<=": "le", ">": "gt", "<": "lt"}[m.group(1)]
    )

    if not op(got, want):
        revops = {">=": "<", "<=": ">", ">": "<=", "<": ">="}
        pytest.skip(
            f"skipping test: libpq loaded is {'.'.join(map(str, got))}"
            f" {revops[m.group(1)]} {'.'.join(map(str, want))}"
        )