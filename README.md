# fava_summary_only

A [Fava](https://beancount.github.io/fava/) extension that enforces
**summary-only mode**: high-level accounting reports remain accessible, but
transaction-level details, per-account drilldowns, and all editing features
are hidden and blocked.

This is useful when you want to share summary level accounting information
with people, but don't want them to see individual transactions.

---

## What it does

### Hidden from the sidebar (CSS + JS)

| Item | Fava URL |
|---|---|
| Income Statement | `/income_statement` |
| Journal | `/journal` |
| Query | `/query` |
| Documents | `/documents` |
| Editor | `/editor` |
| Import | `/import` |
| Options | `/options` |
| "Go to account" input | *(sidebar widget)* |

### Account detail links

On reports like the Balance Sheet and Trial Balance, every account name is
normally a clickable link to that account's transaction journal (e.g.
`/my-ledger/account/Assets:Bank:Checking/`).  In summary-only mode:

- Those links are rendered as **plain, non-clickable text** (via CSS
  `pointer-events: none`).
- Clicking them (or keyboard-activating them) is **intercepted and cancelled**
  by a JavaScript event listener.
- Navigating to any `/account/…` URL directly returns **HTTP 403 Forbidden**
  (enforced server-side by the `before_request` hook).

### Reports that remain fully functional

- Balance Sheet
- Trial Balance
- Commodities / Prices
- Events
- Statistics

---

## Installation

### Option A — install as a package (recommended)

```bash
pip install -e /path/to/fava_summary_only
```

Or, once published to PyPI:

```bash
pip install fava-summary-only
```

### Option B — drop the folder on your Python path

Copy the `fava_summary_only/` directory to any directory that is already on
`PYTHONPATH`, or to the same directory as your `.beancount` file and launch
Fava from there.

---

## Usage

Add **one line** to your `.beancount` file:

```beancount
2000-01-01 custom "fava-extension" "fava_summary_only" "{}"
```

Then restart Fava.  That's all.

---

## How it works (technical details)

Fava's extension API (`FavaExtensionBase`) provides two hooks used here:

| Hook | Purpose |
|---|---|
| `before_request()` | Called by Fava before every HTTP request. Used to `abort(403)` for any `/account/` URL. |
| `has_js_module = True` | Tells Fava to serve `templates/module.js` as a JavaScript ES module on every page. |

The JS module (`module.js`):

1. Injects a `<style>` tag with CSS that hides the forbidden sidebar items
   and sets `pointer-events: none` on account links.
2. Registers a capturing `click` listener that cancels any click on an
   `/account/` link that the CSS might not have caught (e.g. keyboard
   navigation).
3. Patches `history.pushState` / `history.replaceState` to prevent Fava's
   Svelte client-side router from navigating to account pages.

The `report_title = "Summary Only"` attribute adds an informational sidebar
entry.  You can remove it by setting `report_title = None` in the source if
you prefer a clean sidebar.

---

## Compatibility

Tested against Fava ≥ 1.26 (Python 3.10+, Svelte 5 frontend).

The `before_request()` hook and `has_js_module` are stable parts of the
Fava extension API.  The CSS selectors target Fava's compiled Svelte output;
if Fava significantly restructures its DOM in a future release the selectors
may need updating.

---

## License

MIT
