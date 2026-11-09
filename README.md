# 🎴 Memory Match (Pygame)

A classic **Memory Match** (also known as **Concentration**, **Memory**, or **Pelmanism**) card game built with **Pygame**. Flip cards two at a time and try to find all matching pairs with as few moves as possible.

Before the game starts, you choose your board size (**4×4**, **6×6**, **8×8**, or **10×10**). The game automatically scans the `images/` folder, loads every valid image it finds, and uses as many as needed for the selected board size.

---

## 📖 About the Game

The game of memory Match is old and famouse game for all age groups.the game have different name around the world such as Concentration in the United States, Pelmanism in the UK, Memory in Germany, and Pairs in many other countries.  the game have a simple idea: finding matching pairs of cards. It's easy to learn for players, fun to play, and also a good game for train your memory, concentration, visual recognition, and the ability to remember where things are placed.

The gameplay is very simple. All cards are placed face-down on a table or board, with each card having one matching pair hidden somewhere. Players take turns flipping over two cards at a time. If the cards match with together, they stay face-up and the player get a point. If they don't match, both cards are turned face-down again. The challenge for this game is remembering the positions of previously revealed cards so you can find their matching pairs later.

 The best things about Memory Match is that every game feels different. The cards are shuffled randomly at the beginning of each round, so players never know where the matching pairs will be.the players can play harder if they want for example a small 4×4 board is a good starting point for beginners and younger players, while a larger 10×10 board with 50 pairs offers a much greater challenge and requires strong memory.

---

## 🎯 Game Rules in Detail

### The board

- The board is a **square grid** of cards, all initially face-down with a `?` on the back.
- Each grid size determines the total number of cards and the number of pairs:

  | Board size | Total cards | Pairs |
  |------------|-------------|-------|
  | **4×4**    | 16          | 8     |
  | **6×6**    | 36          | 18    |
  | **8×8**    | 64          | 32    |
  | **10×10**  | 100         | 50    |

- Every image in the deck appears **exactly twice** — once as a pair. There are no unpaired cards.

### A turn

1. **Click any face-down card.** It flips face-up and reveals its image. This is your **first pick**.
2. **Click a second face-down card.** It also flips. This is your **second pick**.
3. The game now compares the two images:
   - ✅ **If they match** → both cards turn **green** and remain face-up permanently. Your pair counter increases by one.
   - ❌ **If they don't match** → both cards flip back **face-down after a short delay** (800 ms by default). Your move counter still increases — every attempt counts, even a wrong one.
4. Play continues until **every pair on the board has been matched**.

### Winning

- There is **no "losing"** in this game — the only outcome is *how few moves* and *how little time* you needed to clear the board.
- When the last pair is found, the game stops the timer and displays a **"You Win!"** screen with your final **move count** and **elapsed time**.

### What counts as a "move"

A **move** is one complete flip pair (one first-pick + one second-pick). So:
- If you flip two cards and they match, that's **one move**.
- If they don't match, that's still **one move**.
- The theoretical perfect game on a 4×4 board is **8 moves** (every pair found on the first try). Realistically, most players need 12–20.

---

## 🧠 Strategy & Tips

Memory Match looks like pure luck, but skilled players consistently clear boards in far fewer moves than beginners. Here are the techniques that matter:

### 1. Start from the corners and edges
When a new game begins, flip cards in a **systematic order** (e.g., top-left → top-right → bottom-left → bottom-right) rather than randomly. This helps you build a mental map of the board.

### 2. Chunk the board into regions
Instead of trying to remember 16, 36, or 100 positions at once, mentally divide the board into **quadrants** and focus on one at a time. Human short-term memory holds roughly 7 ± 2 items — chunking lets you store more by grouping.

### 3. Use verbal or visual anchors
Give each image a quick mental label ("red flower", "blue cat", "sun"). Attaching a **word** to a **position** makes it far more memorable than raw pixels.

### 4. Re-flip known matches first
If you know where a pair is but there's a face-down card blocking your mental map, **flip the known pair first** to score the point, then use your remaining flips to explore.

### 5. Track mismatches on purpose
When a mismatch happens, **deliberately note both cards' positions** before they flip back. Those two locations are now "known" — you just need to find their partners.

### 6. Exploit the mismatch delay
The 800 ms delay before a wrong pair flips back is actually **free study time**. Watch carefully during that window; that's your best chance to encode the position.

### 7. On large boards, work methodically
On 8×8 and 10×10 boards, resistance to random clicking is everything. Pick a scan order (left-to-right, top-to-bottom) and stick to it — you'll find pairs far faster than by hunting randomly.

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
- **Avoid duplicate images** — if the same picture appears under two different filenames, the game treats them as two separate pairs, which may confuse players (see the note in the Customization section).

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

- **4×4** — easy (8 pairs) — perfect for a quick game or for children
- **6×6** — medium (18 pairs) — a solid challenge for most players
- **8×8** — hard (32 pairs) — demands real concentration and memory
- **10×10** — expert (50 pairs) — a serious endurance test

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

- Press `R` to **restart with the same board size** (a new shuffle with new random images).
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

### Adjusting difficulty

The difficulty knob is `MISMATCH_DELAY`:

- **400 ms** → very hard, almost impossible to study the cards
- **800 ms** → default, balanced
- **1500 ms** → relaxed, good for children
- **2500 ms** → very forgiving

### Adding or removing board sizes

Edit `GRID_OPTIONS` — the menu is generated dynamically:

```python
GRID_OPTIONS = [3, 4, 5, 6, 8, 10]   # any list of integers
```

The menu will automatically show one button per option, and each button will check whether you have enough images. Just remember each size needs `(size × size) / 2` images.

---

## 🧠 How It Works (Technical)

### Image scanning

At startup (and every time you return to the menu via `Esc`), `scan_images()` walks the `images/` folder, loads every valid image, and stores the result in `AVAILABLE_IMAGES`. Each entry is a `(filename, pygame.Surface)` pair. Invalid or unreadable files are skipped with a console warning.

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

### Two different cards look identical

If you have **two images that look the same** (e.g., two photos of the same cat), the game treats them as different pairs. A player might pick one, then pick the other, and expect a match — but they won't match. Use **unique-looking images** to avoid confusion.

### Card layout looks too small on very large boards

The board auto-fits within the window (`WIDTH - 40` × `HEIGHT - 200`). If you increase `WIDTH`/`HEIGHT`, cards on 8×8 and 10×10 boards will grow accordingly.

### Game window doesn't appear

- Ensure `pygame` is installed: `pip install pygame`
- Run from a terminal to see any error messages.

---
## 📸 Screenshots

### Main Menu
![Main Menu](screenshots/game-menu.png)

### Gameplay (4×4)
![Gameplay 4x4](screenshots/game-board.png)

### Winning Screen
![Win Screen](screenshots/win-game.png)

## 🧩 Ideas for Extension

- 🤖 Add a single-player **vs. AI** mode with adjustable AI memory
- 🏆 Track high scores per board size (save to file)
- 👥 **Two-player turn-based** mode: whoever finds a pair gets another turn
- 🎨 Allow choosing different card back designs
- 🎵 Add sound effects for flips and matches
- ⏱️ Pause / resume the timer
- 🖼️ Drag-and-drop images into the window to add them
- 🎯 Show a preview of a mismatched pair for a split second before hiding
- 📊 Add a **streak counter** that rewards consecutive correct matches

---

## 📄 License

This project is free to use, modify, and share however you like. 🎉