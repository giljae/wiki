(function () {
  'use strict';

  const config = window.WIKI_CONFIG || { basePath: '', searchIndexUrl: '/search-index.json' };

  // ── Theme ──────────────────────────────────────────────
  function initTheme() {
    const stored = localStorage.getItem('wiki-theme');
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    const theme = stored || (prefersDark ? 'dark' : 'light');
    document.documentElement.dataset.theme = theme;

    document.getElementById('theme-toggle')?.addEventListener('click', () => {
      const next = document.documentElement.dataset.theme === 'dark' ? 'light' : 'dark';
      document.documentElement.dataset.theme = next;
      localStorage.setItem('wiki-theme', next);
      updateMermaidTheme();
    });
  }

  // ── Mermaid ────────────────────────────────────────────
  function updateMermaidTheme() {
    if (typeof mermaid === 'undefined') return;
    const isDark = document.documentElement.dataset.theme === 'dark';
    mermaid.initialize({
      startOnLoad: false,
      theme: isDark ? 'dark' : 'neutral',
      themeVariables: isDark ? {
        primaryColor: '#2c2c30',
        primaryTextColor: '#ececee',
        primaryBorderColor: '#3d5248',
        lineColor: '#7e7e86',
        secondaryColor: '#1a201c',
        tertiaryColor: '#1a1a1d'
      } : {
        primaryColor: '#f3f2ef',
        primaryTextColor: '#1a1a1c',
        primaryBorderColor: '#b8c9c0',
        lineColor: '#7a7a82',
        secondaryColor: '#f0f4f2',
        tertiaryColor: '#efeeeb'
      },
      securityLevel: 'loose'
    });
  }

  function initMermaid() {
    if (typeof mermaid === 'undefined') return;
    updateMermaidTheme();

    const mermaidPattern = /^(graph |flowchart|sequenceDiagram|classDiagram|stateDiagram|erDiagram|gantt|pie |gitGraph|mindmap|timeline)/;

    document.querySelectorAll('pre code.language-mermaid, pre code.mermaid').forEach(convertToMermaid);
    document.querySelectorAll('pre.highlight').forEach((pre) => {
      const text = pre.textContent.trim();
      if (mermaidPattern.test(text)) convertToMermaid(pre);
    });

    function convertToMermaid(el) {
      const text = el.textContent.trim();
      const div = document.createElement('div');
      div.className = 'mermaid';
      div.textContent = text;
      (el.closest('pre') || el).replaceWith(div);
    }

    mermaid.run({ querySelector: '.mermaid' });
  }

  // ── KaTeX ──────────────────────────────────────────────
  function initMath() {
    if (typeof renderMathInElement === 'undefined') return;

    document.querySelectorAll('.kdmath').forEach((el) => {
      el.innerHTML = el.textContent;
    });

    renderMathInElement(document.body, {
      delimiters: [
        { left: '$$', right: '$$', display: true },
        { left: '$', right: '$', display: false },
        { left: '\\(', right: '\\)', display: false },
        { left: '\\[', right: '\\]', display: true }
      ],
      throwOnError: false
    });
  }

  // ── Code copy ──────────────────────────────────────────
  function initCodeCopy() {
    document.querySelectorAll('pre > code').forEach((code) => {
      const pre = code.parentElement;
      if (pre.closest('.code-block-wrap') || pre.closest('.highlight')) return;
      if (code.classList.contains('language-mermaid') || code.classList.contains('mermaid')) return;

      const wrap = document.createElement('div');
      wrap.className = 'code-block-wrap';
      pre.parentNode.insertBefore(wrap, pre);
      wrap.appendChild(pre);

      const btn = document.createElement('button');
      btn.className = 'copy-btn';
      btn.type = 'button';
      btn.textContent = 'Copy';
      btn.addEventListener('click', async () => {
        await navigator.clipboard.writeText(code.textContent);
        btn.textContent = 'Copied!';
        btn.classList.add('copied');
        setTimeout(() => { btn.textContent = 'Copy'; btn.classList.remove('copied'); }, 1500);
      });
      wrap.appendChild(btn);
    });

    document.querySelectorAll('.highlight').forEach((highlight) => {
      if (highlight.closest('.code-block-wrap')) return;
      const wrap = document.createElement('div');
      wrap.className = 'code-block-wrap';
      highlight.parentNode.insertBefore(wrap, highlight);
      wrap.appendChild(highlight);

      const btn = document.createElement('button');
      btn.className = 'copy-btn';
      btn.type = 'button';
      btn.textContent = 'Copy';
      btn.addEventListener('click', async () => {
        const text = highlight.querySelector('pre')?.textContent || highlight.textContent;
        await navigator.clipboard.writeText(text);
        btn.textContent = 'Copied!';
        btn.classList.add('copied');
        setTimeout(() => { btn.textContent = 'Copy'; btn.classList.remove('copied'); }, 1500);
      });
      wrap.appendChild(btn);
    });
  }

  // ── Search ─────────────────────────────────────────────
  let searchIndex = [];

  async function loadSearchIndex() {
    try {
      const res = await fetch(config.searchIndexUrl);
      searchIndex = await res.json();
    } catch {
      searchIndex = [];
    }
  }

  function search(query) {
    if (!query || query.length < 2) return [];
    const q = query.toLowerCase();
    return searchIndex
      .map((item) => {
        const titleMatch = item.title.toLowerCase().includes(q);
        const contentIdx = item.content.toLowerCase().indexOf(q);
        if (!titleMatch && contentIdx === -1) return null;
        let snippet = '';
        if (contentIdx !== -1) {
          const start = Math.max(0, contentIdx - 40);
          snippet = (start > 0 ? '…' : '') + item.content.slice(start, contentIdx + 60).trim() + '…';
        }
        return { ...item, snippet, score: titleMatch ? 2 : 1 };
      })
      .filter(Boolean)
      .sort((a, b) => b.score - a.score)
      .slice(0, 8);
  }

  function initSearch() {
    const input = document.getElementById('wiki-search');
    const results = document.getElementById('search-results');
    if (!input || !results) return;

    let timer;
    input.addEventListener('input', () => {
      clearTimeout(timer);
      timer = setTimeout(() => {
        const hits = search(input.value.trim());
        if (!hits.length) {
          results.hidden = true;
          return;
        }
        results.innerHTML = hits.map((h) =>
          `<a href="${h.url}"><div class="search-result-title">${h.title}</div>${h.snippet ? `<div class="search-result-snippet">${h.snippet}</div>` : ''}</a>`
        ).join('');
        results.hidden = false;
      }, 150);
    });

    input.addEventListener('blur', () => setTimeout(() => { results.hidden = true; }, 200));
    input.addEventListener('focus', () => {
      if (input.value.trim().length >= 2) input.dispatchEvent(new Event('input'));
    });
  }

  // ── Boot ───────────────────────────────────────────────
  document.addEventListener('DOMContentLoaded', async () => {
    initTheme();
    initCodeCopy();
    await loadSearchIndex();
    initSearch();
    initMermaid();
    initMath();
  });
})();
