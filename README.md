# ⬢ Hex Chess

A fully playable implementation of **Glinski's Hexagonal Chess** in Python/pygame — with a complete game engine, interactive GUI, and a Minimax AI opponent. Also playable in the browser via WebAssembly.

🎮 **[Play in browser](https://mortiz2.github.io/HexChessBot/)**

---

## Features

- **All 6 piece types** with correct Glinski movement rules — Pawn, Rook, Bishop, Knight, Queen, King
- **Full game logic** — check detection, checkmate, stalemate, en passant
- **Interactive GUI** — click to select pieces, legal moves highlighted in real time
- **Minimax AI** with alpha-beta pruning, selectable depth 1–5
- **Background threading** — AI thinks without freezing the UI (native); synchronous fallback for WebAssembly
- **Game timer**, check notifications, win screen with result and game time
- **Menu screen** — Human vs Human or vs AI mode, depth selector

---

## Running locally

**Requirements:** Python 3.10+, pygame 2.x

```bash
pip install pygame
python3 main.py
```

---

## Project structure

```
main.py       — game loop, menu, AI integration
board.py      — Board class: rendering, hex↔pixel conversion, check/checkmate logic
pieces.py     — Piece classes (Pawn, Rook, Bishop, Knight, Queen, King), Move, create_piece factory
ai.py         — Minimax with alpha-beta pruning, AIWorker background thread
hexmath.py    — Cube coordinate math (Hex, hex_add, hex_neighbor, cube_round)
assets/       — Piece images (PNG)
```

---

## How it works

The board uses **cube coordinates** (q + r + s = 0). Directions 0–5 are orthogonal (Rook/edges), 6–11 are diagonal (Bishop/vertices). The AI uses **minimax with alpha-beta pruning** and a material-based evaluation function.

| Piece  | Value |
|--------|-------|
| Pawn   | 100   |
| Knight | 300   |
| Bishop | 320   |
| Rook   | 500   |
| Queen  | 900   |
| King   | 20000 |

AI depth guide: depth 1–2 = instant/easy, depth 3 ≈ 1–2 s, depth 4 ≈ 5–10 s, depth 5 ≈ 30 s+.

---

## Web build (GitHub Pages)

The project is automatically built and deployed via GitHub Actions using [pygbag](https://pygame-web.github.io/):

```
.github/workflows/deploy.yml  — build with pygbag → deploy to gh-pages branch
```

Every push to `main` triggers a new deploy. The live URL is:
`https://mortiz2.github.io/HexChessBot/`

---

## Credits

- [Hex grid math](https://www.redblobgames.com) — cube coordinate reference
- [Chess piece images](https://greenchess.net/info.php?item=downloads) — GreenChess
- [pygbag](https://pygame-web.github.io/) — pygame → WebAssembly compiler