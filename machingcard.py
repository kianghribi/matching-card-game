import pygame
import sys
import random
import os
import json
from datetime import datetime

pygame.init()

# --- Configuration ---
WIDTH, HEIGHT = 700, 800
MISMATCH_DELAY = 800
GRID_OPTIONS = [4, 6, 8, 10]
MAX_SCORES_PER_SIZE = 10
SCORES_FILE = "scores.json"
IMAGES_DIR = "images"
RESERVED_BASES = {"background", "bg", "card_back", "menu_bg"}

# --- Colors ---
WHITE                = (255, 255, 255)
BG_TOP               = (18, 20, 40)
BG_BOTTOM            = (42, 48, 80)

CARD_BACK_BASE       = (55, 105, 175)
CARD_BACK_PATTERN    = (38, 78, 138)
CARD_BACK_BORDER     = (20, 50, 95)

BTN_BASE             = (55, 105, 175)
BTN_PATTERN          = (42, 85, 148)
BTN_BORDER           = (25, 60, 108)

BTN_HOVER_BASE       = (250, 205, 75)
BTN_HOVER_PATTERN    = (225, 170, 40)
BTN_HOVER_BORDER     = (170, 120, 25)

BTN_DISABLED_BASE    = (55, 58, 70)
BTN_DISABLED_PATTERN = (46, 48, 58)
BTN_DISABLED_BORDER  = (32, 34, 42)

CARD_FACE            = (245, 245, 250)
CARD_FACE_BORDER     = (130, 130, 155)
CARD_MATCHED         = (105, 195, 125)
CARD_MATCHED_PATTERN = (75, 165, 95)
CARD_MATCHED_BORDER  = (45, 135, 65)

TEXT_COLOR           = (240, 240, 240)
HUD_PURPLE           = (170, 130, 230)
TEXT_DARK            = (30, 30, 40)
HOVER_BORDER         = (255, 210, 80)
WIN_COLOR            = (255, 220, 100)
HINT_COLOR           = (180, 200, 255)
WARN_COLOR           = (240, 180, 80)
SUB_COLOR_OK         = (170, 220, 180)
INPUT_BG             = (45, 48, 70)
INPUT_BG_FOCUS       = (65, 70, 100)
INPUT_BORDER         = (100, 100, 130)
INPUT_BORDER_FOCUS   = (255, 210, 80)
GOLD_COLOR           = (255, 215, 0)
SILVER_COLOR         = (200, 200, 210)
BRONZE_COLOR         = (205, 127, 50)

# --- Fonts ---
menu_title_font = pygame.font.SysFont("arial", 54, bold=True)
menu_btn_font   = pygame.font.SysFont("arial", 30, bold=True)
small_font      = pygame.font.SysFont("arial", 17)
info_font       = pygame.font.SysFont("arial", 22, bold=True)
big_font        = pygame.font.SysFont("arial", 36, bold=True)
input_font      = pygame.font.SysFont("arial", 24)
score_font      = pygame.font.SysFont("arial", 18)
header_font     = pygame.font.SysFont("arial", 17, bold=True)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Memory Match - Pygame")
clock = pygame.time.Clock()


# ============ HELPERS ============
def format_time(ms):
    s = ms // 1000
    h = s // 3600
    m = (s % 3600) // 60
    sec = s % 60
    if h > 0:
        return f"{h}:{m:02d}:{sec:02d}"
    return f"{m:02d}:{sec:02d}"


