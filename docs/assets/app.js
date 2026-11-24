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

  document.querySelectorAll('.run-frames').forEach(gallery => {
    const controls = gallery.querySelector('.frame-controls');
    const picker = controls.querySelector('select');
    const previous = controls.querySelector('.frame-back');
    const next = controls.querySelector('.frame-forward');
    const link = gallery.querySelector('.run-image-link');
    const image = link.querySelector('img');
    const heading = gallery.closest('article').querySelector('h3').textContent;
    const show = index => {
      picker.selectedIndex = index;
      const path = picker.value;
      link.href = path;
      image.src = path;
      image.alt = heading + ' — ' + path.split('/').pop();
      previous.disabled = index === 0;
      next.disabled = index === picker.length - 1;
    };
    previous.addEventListener('click', () => show(picker.selectedIndex - 1));
    next.addEventListener('click', () => show(picker.selectedIndex + 1));
    picker.addEventListener('change', () => show(picker.selectedIndex));
    show(picker.selectedIndex);
    controls.hidden = false;
  });

  if (location.protocol === 'http:' || location.protocol === 'https:') {
    document.querySelectorAll('.event-viewer').forEach(viewer => {
      const run = viewer.closest('article');
      const link = run.querySelector('.run-trajectory a');
      const controls = viewer.querySelector('.event-controls');
      const number = controls.querySelector('input');
      const previous = controls.querySelector('.event-back');
      const next = controls.querySelector('.event-forward');
      const record = viewer.querySelector('.event-record');
      const status = viewer.querySelector('.event-status');
      let events;
      let loading = false;
      const show = index => {
        index = Math.max(1, Math.min(events.length, Math.round(index) || 1));
        number.value = index;
        previous.disabled = index === 1;
        next.disabled = index === events.length;
        record.textContent = JSON.stringify(JSON.parse(events[index - 1]), null, 2);
        record.scrollTop = 0;
      };
      previous.addEventListener('click', () => show(number.valueAsNumber - 1));
      next.addEventListener('click', () => show(number.valueAsNumber + 1));
      number.addEventListener('change', () => show(number.valueAsNumber));
      viewer.addEventListener('toggle', async () => {
        if (!viewer.open || loading || events) return;
        loading = true;
        status.textContent = 'Loading trajectory…';
        try {
          const response = await fetch(link.href);
          if (!response.ok) throw new Error();
          events = (await response.text()).trimEnd().split(/\r?\n/);
          show(1);
          record.hidden = controls.hidden = false;
          status.textContent = '';
        } catch (_) {
          events = undefined;
          status.textContent = 'Could not open the event viewer. Use the JSONL download.';
        } finally { loading = false; }
      });
      viewer.hidden = false;
    });
  }

  const citations = document.querySelectorAll('[data-excerpt]');
  let activeSource;
  let pinned = false;
  let closeTimer;

  function closeExcerpt() {
    clearTimeout(closeTimer);
    if (activeSource) document.getElementById(activeSource.dataset.excerpt).hidden = true;
    activeSource = null;
    pinned = false;
  }

  function positionExcerpt() {
    if (!activeSource) return;
    const box = document.getElementById(activeSource.dataset.excerpt);
    const rect = activeSource.getBoundingClientRect();
    if (rect.bottom < 0 || rect.top > window.innerHeight) return closeExcerpt();
    const left = Math.max(12, Math.min(rect.left, window.innerWidth - box.offsetWidth - 12));
    const below = rect.bottom + 6;
    box.style.left = left + 'px';
    box.style.top = Math.max(8, below + box.offsetHeight <= window.innerHeight - 8
      ? below : rect.top - box.offsetHeight - 6) + 'px';
  }

  function openExcerpt(source) {
    clearTimeout(closeTimer);
    if (activeSource !== source) closeExcerpt();
    activeSource = source;
    const box = document.getElementById(source.dataset.excerpt);
    if (box.hidden) {
      box.hidden = false;
      const body = box.querySelector('.excerpt-body');
      body.scrollTop = 0;
      const mark = body.querySelector('mark');
      if (mark) {
        const offset = mark.getBoundingClientRect().top - body.getBoundingClientRect().top;
        if (offset > body.clientHeight / 2) body.scrollTop = offset - body.clientHeight / 3;
      }
    }
    positionExcerpt();
  }

  function scheduleClose() {
    clearTimeout(closeTimer);
    if (!pinned) closeTimer = setTimeout(closeExcerpt, 180);
  }

  citations.forEach(source => {
    const box = document.getElementById(source.dataset.excerpt);
    source.addEventListener('pointerenter', event => {
      if (event.pointerType !== 'touch') openExcerpt(source);
    });
    source.addEventListener('pointerleave', scheduleClose);
    source.addEventListener('focus', () => openExcerpt(source));
    source.addEventListener('blur', event => {
      if (!box.contains(event.relatedTarget)) closeExcerpt();
    });
    source.addEventListener('keydown', event => {
      if (event.key === 'ArrowDown') {
        event.preventDefault();
        openExcerpt(source);
        box.querySelector('.excerpt-body').focus({preventScroll: true});
      }
    });
    box.addEventListener('focusout', event => {
      if (event.relatedTarget !== source && !box.contains(event.relatedTarget)) closeExcerpt();
    });
    source.addEventListener('click', event => {
      event.preventDefault();
      if (pinned && activeSource === source) return closeExcerpt();
      openExcerpt(source);
      pinned = true;
    });
    box.addEventListener('pointerenter', () => clearTimeout(closeTimer));
    box.addEventListener('pointerleave', scheduleClose);
  });
  if (citations.length) {
    document.addEventListener('keydown', event => {
      if (event.key === 'Escape' && activeSource) {
        const box = document.getElementById(activeSource.dataset.excerpt);
        if (box.contains(document.activeElement)) activeSource.focus({preventScroll: true});
        closeExcerpt();
      }
    });
    document.addEventListener('pointerdown', event => {
      if (!event.target.closest('[data-excerpt], .source-popover')) closeExcerpt();
    });
    window.addEventListener('scroll', positionExcerpt, {capture: true, passive: true});
    window.addEventListener('resize', positionExcerpt);
  }

  const clipPlayer = document.querySelector('dialog.clip-player');
  if (clipPlayer && typeof clipPlayer.showModal === 'function') {
    const video = clipPlayer.querySelector('video');
    document.querySelectorAll('a.clip-link').forEach(link => {
      link.addEventListener('click', event => {
        if (event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
        event.preventDefault();
        closeExcerpt();
        clipPlayer.querySelector('h3').textContent = 'Criterion ' + link.dataset.criterion + ' · Evidence ' + link.textContent;
        video.src = link.href;
        clipPlayer.showModal();
        video.play().catch(() => {});
      });
    });
    clipPlayer.addEventListener('close', () => {
      video.pause();
      video.removeAttribute('src');
      video.load();
    });
    clipPlayer.addEventListener('click', event => {
      if (event.target === clipPlayer) {
        const rect = clipPlayer.getBoundingClientRect();
        if (event.clientX < rect.left || event.clientX > rect.right || event.clientY < rect.top || event.clientY > rect.bottom) clipPlayer.close();
      }
    });
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
