(() => {
  'use strict';

  const themeButton = document.querySelector('.theme-toggle');
  const updateThemeLabel = () => {
    const dark = document.documentElement.dataset.theme === 'dark';
    themeButton?.setAttribute('aria-label', `Switch to ${dark ? 'light' : 'dark'} theme`);
    themeButton?.setAttribute('title', `Switch to ${dark ? 'light' : 'dark'} theme`);
  };
  if (themeButton) {
    themeButton.hidden = false;
    updateThemeLabel();
    themeButton.addEventListener('click', () => {
      const theme = document.documentElement.dataset.theme === 'dark' ? 'light' : 'dark';
      document.documentElement.dataset.theme = theme;
      try { localStorage.setItem('aab-theme', theme); } catch (_) { /* Theme still works. */ }
      updateThemeLabel();
    });
  }

  let toastTimer;
  const showToast = message => {
    const toast = document.querySelector('.toast');
    if (!toast) return;
    clearTimeout(toastTimer);
    toast.textContent = message;
    toast.classList.add('visible');
    toastTimer = setTimeout(() => toast.classList.remove('visible'), 2800);
  };

  const copyText = async text => {
    try {
      if (navigator.clipboard && window.isSecureContext) {
        await navigator.clipboard.writeText(text);
        return;
      }
    } catch (_) { /* Fall back when clipboard permissions are unavailable. */ }
    const active = document.activeElement;
    const field = document.createElement('textarea');
    field.value = text;
    field.setAttribute('readonly', '');
    field.style.cssText = 'position:fixed;left:-9999px;top:0';
    document.body.append(field);
    field.select();
    let copied = false;
    try { copied = document.execCommand('copy'); }
    finally { field.remove(); active?.focus({ preventScroll: true }); }
    if (!copied) throw new Error('Clipboard unavailable');
  };

  document.querySelectorAll('.copy-button').forEach(button => {
    button.hidden = false;
    button.addEventListener('click', async () => {
      try {
        await copyText(button.dataset.copy);
        showToast(button.classList.contains('text-button') ? 'Task instruction copied' : 'File path copied');
      } catch (_) {
        showToast('Copy unavailable. Select the text to copy it manually.');
      }
    });
  });

  const search = document.querySelector('#task-search');
  const filter = document.querySelector('#category-filter');
  if (search && filter) {
    const rows = [...document.querySelectorAll('.task-row')];
    const count = document.querySelector('#result-count');
    const empty = document.querySelector('.empty-state');
    const form = document.querySelector('.catalog-controls');
    form.hidden = false;
    const params = new URLSearchParams(window.location.search);
    search.value = params.get('q') || '';
    if ([...filter.options].some(option => option.value === params.get('domain'))) {
      filter.value = params.get('domain');
    }
    const applyFilters = () => {
      const words = search.value.trim().toLowerCase().split(/\s+/).filter(Boolean);
      let visible = 0;
      rows.forEach(row => {
        const matches = (!filter.value || row.dataset.category === filter.value)
          && words.every(word => row.dataset.search.includes(word));
        row.hidden = !matches;
        if (matches) visible++;
      });
      count.textContent = `${visible} ${visible === 1 ? 'task' : 'tasks'}${visible < rows.length ? ' of 10' : ''}`;
      empty.hidden = visible !== 0;
      const url = new URL(window.location.href);
      for (const [key, value] of [['q', search.value.trim()], ['domain', filter.value]]) {
        if (value) url.searchParams.set(key, value);
        else url.searchParams.delete(key);
      }
      try { window.history.replaceState(null, '', url); } catch (_) { /* Filtering also works on file URLs. */ }
    };
    search.addEventListener('input', applyFilters);
    filter.addEventListener('change', applyFilters);
    form.addEventListener('submit', event => { event.preventDefault(); applyFilters(); });
    document.querySelector('.reset-filters').addEventListener('click', () => {
      search.value = '';
      filter.value = '';
      applyFilters();
      search.focus();
    });
    document.addEventListener('keydown', event => {
      if (event.key === '/' && !event.ctrlKey && !event.metaKey && !event.altKey
          && !event.target.closest('input, textarea, select, [contenteditable]')) {
        event.preventDefault();
        search.focus();
      }
    });
    applyFilters();
  }

  // Track the section at the reading position, including long rubric tables.
  const navLinks = [...document.querySelectorAll('.section-nav a')];
  if (navLinks.length) {
    const sections = navLinks.map(link => document.querySelector(link.getAttribute('href')));
    let pending = false;
    const updateSection = () => {
      let active = 0;
      sections.forEach((section, index) => {
        if (section.getBoundingClientRect().top <= 160) active = index;
      });
      if (window.innerHeight + window.scrollY >= document.documentElement.scrollHeight - 10) active = sections.length - 1;
      navLinks.forEach((link, index) => {
        link.classList.toggle('current', index === active);
        if (index === active) link.setAttribute('aria-current', 'location');
        else link.removeAttribute('aria-current');
      });
      pending = false;
    };
    window.addEventListener('scroll', () => {
      if (!pending) { pending = true; requestAnimationFrame(updateSection); }
    }, { passive: true });
    window.addEventListener('resize', updateSection);
    updateSection();
  }
})();
