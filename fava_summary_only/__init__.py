"""
fava_summary_only
=================
A Fava extension that enforces "summary-only" mode:

  * Hides transaction-level and editing nav items from the sidebar
    (Income Statement, Journal, Query, Documents, Editor, Import, Options,
    and the "Go to account" search input).
  * Removes clickable links on account names in tree reports
    (Balance Sheet, Trial Balance, etc.).
  * Blocks direct navigation to per-account pages (/account/...) with a
    friendly 403 response, even if a user types the URL manually.

How it works
------------
* ``before_request()`` — a native Fava extension hook called on every
  request — checks the URL and aborts with 403 for /account/ paths.
* The extension sets ``has_js_module = True`` and ships a ``Module.svelte``
  (or plain ``module.js``) file that Fava loads as a JavaScript module on
  every page.  That module injects the necessary <style> block and sets up
  a click-interceptor so account links are inert.
* A Jinja2 template (``fava_summary_only.html``) is provided for the
  optional sidebar "Summary Only" info page.

Installation
------------
1. Place the ``fava_summary_only/`` directory somewhere on your PYTHONPATH,
   or install it:

       pip install -e /path/to/fava_summary_only

2. Add the extension directive to your ``.beancount`` file::

       2000-01-01 custom "fava-extension" "fava_summary_only" "{}"

3. Restart Fava.

What is blocked / hidden
-------------------------
Sidebar items hidden (CSS + JS):
  - Income Statement  (/income_statement)
  - Journal           (/journal)
  - Query             (/query)
  - Documents         (/documents)
  - Editor            (/editor)
  - Import            (/import)
  - Options           (/options)
  - "Go to account" account-input widget

Account detail links:
  - All <a href=".../.../account/..."> anchors become non-clickable
  - Navigating to /account/... directly returns HTTP 403
"""

from __future__ import annotations

from flask import abort, request
from fava.ext import FavaExtensionBase


# ---------------------------------------------------------------------------
# CSS injected into every page via the JS module.
# Hiding is done with CSS selectors on Fava's rendered HTML.
# We target both the href pattern and the li that contains the link so that
# the list item's spacing is also removed.
# ---------------------------------------------------------------------------
_SUMMARY_ONLY_CSS = """
/* === fava_summary_only: hide forbidden sidebar nav items === */

/* Income Statement */
a[href*="/income_statement"] { display: none !important; }
li:has(> a[href*="/income_statement"]) { display: none !important; }

/* Journal */
a[href*="/journal"] { display: none !important; }
li:has(> a[href*="/journal"]) { display: none !important; }

/* Query */
a[href*="/query"] { display: none !important; }
li:has(> a[href*="/query"]) { display: none !important; }

/* Documents */
a[href*="/documents"] { display: none !important; }
li:has(> a[href*="/documents"]) { display: none !important; }

/* Editor / Source */
a[href*="/editor"] { display: none !important; }
li:has(> a[href*="/editor"]) { display: none !important; }

/* Import */
a[href*="/import"] { display: none !important; }
li:has(> a[href*="/import"]) { display: none !important; }

/* Options */
a[href*="/options"] { display: none !important; }
li:has(> a[href*="/options"]) { display: none !important; }

/* "Go to account" input — Fava renders this as a custom element or
   a labelled <input> near the sidebar top. */
fava-account-input,
.account-link-form,
[data-account-link],
aside input[type="text"],
aside label:has(input),
nav input[placeholder*="account" i],
nav label:has(input[placeholder*="account" i]) {
    display: none !important;
}

/* === fava_summary_only: make account links non-navigable === */
/* Account links in tree reports (Balance Sheet, Trial Balance, etc.)
   link to e.g. /ledger/account/Assets:Bank/.  We make them look like
   plain text so the UI is not confusing. */
a[href*="/account/"] {
    pointer-events: none !important;
    cursor: default     !important;
    text-decoration: none !important;
    color: inherit      !important;
}
"""


class SummaryOnlyExtension(FavaExtensionBase):
    """Enforce summary-only mode — no transaction-level or editing access."""

    # Set a report_title to get a sidebar entry that shows an info page.
    # Users can remove this if they don't want the extra sidebar link.
    report_title: str | None = "Summary Only"

    # Tell Fava to load our JS module (Module.svelte or module.js) on every
    # page.  The module injects CSS and sets up the click interceptor.
    has_js_module: bool = True

    # ------------------------------------------------------------------ #
    #  Fava hook: called before every HTTP request to this ledger          #
    # ------------------------------------------------------------------ #

    def before_request(self) -> None:
        """Block /account/ URLs before any response is generated."""
        if "/account/" in request.path:
            abort(
                403,
                description=(
                    "Account detail pages are not available in summary-only "
                    "mode.  Only summary-level reports are accessible."
                ),
            )
