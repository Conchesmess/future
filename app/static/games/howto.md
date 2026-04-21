# How to Add a New pygbag Game

## Requirements
- A game built with [pygbag](https://pygame-web.github.io/) (produces an `index.html` and a `.apk` file)
- No changes to the game files needed — the server handles everything automatically

---

## Steps

### 1. Create a folder for the game
Inside `app/static/games/`, create a folder named after your game.
Use only letters, numbers, hyphens, and underscores — no spaces.

```
app/static/games/
    mankala/        ← existing example
    your-game/      ← new game
```

### 2. Copy in the pygbag build output
Drop the files pygbag produced into your game folder. At minimum you need:

```
app/static/games/your-game/
    index.html      ← unmodified, straight from pygbag
    your-game.apk   ← the game bundle
    favicon.png     ← optional but recommended
```

### 3. That's it — no code changes needed
The game is immediately available at:

```
http://127.0.0.1:8080/games/your-game/
```

The server automatically:
- Serves the game as a top-level page (required for SharedArrayBuffer / WASM)
- Sets COOP/COEP security headers so the browser allows WASM to run
- Rewrites CDN URLs in `index.html` to route through the local proxy
- Proxies all pygame-web CDN resources with the required CORP headers

---

## How it works (quick reference)

| URL pattern                    | What it does                                           |
|--------------------------------|--------------------------------------------------------|
| `/games/<name>/`               | Landing page with "Play" button — Flask nav visible    |
| `/games/<name>/play/`          | Game popup window (full canvas, COOP/COEP headers)     |
| `/games/<name>/play/<file>`    | Serves game assets (apk, png, etc.)                    |
| `/pygbag-cdn/<path>`           | Proxies pygame-web CDN with required CORP headers      |
| `/mankala`                     | Redirects to `/games/mankala/` (legacy)                |

---

## Troubleshooting

**Game freezes on load**
- Open browser DevTools → Network tab and look for red (failed) requests
- All requests should go to `127.0.0.1:8080` — none to `pygame-web.github.io`

**"can't access property 'statSync', i.fs is undefined"**
- BrowserFS failed to load, usually due to a double-slash URL in the game's
  `index.html` (e.g. `archives/0.9//browserfs.min.js`). The server normalizes
  these automatically — if you see this error, ensure you are using the latest
  version of the game serving code.

**NS_ERROR_DOM_CORP_FAILED errors**
- The CDN URL rewriting didn't catch something — check the game's `index.html`
  for any hardcoded `https://pygame-web.github.io/` URLs and replace with `/pygbag-cdn/`

**404 on the .apk file**
- Make sure the folder name in `static/games/` matches the URL you're using
- The `.apk` filename doesn't need to match anything — pygbag finds it via `index.html`

**"Ready to start!" message appears but nothing happens**
- Click anywhere on the canvas — pygbag requires a user interaction to start audio/media
