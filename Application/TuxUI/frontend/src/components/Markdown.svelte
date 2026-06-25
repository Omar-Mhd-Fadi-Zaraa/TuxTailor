<script>
  import { renderMarkdown } from "../lib/markdown.js";

  export let source = "";

  $: html = renderMarkdown(source);
</script>

<div class="markdown">{@html html}</div>

<style>
  .markdown {
    font-size: 0.9rem;
    line-height: 1.65;
    word-break: break-word;
  }

  .markdown :global(p) {
    margin: 0 0 0.75rem;
  }

  .markdown :global(p:last-child) {
    margin-bottom: 0;
  }

  .markdown :global(h1),
  .markdown :global(h2),
  .markdown :global(h3),
  .markdown :global(h4) {
    margin: 1.25rem 0 0.5rem;
    line-height: 1.3;
    font-weight: 700;
  }

  .markdown :global(h1) { font-size: 1.35rem; }
  .markdown :global(h2) { font-size: 1.15rem; }
  .markdown :global(h3) { font-size: 1rem; }
  .markdown :global(h4) { font-size: 0.95rem; }

  .markdown :global(h1:first-child),
  .markdown :global(h2:first-child),
  .markdown :global(h3:first-child),
  .markdown :global(h4:first-child) {
    margin-top: 0;
  }

  .markdown :global(ul),
  .markdown :global(ol) {
    margin: 0 0 0.75rem;
    padding-left: 1.4rem;
  }

  .markdown :global(li) {
    margin: 0.2rem 0;
  }

  .markdown :global(li > p) {
    margin: 0;
  }

  .markdown :global(blockquote) {
    margin: 0 0 0.75rem;
    padding: 0.25rem 0 0.25rem 0.85rem;
    border-left: 3px solid var(--border-strong);
    color: var(--text-muted);
  }

  .markdown :global(a) {
    color: var(--accent);
    text-decoration: underline;
    text-underline-offset: 2px;
  }

  .markdown :global(a:hover) {
    opacity: 0.85;
  }

  .markdown :global(code) {
    font-family: "Menlo", "Monaco", "Consolas", monospace;
    font-size: 0.84em;
    background: var(--panel-bg);
    border: 1px solid var(--border);
    border-radius: 4px;
    padding: 0.1em 0.35em;
  }

  .markdown :global(pre) {
    margin: 0 0 0.75rem;
    padding: 0.75rem 0.9rem;
    background: var(--thinking-bg);
    border: 1px solid var(--border);
    border-radius: 8px;
    overflow-x: auto;
  }

  .markdown :global(pre code) {
    display: block;
    padding: 0;
    background: transparent;
    border: none;
    border-radius: 0;
    font-size: 0.82rem;
    line-height: 1.55;
    white-space: pre;
  }

  .markdown :global(hr) {
    border: none;
    border-top: 1px solid var(--border);
    margin: 1rem 0;
  }

  .markdown :global(table) {
    width: 100%;
    margin: 0 0 0.75rem;
    border-collapse: collapse;
    font-size: 0.86rem;
  }

  .markdown :global(th),
  .markdown :global(td) {
    border: 1px solid var(--border);
    padding: 0.4rem 0.6rem;
    text-align: left;
  }

  .markdown :global(th) {
    background: var(--panel-bg);
    font-weight: 600;
  }

  .markdown :global(img) {
    max-width: 100%;
    border-radius: 8px;
  }

  .markdown :global(strong) {
    font-weight: 700;
  }
</style>
