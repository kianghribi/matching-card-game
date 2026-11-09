# 🎴 Memory Match (Pygame)

A classic **Memory Match** (Concentration) card game built with **Pygame**. Flip cards two at a time and try to find all matching pairs with as few moves as possible.

Before the game starts, you choose your board size (**4×4**, **6×6**, **8×8**, or **10×10**). The game automatically scans the `images/` folder, loads every valid image it finds, and uses as many as needed for the selected board size.

---

## ✨ Features

- ✅ **Board size selection menu** (4×4, 6×6, 8×8, 10×10)
- ✅ **Auto-scan** of the `images/` folder — any filenames are accepted
- ✅ Supports `.png`, `.jpg`, and `.jpeg` file formats
- ✅ Automatic smooth scaling of images to fit each card size
- ✅ Cards, fonts, and "?" back-icons resize automatically per board size
- ✅ Move counter and live timer
- ✅ Win screen with final stats
- ✅ Hover highlight for clickable cards
- ✅ Unplayable board sizes are **automatically greyed out** with a hint showing how many more images are needed
- ✅ Quick restart with `R`
- ✅ Return to menu with `Esc` (rescans images on return)
- ✅ Clean quit from menu with `Esc`
- ✅ Graceful error message if the `images/` folder is missing or empty

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
    └── 8.jpg      ← plus any additional images you want
```

### Rules for image files

- **Any filename is accepted** — the game auto-scans the folder (e.g., `1.jpg`, `cat.png`, `sunset.jpeg`, etc.).
- **Extensions can be** `.png`, `.jpg`, or `.jpeg`.
- **Recommended minimum size:** 120×120 pixels (square preferred).
- **PNG with transparent background** looks best, but JPG works fine.
- Each image will be **automatically scaled** to fit the current card size.

### How many images do I need?

| Board size | Total cards | Pairs needed |
|------------|-------------|--------------|
| **4×4**    | 16          | 8            |
| **6×6**    | 36          | 18           |
| **8×8**    | 64          | 32           |
| **10×10**  | 100         | 50           |

> ⚠️ A board size only becomes **playable** if the `images/` folder contains at least that many valid images. Otherwise, its button is greyed out with a message like _"needs 18 images (have 8)"_.

If the `images/` folder is missing or contains no valid images, the game exits with a clear error message.

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

### 1. Menu Screen

When the game starts, you'll see a menu with four buttons:

- **4×4** — easy (8 pairs)
- **6×6** — medium (18 pairs)
- **8×8** — hard (32 pairs)
- **10×10** — expert (50 pairs)

A button is **enabled (blue)** only if you have enough images. Disabled buttons appear **greyed out** with a hint showing how many images are missing.

The footer shows the **total number of images** currently loaded from the `images/` folder.

### 2. Game Screen

1. All cards start **face-down** with a `?` on the back.
2. Click any card — it flips and reveals its image.
3. Click a **second** card:
   - ✅ **If the two images match** → both cards turn **green** and stay face-up.
   - ❌ **If they don't match** → both flip back after **800 ms**.
4. Keep flipping pairs until all pairs are matched.
5. The game ends when every pair is found — you'll see a **"You Win!"** message with your final move count and time.

### 3. After the Game

- Press `R` to **restart with the same board size**.
- Press `Esc` to **return to the menu** and pick a different size.

---

## ⌨️ Controls

### On the Menu Screen

| Action          | Function                          |
|-----------------|-----------------------------------|
| **Left click**  | Start a game with the chosen size |
| **`Esc`**       | Quit the game                     |

### On the Game Screen

| Action          | Function                          |
|-----------------|-----------------------------------|
| **Left click**  | Flip a card                       |
| **`R`**         | Restart with the same board size  |
| **`Esc`**       | Return to the menu (rescans images) |

---

## 🎨 Customization

You can adjust these values at the top of `main.py`:

```python
# Window dimensions
WIDTH, HEIGHT  = 700, 800

# Game rules
MISMATCH_DELAY = 800       # Delay before wrong cards flip back (ms)

# Available board sizes
GRID_OPTIONS   = [4, 6, 8, 10]

