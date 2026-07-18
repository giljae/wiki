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
        primaryColor: '#1c1c21',
        primaryTextColor: '#ededf0',
        primaryBorderColor: '#6d9584',
        lineColor: '#7d7d88',
        secondaryColor: '#141a17',
        tertiaryColor: '#16161a'
      } : {
        primaryColor: '#f6f5f1',
        primaryTextColor: '#141416',
        primaryBorderColor: '#6b8f7c',
        lineColor: '#76767f',
        secondaryColor: '#f2f7f4',
        tertiaryColor: '#ffffff'
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

  // ── Nav highlight & tree ───────────────────────────────
  function initNav() {
    const slug = config.currentSlug;

    document.querySelectorAll('.nav-toggle').forEach((btn) => {
      btn.addEventListener('click', (e) => {
        e.preventDefault();
        e.stopPropagation();
        const li = btn.closest('.nav-item');
        if (!li) return;
        const open = li.classList.toggle('nav-open');
        btn.setAttribute('aria-expanded', open ? 'true' : 'false');
      });
    });

    if (!slug) return;

    document.querySelectorAll('.nav-tree a[data-slug]').forEach((link) => {
      const itemSlug = link.dataset.slug;
      const li = link.closest('.nav-item');
      if (itemSlug === slug) {
        li?.classList.add('nav-current');
      }
      if (slug.startsWith(itemSlug + '/')) {
        li?.classList.add('nav-ancestor');
        let parent = li?.parentElement?.closest('.nav-item');
        while (parent) {
          parent.classList.add('nav-open', 'nav-ancestor');
          parent = parent.parentElement?.closest('.nav-item');
        }
      }
    });
  }

  // ── Auto TOC (when [[_TOC_]] not used) ────────────────
  function initAutoToc() {
    const panel = document.getElementById('wiki-toc-panel');
    if (!panel || panel.querySelector('.toc:not(.toc-auto)')) return;

    const article = document.querySelector('.article-body');
    const autoToc = panel.querySelector('.toc-auto');
    const list = document.getElementById('wiki-auto-toc');
    if (!article || !autoToc || !list) return;

    const headings = article.querySelectorAll('h2, h3');
    if (!headings.length) return;

    headings.forEach((h) => {
      const anchor = h.querySelector('.anchor');
      const id = anchor?.getAttribute('href')?.slice(1) || h.id;
      if (!id) return;
      const li = document.createElement('li');
      if (h.tagName === 'H3') li.style.paddingLeft = '0.75rem';
      const a = document.createElement('a');
      a.href = '#' + id;
      a.textContent = h.textContent.replace(/^#\s*/, '').trim();
      li.appendChild(a);
      list.appendChild(li);
    });

    autoToc.hidden = false;
  }

  // ── Boot ───────────────────────────────────────────────
  document.addEventListener('DOMContentLoaded', async () => {
    initTheme();
    initNav();
    initAutoToc();
    initCodeCopy();
    await loadSearchIndex();
    initSearch();
    initMermaid();
    initMath();
  });
})();