# ============ SCORE PERSISTENCE ============
def load_scores():
    if not os.path.isfile(SCORES_FILE):
        return {}
    try:
        with open(SCORES_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        result = {}
        for k, v in data.items():
            if isinstance(v, list):
                v = [e for e in v if isinstance(e, dict)
                     and "name" in e and "moves" in e and "time" in e]
                v.sort(key=lambda e: (e["moves"], e["time"]))
                result[str(k)] = v
            else:
                result[str(k)] = []
        return result
    except Exception as e:
        print(f"Could not load scores: {e}")
        return {}


def save_scores(scores):
    try:
        with open(SCORES_FILE, "w", encoding="utf-8") as f:
            json.dump(scores, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Could not save scores: {e}")


def get_scores_for(scores, gsize):
    entries = scores.get(str(gsize), [])
    return entries if isinstance(entries, list) else []


def add_score(scores, gsize, name, moves, elapsed_ms):
    key = str(gsize)
    entries = scores.get(key, [])
    if not isinstance(entries, list):
        entries = []
    new_entry = {
        "name": name or "Player",
        "moves": moves,
        "time": elapsed_ms,
        "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
    }
    entries.append(new_entry)
    entries.sort(key=lambda e: (e["moves"], e["time"]))
    if len(entries) > MAX_SCORES_PER_SIZE:
        entries = entries[:MAX_SCORES_PER_SIZE]
    scores[key] = entries
    save_scores(scores)
    for i, e in enumerate(entries):
        if e is new_entry:
            return i + 1
    return None


# ============ IMAGE SCANNING ============
def find_image_by_base(base_name):
    """Find an image with the given base name in root or images/ folder."""
    exts = (".png", ".jpg", ".jpeg")
    for folder in ("", IMAGES_DIR):
        for ext in exts:
            path = os.path.join(folder, f"{base_name}{ext}") if folder else f"{base_name}{ext}"
            if os.path.isfile(path):
                return path
    return None


def scan_images():
    if not os.path.isdir(IMAGES_DIR):
        return []
    exts = (".png", ".jpg", ".jpeg")
    result = []
    for fname in sorted(os.listdir(IMAGES_DIR)):
        if not fname.lower().endswith(exts):
            continue
        base = os.path.splitext(fname)[0].lower()
        if base in RESERVED_BASES:
            continue
        full = os.path.join(IMAGES_DIR, fname)
        try:
            img = pygame.image.load(full).convert_alpha()
            result.append((fname, img))
        except Exception as e:
            print(f"Skipping invalid image {full}: {e}")
    return result


# ============ ASSET BUILDERS ============
_asset_cache = {}


def get_shadow(w, h, radius, alpha=80):
    key = ("shadow", w, h, radius, alpha)
    if key not in _asset_cache:
        surf = pygame.Surface((w, h), pygame.SRCALPHA)
        pygame.draw.rect(surf, (0, 0, 0, alpha), (0, 0, w, h), border_radius=radius)
        _asset_cache[key] = surf
    return _asset_cache[key]


def make_pattern_surface(w, h, base, pattern, border, radius=None):
    """Create a decorative card-like surface with rounded corners + diagonal pattern."""
    if radius is None:
        radius = max(8, min(w, h) // 12)
    key = (w, h, base, pattern, border, radius)
    if key in _asset_cache:
        return _asset_cache[key]

    surf = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.rect(surf, base, (0, 0, w, h), border_radius=radius)

    if pattern:
        pat = pygame.Surface((w, h), pygame.SRCALPHA)
        step = max(10, w // 8)
        lw = max(2, w // 55)
        for off in range(-h, w + h, step):
            pygame.draw.line(pat, pattern, (off, 0), (off + h, h), lw)
        # Mask to rounded rect
        mask = pygame.Surface((w, h), pygame.SRCALPHA)
        pygame.draw.rect(mask, (255, 255, 255, 255), (0, 0, w, h), border_radius=radius)
        pat.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        surf.blit(pat, (0, 0))

    bw = max(2, w // 55)
    pygame.draw.rect(surf, border, (0, 0, w, h), bw, border_radius=radius)

    inset = max(6, w // 14)
    if w - 2 * inset > 4 and h - 2 * inset > 4:
        pygame.draw.rect(surf, border,
                         (inset, inset, w - 2 * inset, h - 2 * inset),
                         max(1, bw // 2), border_radius=max(4, radius - 4))

    _asset_cache[key] = surf
    return surf


def build_card_back(w, h):
    """Build card back surface - custom image if available, else procedural."""
    key = ("card_back", w, h)
    if key in _asset_cache:
        return _asset_cache[key]

    radius = max(6, w // 12)
    path = find_image_by_base("card_back")

    if path:
        try:
            img = pygame.image.load(path).convert_alpha()


            ZOOM = 1.85

            if ZOOM > 1.0:
                big = pygame.transform.smoothscale(
                    img, (int(w * ZOOM), int(h * ZOOM))
                )
                crop_rect = pygame.Rect(
                    (big.get_width() - w) // 2,
                    (big.get_height() - h) // 2,
                    w, h
                )
                scaled = big.subsurface(crop_rect).copy()
            else:
                scaled = pygame.transform.smoothscale(img, (w, h))


            result = pygame.Surface((w, h), pygame.SRCALPHA)
            result.blit(scaled, (0, 0))

            mask = pygame.Surface((w, h), pygame.SRCALPHA)
            pygame.draw.rect(mask, (255, 255, 255, 255),
                             (0, 0, w, h), border_radius=radius)
            result.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

            pygame.draw.rect(result, CARD_BACK_BORDER,
                             (0, 0, w, h), 3, border_radius=radius)

            _asset_cache[key] = result
            return result

        except Exception as e:
            print(f"Could not load card back {path}: {e}")

    surf = make_pattern_surface(w, h, CARD_BACK_BASE, CARD_BACK_PATTERN,
                                CARD_BACK_BORDER, radius=radius)

 
    qm_size = max(16, int(w * 0.45))
    qm_font = pygame.font.SysFont("arial", qm_size, bold=True)
    qm = qm_font.render("?", True, (225, 235, 255))
    surf.blit(qm, qm.get_rect(center=(w // 2, h // 2)))

    _asset_cache[key] = surf
    return surf


def create_background():
    """Create background - custom image if available, else gradient + bokeh."""
    path = find_image_by_base("background")
    if not path:
        path = find_image_by_base("bg")
    if path:
        try:
            img = pygame.image.load(path).convert()
            return pygame.transform.smoothscale(img, (WIDTH, HEIGHT))
        except Exception as e:
            print(f"Could not load background {path}: {e}")

    # Procedural gradient
    surf = pygame.Surface((WIDTH, HEIGHT))
    for y in range(HEIGHT):
        t = y / max(1, HEIGHT - 1)
        r = int(BG_TOP[0] + (BG_BOTTOM[0] - BG_TOP[0]) * t)
        g = int(BG_TOP[1] + (BG_BOTTOM[1] - BG_TOP[1]) * t)
        b = int(BG_TOP[2] + (BG_BOTTOM[2] - BG_TOP[2]) * t)
        pygame.draw.line(surf, (r, g, b), (0, y), (WIDTH, y))

    # Soft bokeh
    rng = random.Random(42)
    for _ in range(28):
        x = rng.randint(-50, WIDTH + 50)
        y = rng.randint(-50, HEIGHT + 50)
        r = rng.randint(40, 160)
        color = rng.choice([
            (255, 255, 255, 7),
            (100, 150, 255, 12),
            (255, 180, 100, 9),
            (180, 100, 255, 8),
        ])
        blob = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
        pygame.draw.circle(blob, color, (r, r), r)
        surf.blit(blob, (x - r, y - r))
    return surf


# ============ INIT ASSETS ============
AVAILABLE_IMAGES = scan_images()
if not AVAILABLE_IMAGES:
    print(f"⚠️  No images found in '{IMAGES_DIR}/' folder.")
    pygame.quit()
    sys.exit(1)
print(f"Loaded {len(AVAILABLE_IMAGES)} images from '{IMAGES_DIR}/' folder.")

SCORES = load_scores()
BACKGROUND = create_background()


# ============ CARD ============
class Card:
    __slots__ = ("pair_id", "image", "flipped", "matched")

    def __init__(self, pair_id, image):
        self.pair_id = pair_id
        self.image = image
        self.flipped = False
        self.matched = False


# ============ STATE ============
STATE_MENU = "menu"
STATE_PLAY = "play"
STATE_SCORES = "scores"
state = STATE_MENU

player_name = "Player"
name_input_active = False
cursor_visible = True
cursor_timer = 0

grid_size = 4
board_cols = 4
board_rows = 4
card_size = 100
card_gap = 12
board_x = 0
board_y = 0
deck = []
first_pick = None
second_pick = None
mismatch_time = 0
moves = 0
pairs_found = 0
total_pairs = 8
game_won = False
start_time = 0
final_time = 0
last_rank = None

scores_view_size = 4

# UI rects
NAME_RECT = pygame.Rect((WIDTH - 320) // 2, 130, 320, 48)


def get_menu_buttons():
    btn_w, btn_h = 300, 80
    gap = 22
    start_y = 240
    x = (WIDTH - btn_w) // 2
    buttons = []
    for i, gsize in enumerate(GRID_OPTIONS):
        pairs_needed = (gsize * gsize) // 2
        y = start_y + i * (btn_h + gap)
        rect = pygame.Rect(x, y, btn_w, btn_h)
        playable = len(AVAILABLE_IMAGES) >= pairs_needed
        buttons.append((gsize, pairs_needed, rect, playable))
    return buttons


def get_scores_button_rect():
    return pygame.Rect((WIDTH - 280) // 2, 690, 280, 52)


def get_scores_tab_rects():
    tab_w, tab_h, gap = 130, 44, 12
    total_w = 4 * tab_w + 3 * gap
    start_x = (WIDTH - total_w) // 2
    y = 130
    rects = []
    for i, gsize in enumerate(GRID_OPTIONS):
        x = start_x + i * (tab_w + gap)
        rects.append((gsize, pygame.Rect(x, y, tab_w, tab_h)))
    return rects


def get_back_button_rect():
    return pygame.Rect((WIDTH - 220) // 2, HEIGHT - 85, 220, 52)


# ============ MENU ============
def get_button_surface(rect, kind):
    if kind == "disabled":
        base, pat, border = BTN_DISABLED_BASE, BTN_DISABLED_PATTERN, BTN_DISABLED_BORDER
    elif kind == "hover":
        base, pat, border = BTN_HOVER_BASE, BTN_HOVER_PATTERN, BTN_HOVER_BORDER
    else:
        base, pat, border = BTN_BASE, BTN_PATTERN, BTN_BORDER
    return make_pattern_surface(rect.width, rect.height, base, pat, border, radius=14)


def draw_menu():
    screen.blit(BACKGROUND, (0, 0))

    # Title with glow
    title = menu_title_font.render("Memory Match", True, TEXT_COLOR)
    title_shadow = menu_title_font.render("Memory Match", True, (0, 0, 0))
    rect = title.get_rect(center=(WIDTH // 2, 62))
    screen.blit(title_shadow, rect.move(3, 3))
    screen.blit(title, rect)

    # Name label
    label = small_font.render("Your name:", True, HINT_COLOR)
    screen.blit(label, (NAME_RECT.x, NAME_RECT.y - 22))

    # Name input (card style)
    name_rect_style = make_pattern_surface(
        NAME_RECT.width, NAME_RECT.height,
        INPUT_BG_FOCUS if name_input_active else INPUT_BG,
        (58, 62, 88) if not name_input_active else (78, 82, 115),
        INPUT_BORDER_FOCUS if name_input_active else INPUT_BORDER,
        radius=10,
    )
    screen.blit(name_rect_style, NAME_RECT.topleft)

    display = player_name
    if name_input_active and cursor_visible:
        display += "|"
    if not display.strip():
        display = " "
    name_surf = input_font.render(display, True, TEXT_COLOR)
    screen.blit(name_surf, (NAME_RECT.x + 14,
                            NAME_RECT.y + (NAME_RECT.height - name_surf.get_height()) // 2))

    mouse = pygame.mouse.get_pos()

    # Menu buttons
    for gsize, pairs_needed, rect, playable in get_menu_buttons():
        if not playable:
            kind, text_color = "disabled", (130, 130, 140)
        elif rect.collidepoint(mouse):
            kind, text_color = "hover", TEXT_DARK
        else:
            kind, text_color = "normal", WHITE

        # Shadow
        shadow = get_shadow(rect.width, rect.height, 14, 90)
        screen.blit(shadow, (rect.x + 4, rect.y + 6))

        # Card
        btn_surf = get_button_surface(rect, kind)
        screen.blit(btn_surf, rect.topleft)

        # Main label
        lbl = menu_btn_font.render(f"{gsize} × {gsize}", True, text_color)
        screen.blit(lbl, lbl.get_rect(center=(rect.centerx, rect.centery - 12)))

        # Subtitle
        if playable:
            best = get_scores_for(SCORES, gsize)
            if best:
                b = best[0]
                sub_text = f"Best: {b['moves']} moves / {format_time(b['time'])}"
                sub_color = GOLD_COLOR if kind != "hover" else (100, 60, 10)
            else:
                sub_text = f"{pairs_needed} pairs"
                sub_color = SUB_COLOR_OK if kind != "hover" else (40, 90, 40)
        else:
            sub_text = f"needs {pairs_needed} images (have {len(AVAILABLE_IMAGES)})"
            sub_color = WARN_COLOR

        sub = small_font.render(sub_text, True, sub_color)
        screen.blit(sub, sub.get_rect(center=(rect.centerx, rect.centery + 18)))

    # View Scores button
    sb = get_scores_button_rect()
    sb_kind = "hover" if sb.collidepoint(mouse) else "normal"
    sb_shadow = get_shadow(sb.width, sb.height, 12, 90)
    screen.blit(sb_shadow, (sb.x + 4, sb.y + 6))
    sb_surf = get_button_surface(sb, sb_kind)
    screen.blit(sb_surf, sb.topleft)
    sb_text_color = TEXT_DARK if sb_kind == "hover" else WHITE
    sb_text = menu_btn_font.render("View Scores", True, sb_text_color)
    screen.blit(sb_text, sb_text.get_rect(center=sb.center))

    footer = small_font.render(
        f"Images loaded: {len(AVAILABLE_IMAGES)}    |    Esc: quit",
        True, HINT_COLOR)
    screen.blit(footer, footer.get_rect(center=(WIDTH // 2, HEIGHT - 20)))


# ============ SCORES SCREEN ============
def draw_scores_screen():
    SCOREBOARD_BG = (15, 17, 28)
    screen.fill(SCOREBOARD_BG)

    title = menu_title_font.render("Scoreboard", True, TEXT_COLOR)
    title_shadow = menu_title_font.render("Scoreboard", True, (0, 0, 0))
    trect = title.get_rect(center=(WIDTH // 2, 62))
    screen.blit(title_shadow, trect.move(3, 3))
    screen.blit(title, trect)

    subtitle = small_font.render(
        "Ranked by fewer moves, then less time", True, HINT_COLOR)
    screen.blit(subtitle, subtitle.get_rect(center=(WIDTH // 2, 100)))

    mouse = pygame.mouse.get_pos()

    # Tabs
    for gsize, rect in get_scores_tab_rects():
        active = (gsize == scores_view_size)
        hover = rect.collidepoint(mouse)
        if active:
            kind = "hover"
            text_color = TEXT_DARK
        elif hover:
            kind = "normal"
            text_color = WHITE
        else:
            kind = "normal"
            text_color = WHITE

        shadow = get_shadow(rect.width, rect.height, 10, 70)
        screen.blit(shadow, (rect.x + 3, rect.y + 4))
        surf = get_button_surface(rect, kind)
        screen.blit(surf, rect.topleft)
        lbl = info_font.render(f"{gsize}×{gsize}", True, text_color)
        screen.blit(lbl, lbl.get_rect(center=rect.center))

    entries = get_scores_for(SCORES, scores_view_size)

    list_y = 200
    row_h = 42
    cols = [
        ("#", 80), ("Name", 160), ("Moves", 370),
        ("Time", 500), ("Date", 625),
    ]
    for text, x in cols:
        h = header_font.render(text, True, HINT_COLOR)
        screen.blit(h, (x - h.get_width() // 2, list_y))
    pygame.draw.line(screen, INPUT_BORDER,
                     (60, list_y + 28), (WIDTH - 60, list_y + 28), 2)

    if not entries:
        empty = info_font.render(
            "No scores yet — go play a game!", True, HINT_COLOR)
        screen.blit(empty, empty.get_rect(center=(WIDTH // 2, 380)))
    else:
        for i, e in enumerate(entries):
            y = list_y + 45 + i * row_h
            if i == 0:
                color = GOLD_COLOR
            elif i == 1:
                color = SILVER_COLOR
            elif i == 2:
                color = BRONZE_COLOR
            else:
                color = TEXT_COLOR
            values = [
                str(i + 1),
                e["name"][:14],
                str(e["moves"]),
                format_time(e["time"]),
                e["date"][:10],
            ]
            for (text, x), val in zip(cols, values):
                s = score_font.render(val, True, color)
                screen.blit(s, (x - s.get_width() // 2, y))

    # Back button
    bb = get_back_button_rect()
    bb_kind = "hover" if bb.collidepoint(mouse) else "normal"
    bb_shadow = get_shadow(bb.width, bb.height, 12, 90)
    screen.blit(bb_shadow, (bb.x + 4, bb.y + 6))
    bb_surf = get_button_surface(bb, bb_kind)
    screen.blit(bb_surf, bb.topleft)
    bb_text_color = TEXT_DARK if bb_kind == "hover" else WHITE
    bb_text = menu_btn_font.render("Back to Menu", True, bb_text_color)
    screen.blit(bb_text, bb_text.get_rect(center=bb.center))


# ============ GAME ============
def start_game(gsize):
    global grid_size, board_cols, board_rows, card_size, card_gap
    global board_x, board_y, deck, first_pick, second_pick
    global mismatch_time, moves, pairs_found, total_pairs
    global game_won, start_time, final_time, state, last_rank

    grid_size = gsize
    board_cols = board_rows = gsize
    total_pairs = (gsize * gsize) // 2

    max_board_w = WIDTH - 40
    max_board_h = HEIGHT - 200
    card_size = min(
        (max_board_w - (gsize - 1) * card_gap) // gsize,
        (max_board_h - (gsize - 1) * card_gap) // gsize,
    )
    board_w = board_cols * card_size + (board_cols - 1) * card_gap
    board_h = board_rows * card_size + (board_rows - 1) * card_gap
    board_x = (WIDTH - board_w) // 2
    board_y = 120 + (max_board_h - board_h) // 2

    imgs = [img for _, img in AVAILABLE_IMAGES]
    random.shuffle(imgs)
    selected = imgs[:total_pairs]

    img_size = max(20, int(card_size * 0.82))
    deck = []
    for pair_id, img in enumerate(selected):
        scaled = pygame.transform.smoothscale(img, (img_size, img_size))
        deck.append(Card(pair_id, scaled))
        deck.append(Card(pair_id, scaled))
    random.shuffle(deck)

    first_pick = None
    second_pick = None
    mismatch_time = 0
    moves = 0
    pairs_found = 0
    game_won = False
    start_time = pygame.time.get_ticks()
    final_time = 0
    last_rank = None
    state = STATE_PLAY


def get_card_rect(index):
    row = index // board_cols
    col = index % board_cols
    x = board_x + col * (card_size + card_gap)
    y = board_y + row * (card_size + card_gap)
    return pygame.Rect(x, y, card_size, card_size)


def draw_card(rect, card, hovered):
    radius = max(6, card_size // 12)

    if card.matched:
        surf = make_pattern_surface(rect.width, rect.height,
                                    CARD_MATCHED, CARD_MATCHED_PATTERN,
                                    CARD_MATCHED_BORDER, radius=radius)
        screen.blit(surf, rect.topleft)
        screen.blit(card.image, card.image.get_rect(center=rect.center))

    elif card.flipped:
        surf = make_pattern_surface(rect.width, rect.height,
                                    CARD_FACE, None,
                                    CARD_FACE_BORDER, radius=radius)
        screen.blit(surf, rect.topleft)
        screen.blit(card.image, card.image.get_rect(center=rect.center))

    else:
        BACK_WIDTH_RATIO = 0.85

        back_w = int(rect.width * BACK_WIDTH_RATIO)
        back_h = rect.height
        back = build_card_back(back_w, back_h)

        back_x = rect.centerx - back_w // 2
        back_y = rect.top
        screen.blit(back, (back_x, back_y))

        if hovered:
            overlay = pygame.Surface((back_w, back_h), pygame.SRCALPHA)
            pygame.draw.rect(overlay, (255, 210, 80, 80),
                             (0, 0, back_w, back_h),
                             border_radius=max(4, back_w // 12))
            screen.blit(overlay, (back_x, back_y))


def draw_hud():
    title = big_font.render(f"Memory Match  -  {grid_size} × {grid_size}", True, HUD_PURPLE)
    title_shadow = big_font.render(f"Memory Match  -  {grid_size} × {grid_size}", True, (0, 0, 0))
    trect = title.get_rect(center=(WIDTH // 2, 42))
    screen.blit(title_shadow, trect.move(2, 2))
    screen.blit(title, trect)

    moves_text = info_font.render(f"Moves: {moves}", True, HUD_PURPLE)
    pairs_text = info_font.render(f"Pairs: {pairs_found}/{total_pairs}", True, HUD_PURPLE)
    elapsed = final_time if game_won else (pygame.time.get_ticks() - start_time)
    time_text = info_font.render(f"Time: {format_time(elapsed)}", True, HUD_PURPLE)

    screen.blit(moves_text, (30, 82))
    screen.blit(pairs_text, (WIDTH // 2 - pairs_text.get_width() // 2, 82))
    screen.blit(time_text, (WIDTH - time_text.get_width() - 30, 82))

    if not game_won:
        hint = small_font.render("R: restart  -  Esc: back to menu", True, HINT_COLOR)
        screen.blit(hint, hint.get_rect(center=(WIDTH // 2, HEIGHT - 20)))

def draw_win_overlay():
    dim = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    dim.fill((10, 10, 20, 200))
    screen.blit(dim, (0, 0))

    panel_w, panel_h = 500, 340
    panel_rect = pygame.Rect((WIDTH - panel_w) // 2,
                             (HEIGHT - panel_h) // 2,
                             panel_w, panel_h)

    if last_rank == 1:
        border = GOLD_COLOR
        pattern = (140, 110, 30)
        base = (55, 48, 30)
    else:
        border = HOVER_BORDER
        pattern = (65, 90, 145)
        base = (35, 42, 72)

    panel = make_pattern_surface(panel_w, panel_h, base, pattern, border, radius=20)
    shadow = get_shadow(panel_w, panel_h, 20, 150)
    screen.blit(shadow, (panel_rect.x + 6, panel_rect.y + 10))
    screen.blit(panel, panel_rect.topleft)

    y = panel_rect.y + 55
    msg = big_font.render("You Win!", True, WIN_COLOR)
    screen.blit(msg, msg.get_rect(center=(WIDTH // 2, y)))

    y += 60
    name = info_font.render(f"Congratulations, {player_name or 'Player'}!",
                            True, HINT_COLOR)
    screen.blit(name, name.get_rect(center=(WIDTH // 2, y)))

    y += 40
    stats = info_font.render(
        f"Moves: {moves}   |   Time: {format_time(final_time)}",
        True, TEXT_COLOR)
    screen.blit(stats, stats.get_rect(center=(WIDTH // 2, y)))

    y += 45
    if last_rank is not None:
        if last_rank == 1:
            rank_text = f"★ New Record! Rank #{last_rank} ★"
            rank_color = GOLD_COLOR
        else:
            rank_text = f"Rank #{last_rank} on the {grid_size}×{grid_size} leaderboard"
            rank_color = HINT_COLOR
        rank_surf = info_font.render(rank_text, True, rank_color)
        screen.blit(rank_surf, rank_surf.get_rect(center=(WIDTH // 2, y)))

    y += 55
    hint = small_font.render(
        "R: play again   |   Esc: back to menu", True, HINT_COLOR)
    screen.blit(hint, hint.get_rect(center=(WIDTH // 2, y)))


def check_win():
    global game_won, final_time, last_rank
    if pairs_found == total_pairs:
        game_won = True
        final_time = pygame.time.get_ticks() - start_time
        last_rank = add_score(
            SCORES, grid_size, player_name or "Player", moves, final_time)


# ============ MAIN LOOP ============
running = True
pygame.key.start_text_input()

while running:
    dt = clock.tick(60)
    cursor_timer += dt
    if cursor_timer >= 500:
        cursor_timer = 0
        cursor_visible = not cursor_visible

    mouse_pos = pygame.mouse.get_pos()
    mouse_clicked = False

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if state == STATE_PLAY:
                    AVAILABLE_IMAGES = scan_images()
                    BACKGROUND = create_background()
                    state = STATE_MENU
                elif state == STATE_SCORES:
                    state = STATE_MENU
                else:
                    running = False
            elif event.key == pygame.K_r and state == STATE_PLAY:
                start_game(grid_size)
            elif state == STATE_MENU and name_input_active:
                if event.key == pygame.K_BACKSPACE:
                    player_name = player_name[:-1]
                elif event.key == pygame.K_RETURN:
                    name_input_active = False
            elif state == STATE_SCORES:
                if pygame.K_1 <= event.key <= pygame.K_4:
                    idx = event.key - pygame.K_1
                    if idx < len(GRID_OPTIONS):
                        scores_view_size = GRID_OPTIONS[idx]

        elif event.type == pygame.TEXTINPUT:
            if state == STATE_MENU and name_input_active:
                if len(player_name) < 15:
                    player_name += event.text
                    cursor_visible = True

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_clicked = True

    if state == STATE_MENU:
        if mouse_clicked:
            if NAME_RECT.collidepoint(mouse_pos):
                name_input_active = True
            else:
                name_input_active = False
                if get_scores_button_rect().collidepoint(mouse_pos):
                    state = STATE_SCORES
                    scores_view_size = 4
                else:
                    for gsize, pairs_needed, rect, playable in get_menu_buttons():
                        if rect.collidepoint(mouse_pos) and playable:
                            start_game(gsize)
                            break
        draw_menu()

    elif state == STATE_SCORES:
        if mouse_clicked:
            clicked_tab = False
            for gsize, rect in get_scores_tab_rects():
                if rect.collidepoint(mouse_pos):
                    scores_view_size = gsize
                    clicked_tab = True
                    break
            if not clicked_tab and get_back_button_rect().collidepoint(mouse_pos):
                state = STATE_MENU
        draw_scores_screen()

    elif state == STATE_PLAY:
        if mouse_clicked and not game_won and second_pick is None:
            for i, card in enumerate(deck):
                rect = get_card_rect(i)
                if rect.collidepoint(mouse_pos) and not card.flipped and not card.matched:
                    card.flipped = True
                    if first_pick is None:
                        first_pick = card
                    else:
                        second_pick = card
                        moves += 1
                        if first_pick.pair_id == second_pick.pair_id:
                            first_pick.matched = True
                            second_pick.matched = True
                            pairs_found += 1
                            first_pick = None
                            second_pick = None
                            check_win()
                        else:
                            mismatch_time = pygame.time.get_ticks()
                    break

        if second_pick is not None:
            if pygame.time.get_ticks() - mismatch_time > MISMATCH_DELAY:
                if first_pick:
                    first_pick.flipped = False
                second_pick.flipped = False
                first_pick = None
                second_pick = None

        screen.blit(BACKGROUND, (0, 0))
        draw_hud()
        for i, card in enumerate(deck):
            rect = get_card_rect(i)
            hovered = (rect.collidepoint(mouse_pos) and not card.flipped
                       and not card.matched and second_pick is None and not game_won)
            draw_card(rect, card, hovered)

        if game_won:
            draw_win_overlay()

    pygame.display.flip()

pygame.quit()
sys.exit()