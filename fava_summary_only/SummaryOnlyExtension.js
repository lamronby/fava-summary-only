/**
 * fava_summary_only — client-side enforcement
 *
 * Fava loads this file as a JavaScript module (ES module) on every page
 * when the extension sets `has_js_module = True`.  It is loaded after the
 * Fava app boots, so we can safely query and mutate the DOM.
 *
 * This module does two things:
 *  1. Injects the summary-only CSS (hiding forbidden nav items and making
 *     account links non-clickable).
 *  2. Intercepts any residual click or keyboard navigation to /account/ URLs
 *     in case the CSS pointer-events suppression is insufficient (e.g. for
 *     keyboard users or programmatic navigation triggered by Fava's Svelte
 *     router).
 */

/* ── 1. Inject CSS ──────────────────────────────────────────────────────── */

const css = `
/* === fava_summary_only: hide forbidden sidebar nav items === */

a[href*="/income_statement"],
li:has(> a[href*="/income_statement"]) { display: none !important; }

a[href*="/journal"],
li:has(> a[href*="/journal"]) { display: none !important; }

a[href*="/query"],
li:has(> a[href*="/query"]) { display: none !important; }

a[href*="/documents"],
li:has(> a[href*="/documents"]) { display: none !important; }

a[href*="/editor"],
li:has(> a[href*="/editor"]) { display: none !important; }

a[href*="/import"],
li:has(> a[href*="/import"]) { display: none !important; }

a[href*="/options"],
li:has(> a[href*="/options"]) { display: none !important; }

/* "Go to account" input widget */
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
a[href*="/account/"] {
    pointer-events: none !important;
    cursor:         default !important;
    text-decoration: none !important;
    color:          inherit !important;
}
`;

const style = document.createElement("style");
style.id = "fava-summary-only-css";
style.textContent = css;
document.head.appendChild(style);

/* ── 2. Intercept account navigation ────────────────────────────────────── */

function isAccountUrl(url) {
    try {
        const pathname = new URL(url, window.location.href).pathname;
        return /\/account\//.test(pathname);
    } catch {
        return false;
    }
}

/**
 * Block clicks on any <a href="…/account/…"> that the CSS
 * pointer-events suppression might not have caught (e.g. keyboard Enter).
 */
document.addEventListener(
    "click",
    (e) => {
        const anchor = e.target.closest("a[href]");
        if (anchor && isAccountUrl(anchor.href)) {
            e.preventDefault();
            e.stopImmediatePropagation();
        }
    },
    /* capture = true so we run before Fava's own listeners */
    true,
);

/**
 * Block Fava's Svelte router from pushing /account/ URLs into history.
 * Fava uses history.pushState for client-side navigation between reports.
 */
const _origPush = history.pushState.bind(history);
history.pushState = function (state, title, url) {
    if (url && isAccountUrl(String(url))) return;
    return _origPush(state, title, url);
};

const _origReplace = history.replaceState.bind(history);
history.replaceState = function (state, title, url) {
    if (url && isAccountUrl(String(url))) return;
    return _origReplace(state, title, url);
};
