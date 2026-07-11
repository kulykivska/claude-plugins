# lsp: per-machine binary install

The plugin only wires the servers; the binaries install once per machine:

```bash
npm i -g pyright typescript-language-server typescript
# sourcekit-lsp ships with Xcode; verify:
xcrun --find sourcekit-lsp
```

Verify in Claude Code: enable the plugin, open a .py/.ts/.swift file, and
check the plugin errors tab for any missing-binary complaint.
