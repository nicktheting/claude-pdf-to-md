# Claude Code: PDF → Markdown hook

A [Claude Code](https://docs.claude.com/en/docs/claude-code) hook that automatically converts
any PDF to Markdown with [MarkItDown](https://github.com/microsoft/markitdown) before Claude reads it.

**Why:** fewer tokens on text-heavy PDFs, and `.md` files you can search with `grep`.

## How it works

1. Claude is about to `Read` a `.pdf`.
2. The `PreToolUse` hook converts it to `.md` in `~/.claude/pdf-cache/`
   (or reuses the cached file if the PDF hasn't changed).
3. The hook blocks the PDF read and tells Claude to read the `.md` instead.

**Fail-open:** for scanned PDFs (no text layer), conversion errors, or explicit page reads
(`pages` parameter), the PDF is read normally.

## Installation (Windows)

1. Install the dependency:
   ```powershell
   pip install -U "markitdown[pdf]"
   ```
2. Copy `hooks/pdf-to-md.py` to `%USERPROFILE%\.claude\hooks\`.
3. Merge the `hooks` block from `settings.example.json` into
   `%USERPROFILE%\.claude\settings.json` (replace `<USERNAME>`).
4. Validate the JSON:
   ```powershell
   Get-Content "$env:USERPROFILE\.claude\settings.json" -Raw | ConvertFrom-Json | Out-Null; "OK"
   ```
5. Start a new Claude Code session (hooks load at session start).

macOS/Linux: same steps, use `python3` and `~/.claude/hooks/pdf-to-md.py` in the command.

## Test

```powershell
'{"tool_name":"Read","tool_input":{"file_path":"C:/path/to/file.pdf"}}' | python "$env:USERPROFILE\.claude\hooks\pdf-to-md.py"
```

Expected: JSON with `"permissionDecision": "deny"` and a new `.md` in `~/.claude/pdf-cache/`.
No output means the hook let the PDF through (file not found, scanned PDF, or error).

In Claude Code, ask it to read a PDF by path: the PDF read shows as **Failed** (blocked by the hook)
and Claude then reads the cached `.md`.

## Limitations

- PDFs attached directly in the chat don't go through `Read`, so the hook can't intercept them.
  Give Claude the file path instead.
- No OCR: scanned PDFs are read normally (no savings).
- Complex tables may lose structure. Ask Claude to read specific pages of the PDF when needed.
- `pdf-cache` contains the text of your PDFs: don't share it or commit it.

## Troubleshooting

- **Hook doesn't run:** replace `python` with `py` or the full path from `(Get-Command python).Source`.
- **Clear the cache:** delete the contents of `~/.claude/pdf-cache/`; files are regenerated on demand.

## License

MIT
