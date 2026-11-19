// Apply the theme before rendering, including when storage is unavailable.
(() => {
  let theme;
  try { theme = localStorage.getItem('aab-theme'); } catch (_) { /* Use system preference. */ }
  if (theme !== 'light' && theme !== 'dark') {
    theme = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
  }
  document.documentElement.dataset.theme = theme;
})();
