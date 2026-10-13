"""PreToolUse hook: when Claude is about to read a PDF, convert it to Markdown
with MarkItDown and tell Claude to read the .md instead. On any problem it
lets the PDF be read normally (fail-open)."""
import hashlib
import json
import sys
from pathlib import Path

CACHE_DIR = Path.home() / ".claude" / "pdf-cache"
MIN_CHARS = 200  # below this we assume a scanned PDF (no text layer)


def allow():
    sys.exit(0)  # no output = the PDF read proceeds normally


def main():
    try:
        data = json.load(sys.stdin)
    except Exception:
        allow()

    if data.get("tool_name") != "Read":
        allow()
    tool_input = data.get("tool_input") or {}
    file_path = tool_input.get("file_path", "")
    if not file_path.lower().endswith(".pdf"):
        allow()
    # Explicit page reads (e.g. for tables/images): let them through
    if tool_input.get("pages"):
        allow()

    pdf = Path(file_path)
    if not pdf.is_file():
        allow()

    key = hashlib.sha1(str(pdf.resolve()).lower().encode("utf-8")).hexdigest()[:10]
    md_path = CACHE_DIR / f"{pdf.stem}-{key}.md"

    # Cache: reuse the .md if it is newer than the PDF
    if not (md_path.exists() and md_path.stat().st_mtime >= pdf.stat().st_mtime):
        try:
            from markitdown import MarkItDown
            text = MarkItDown().convert(str(pdf)).text_content or ""
        except Exception:
            allow()
        if len(text.strip()) < MIN_CHARS:
            allow()  # most likely scanned: let Claude see the PDF itself
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        md_path.write_text(text, encoding="utf-8")

    reason = (
        f"This PDF was converted to Markdown to save tokens. "
        f"Read this file instead: {md_path}\n"
        f"If you need tables/images/layout that were lost, read specific pages "
        f"of the PDF with Read and the pages parameter."
    )
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": reason,
        }
    }))
    sys.exit(0)


if __name__ == "__main__":
    main()