# Images folder
IMAGES_DIR     = "images"
```

### Changing colors

All colors are defined at the top of the file:

```python
BG_COLOR            = (28, 30, 48)     # Background
BUTTON_BG           = (60, 110, 180)   # Menu button (enabled)
BUTTON_HOVER        = (80, 140, 210)   # Menu button (hover)
BUTTON_DISABLED     = (55, 55, 65)     # Menu button (disabled)
CARD_BACK           = (60, 110, 180)   # Card back (face-down)
CARD_FACE           = (245, 245, 250)  # Card face (revealed)
CARD_MATCHED        = (110, 200, 130)  # Matched cards (green)
HOVER_BORDER        = (255, 210, 80)   # Hover highlight
TEXT_COLOR          = (240, 240, 240)  # HUD text
WARN_COLOR          = (240, 180, 80)   # "not enough images" hint
```

### Adding or removing board sizes

Edit `GRID_OPTIONS` — the menu is generated dynamically:

```python
GRID_OPTIONS = [3, 4, 5, 6, 8, 10]   # any list of integers
```

The menu will automatically show one button per option, and each button will check whether you have enough images.

---

## 🧠 How It Works

### Image scanning

At startup (and every time you return to the menu via `Esc`), `scan_images()` walks the `images/` folder, loads every valid image, and stores the result in `AVAILABLE_IMAGES`. Each entry is a `(filename, pygame.Surface)` pair.

### Card model

Each `Card` object stores:
- `pair_id` — a number identifying which pair the card belongs to
- `image` — the pre-scaled image surface for that pair
- `flipped` — whether the card is currently face-up
- `matched` — whether the card has been permanently matched

### Deck creation per board size

When you pick a size:
1. `pairs_needed = (size × size) / 2`.
2. A random sample of `pairs_needed` unique images is drawn from `AVAILABLE_IMAGES`.
3. The images are **scaled once** to fit the current card size.
4. Each image is added **twice** to the deck (creating a pair) with a shared `pair_id`.
5. The deck is shuffled.

### Layout calculation

Card size, gap, and board position are computed **dynamically** based on the chosen grid size, so the board always fits the window. The "?" back symbol is also re-rendered at an appropriate font size each time.

### Win condition

When `pairs_found == total_pairs`, the timer stops and the win screen appears.

---

## 🗂️ Code Structure

```
main.py
├── Configuration (dimensions, colors, fonts, grid options)
├── Image scanning (scan_images)
├── Card class
├── Menu helpers
│   ├── get_menu_buttons()  → build clickable button rects
│   └── draw_menu()         → render the menu screen
├── Game helpers
│   ├── start_game(gsize)   → build the deck & layout for a given size
│   ├── get_card_rect()     → compute a card's on-screen rect
│   ├── draw_card()         → render a single card
│   ├── format_time()       → mm:ss formatting
│   └── draw_hud()          → title, stats, and hints
└── Main loop (state machine: MENU ↔ PLAY)
```

---

## 🐛 Troubleshooting

### "No images found" error on startup

- Make sure the `images/` folder is **next to** `main.py`, not inside another folder.
- Make sure at least one valid image (`.png`, `.jpg`, `.jpeg`) is inside it.

### A board size is greyed out even though I have enough images

- Return to the menu (`Esc`) so the game **rescans** the folder.
- Check that the images are not corrupted — the game prints a warning to the console for any image it fails to load.

### Images look stretched

Images are scaled to roughly 82% of the card size, square. For non-square images, either:
- Crop them to square before adding them, or
- Modify `start_game()` to preserve aspect ratio by padding.

### Card layout looks too small on very large boards

The board auto-fits within the window (`WIDTH - 40` × `HEIGHT - 200`). If you increase `WIDTH`/`HEIGHT`, cards on 8×8 and 10×10 boards will grow accordingly.

### Game window doesn't appear

- Ensure `pygame` is installed: `pip install pygame`
- Run from a terminal to see any error messages.

### Text appears cut off on some systems

- If the HUD text seems clipped, reduce the `info_font` and `big_font` sizes.

---

## 🧩 Ideas for Extension

- 🤖 Add a time limit per turn
- 🏆 Track high scores per board size (save to file)
- 🎨 Allow choosing different card back designs
- 🎵 Add sound effects for flips and matches
- 🌐 Multiplayer mode (two players alternate turns)
- ⏱️ Pause / resume the timer
- 🖼️ Drag-and-drop images into the window to add them
- 🎯 Show a preview of a mismatched pair for a split second before hiding

---

## 📄 License

This project is free to use, modify, and share however you like. 🎉