# 🎴 Memory Match (Pygame)

A classic **Memory Match** (Concentration) card game built with **Pygame**. Flip cards two at a time and try to find all matching pairs with as few moves as possible.

The game board contains **16 cards** (8 matching pairs). All cards start face-down. Click a card to flip it, then click another one — if the two images match, they stay face-up; otherwise, they flip back after a short delay.

---

## ✨ Features

- ✅ 4×4 grid with 8 matching pairs (16 cards total)
- ✅ Custom images loaded from the `images/` folder
- ✅ Supports `.png`, `.jpg`, and `.jpeg` file formats
- ✅ Smooth automatic image scaling to fit cards
- ✅ Move counter and live timer
- ✅ Win screen with final stats
- ✅ Hover highlight for clickable cards
- ✅ Quick restart with `R`
- ✅ Clean exit with `Esc`
- ✅ Graceful error message if images are missing

---

## 📋 Requirements

- **Python 3.8+**
- **Pygame**

Install Pygame:

```bash
pip install pygame
```

---

## 📁 Project Structure

Your project folder must look like this:

```
project/
├── main.py
└── images/
    ├── 1.jpg      (or 1.png / 1.jpeg)
    ├── 2.jpg
    ├── 3.jpg
    ├── 4.jpg
    ├── 5.jpg
    ├── 6.jpg
    ├── 7.jpg
    └── 8.jpg
```

### Rules for image files

- **Exactly 8 images**, named `1` through `8` (no leading zeros).
- **Extensions can be** `.png`, `.jpg`, or `.jpeg` — the game detects whichever exists.
- **Recommended minimum size:** 120×120 pixels (square preferred).
- **PNG with transparent background** looks best, but JPG works fine.
- Each image will be **automatically scaled** to `100×100` inside the card.

> ⚠️ If any of the 8 images is missing or invalid, the game will print a clear error listing the missing files and exit gracefully.

---

## 🚀 How to Run

1. Make sure the `images/` folder sits **next to** `main.py`.
2. Open a terminal in the project folder:

```bash
cd path/to/your/project
python main.py
```

Alternatively, on Windows you can double-click `main.py` (if Python is associated with `.py` files).

---

## 🕹️ How to Play

1. All 16 cards start **face-down** with a `?` on the back.
2. Click any card — it flips and reveals its image.
3. Click a **second** card:
   - ✅ **If the two images match** → both cards turn **green** and stay face-up.
   - ❌ **If they don't match** → both flip back after **800 ms**.
4. Keep flipping pairs until all **8 pairs** are matched.
5. The game ends when every pair is found — you'll see a **"You Win!"** message with your final move count and time.

---

## ⌨️ Controls

| Action          | Function                          |
|-----------------|-----------------------------------|
| **Left click**  | Flip a card                       |
| **`R`**         | Restart the game                  |
| **`Esc`**       | Quit the game                     |

---

## 🎨 Customization

You can adjust these values at the top of `main.py`:

```python
# Board layout
WIDTH, HEIGHT           = 700, 780
GRID_COLS, GRID_ROWS    = 4, 4
CARD_SIZE               = 140
CARD_GAP                = 15

# Game rules
NUM_PAIRS               = 8       # Number of matching pairs
MISMATCH_DELAY          = 800     # Delay before wrong cards flip back (ms)
IMAGE_DISPLAY_SIZE      = (100, 100)  # Size of image inside each card

# Images folder
IMAGES_DIR              = "images"
```

### Changing colors

All colors are defined at the top of the file:

```python
BG_COLOR            = (28, 30, 48)     # Background
CARD_BACK           = (60, 110, 180)   # Card back (face-down)
CARD_FACE           = (245, 245, 250)  # Card face (revealed)
CARD_MATCHED        = (110, 200, 130)  # Matched cards (green)
HOVER_BORDER        = (255, 210, 80)   # Hover highlight
TEXT_COLOR          = (240, 240, 240)  # HUD text
```

### Changing the grid size

To use a different number of pairs, update both:

1. `NUM_PAIRS = N` (and add images `1` through `N` to the `images/` folder).
2. `GRID_COLS` and `GRID_ROWS` to accommodate `2 × N` cards — for example, 6 pairs → `3×4` grid, 10 pairs → `4×5` grid.

You may also need to adjust `WIDTH` and `HEIGHT` to fit the larger board.

---

## 🧠 How It Works

### Card model

Each `Card` object stores only:
- `image_key` — the image identifier (`"1"` through `"8"`)
- `flipped` — whether the card is currently face-up
- `matched` — whether the card has been permanently matched

### Game flow

1. **Deck creation** — all 8 image keys are added twice (16 cards) and shuffled.
2. **First click** — a card is flipped and stored as `first_pick`.
3. **Second click** — stored as `second_pick`; the move counter increments.
   - **Match** → both cards marked `matched`, pair counter increases.
   - **Mismatch** → a timestamp is recorded; after `MISMATCH_DELAY` ms, both flip back.
4. **Win condition** — when `pairs_found == total_pairs`, the timer stops and the win screen appears.

### Image loading

The `load_images()` function loops through indices `1` to `NUM_PAIRS` and tries each extension in order (`.png`, `.jpg`, `.jpeg`). The first one found is loaded and scaled with `pygame.transform.smoothscale` for high-quality resizing. If none is found for an index, the game exits with a helpful error message.

---

## 🗂️ Code Structure

```
main.py
├── Configuration (dimensions, colors, fonts)
├── Image loading (load_images)
├── Card class
├── Deck creation (create_deck)
├── Game state variables
├── Helper functions
│   ├── reset_game()        → reset the game
│   ├── get_card_rect()     → compute a card's on-screen rect
│   ├── draw_card()         → render a single card
│   ├── format_time()       → mm:ss formatting
│   └── draw_hud()          → title, stats, and hints
└── Main loop (event handling + rendering)
```

---

## 🐛 Troubleshooting

### "Missing or invalid images" error on startup

- Make sure the `images/` folder is **next to** `main.py`, not inside another folder.
- Check that file names are exactly `1`, `2`, ..., `8` with a valid extension.
- On Windows, verify that extensions aren't hidden — a file might actually be `1.jpg.png` if extensions are hidden.

### Images look stretched

Images are scaled to `100×100` regardless of aspect ratio. For non-square images, either:
- Crop them to square before adding them, or
- Modify `load_images()` to preserve aspect ratio by padding.

### Game window doesn't appear

- Ensure `pygame` is installed: `pip install pygame`
- Run from a terminal to see any error messages.

### Text appears cut off on some systems

- If the "Moves:" or "Time:" text seems clipped, reduce the font size in `info_font`.

---

## 🧩 Ideas for Extension

- 🤖 Add a time limit per turn
- 🏆 Track high scores across sessions (save to file)
- 🎨 Allow selecting different card back designs
- 🎵 Add sound effects for flips and matches
- 🌐 Multiplayer mode (two players alternate turns)
- 📱 Add difficulty levels (easy 4×3, medium 4×4, hard 5×4)
- 🖼️ Let players supply their own images via a file picker

---

## 📄 License

This project is free to use, modify, and share however you like. 