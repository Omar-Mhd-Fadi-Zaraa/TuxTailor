import { marked } from "marked";
import DOMPurify from "dompurify";

marked.setOptions({
  gfm: true,
  breaks: true,
});

export function renderMarkdown(source) {
  if (!source) return "";
  const raw = marked.parse(source, { async: false });
  return DOMPurify.sanitize(raw, { USE_PROFILES: { html: true } });
}
