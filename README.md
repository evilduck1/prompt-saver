# Prompt Saver

A lightweight prompt library manager built for the Invoke community.

- Store prompts with optional images
- Save/load an external library file
- Export/Import backups independently of library saves
- Designed to be portable (no install required if you distribute as a bundled app)

## Development

### Prerequisites
- Node.js (LTS recommended)
- Rust toolchain (via rustup)
- Tauri prerequisites for your OS

### Install & Run (dev)
```bash
npm install
npm run tauri dev

## macOS first run (important)

If macOS says **“Prompt Saver is damaged and can’t be opened”**, this is Gatekeeper quarantine.

### Required order (important)
Before first launch, do this **once**:

1. **Move `Prompt Saver.app` into `/Applications`**
2. **Do NOT open it yet**
3. Open **Terminal** and run:

```bash
xattr -dr com.apple.quarantine "/Applications/Prompt Saver.app"
```

4. Now open **Prompt Saver.app** normally

### If you kept it in Downloads instead
(Still run this **before the first launch**)

```bash
xattr -dr com.apple.quarantine "$HOME/Downloads/Prompt Saver.app"
```

**Tip:** You can type the command, then drag the `.app` into Terminal to auto‑fill the path.
