/**
 * script.js – Indian Crime Data Analysis 2020
 * Shared JavaScript utilities for all pages.
 */

const API = 'http://localhost:5001';

/* ═══════════════════════════════════════════
   UTILITY HELPERS
═══════════════════════════════════════════ */

/** Show global spinner */
function showSpinner(msg = 'Loading...') {
  const ov = document.getElementById('spinnerOverlay');
  const tx = document.getElementById('spinnerText');
  if (ov) { ov.classList.add('active'); if (tx) tx.textContent = msg; }
}

/** Hide global spinner */
function hideSpinner() {
  const ov = document.getElementById('spinnerOverlay');
  if (ov) ov.classList.remove('active');
}

/** Format large numbers with commas */
function fmtNum(n) {
  if (n === null || n === undefined) return '—';
  return Number(n).toLocaleString('en-IN');
}

/** Animate counter from 0 to target */
function animateCount(el, target, duration = 1600) {
  const start = performance.now();
  const isFloat = String(target).includes('.');
  const update = (now) => {
    const p = Math.min((now - start) / duration, 1);
    const ease = 1 - Math.pow(1 - p, 4);
    const val = ease * target;
    el.textContent = isFloat
      ? val.toFixed(2)
      : fmtNum(Math.round(val));
    if (p < 1) requestAnimationFrame(update);
  };
  requestAnimationFrame(update);
}

/** Set active nav link based on current page */
function setActiveNav() {
  const page = window.location.pathname.split('/').pop() || 'index.html';
  document.querySelectorAll('.nav-links a').forEach(a => {
    const href = a.getAttribute('href');
    if (href === page || (page === '' && href === 'index.html')) {
      a.classList.add('active');
    } else {
      a.classList.remove('active');
    }
  });
}

/** Show an alert in a container */
function showAlert(containerId, message, type = 'error') {
  const icons = { error: '✖', success: '✔', info: 'ℹ', warning: '⚠' };
  const el = document.getElementById(containerId);
  if (!el) return;
  el.innerHTML = `
    <div class="alert alert-${type}">
      <span>${icons[type] || '●'}</span>
      <span>${message}</span>
    </div>`;
}

/** Generic fetch wrapper with error handling */
async function apiFetch(endpoint, opts = {}) {
  const res = await fetch(API + endpoint, {
    headers: { 'Content-Type': 'application/json' },
    ...opts,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ error: res.statusText }));
    throw new Error(err.error || `HTTP ${res.status}`);
  }
  return res.json();
}

/** Create a skeleton placeholder row */
function skeletonRow(cols) {
  return `<tr>${Array(cols).fill('<td><div class="skeleton" style="height:14px;width:80%">&nbsp;</div></td>').join('')}</tr>`;
}

/** Build nav HTML (shared across pages) */
const NAV_HTML = `
<nav>
  <a href="index.html" class="nav-brand">
    <div class="brand-icon">🔍</div>
    <span class="brand-text">CrimeAnalytics</span>
    <span class="brand-year">2020</span>
  </a>
  <div class="nav-links">
    <a href="index.html">Home</a>
    <a href="dashboard.html">Dashboard</a>
    <a href="data.html">Data</a>
    <a href="visualizations.html">Visualizations</a>
    <a href="analysis.html">Analysis</a>
  </div>
</nav>`;

const SPINNER_HTML = `
<div class="spinner-overlay" id="spinnerOverlay">
  <div class="spinner"></div>
  <div class="spinner-text" id="spinnerText">Loading...</div>
</div>`;

const FOOTER_HTML = `
<footer>
  <p>Indian Crime Data Analysis 2020 &nbsp;·&nbsp;
     Data Source: <a href="#">NCRB 2020</a> &nbsp;·&nbsp;
     Built with Flask + Vanilla JS
  </p>
</footer>`;

/** Inject shared layout into page */
function injectLayout() {
  // Nav
  const navEl = document.getElementById('navContainer');
  if (navEl) { navEl.innerHTML = NAV_HTML; setActiveNav(); }

  // Spinner
  const spEl = document.getElementById('spinnerContainer');
  if (spEl) spEl.innerHTML = SPINNER_HTML;

  // Footer
  const ftEl = document.getElementById('footerContainer');
  if (ftEl) ftEl.innerHTML = FOOTER_HTML;
}

/** On DOM ready, set up shared layout */
document.addEventListener('DOMContentLoaded', () => {
  injectLayout();
});
