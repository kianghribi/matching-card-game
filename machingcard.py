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

# --- Colors ---
WHITE                = (255, 255, 255)
BG_COLOR             = (28, 30, 48)
BUTTON_BG            = (60, 110, 180)
BUTTON_HOVER         = (80, 140, 210)
BUTTON_DISABLED      = (55, 55, 65)
BUTTON_TEXT          = (240, 240, 240)
BUTTON_TEXT_DISABLED = (130, 130, 140)
CARD_BACK            = (60, 110, 180)
CARD_BACK_DARK       = (40, 80, 140)
CARD_FACE            = (245, 245, 250)
CARD_FACE_BORDER     = (150, 150, 170)
CARD_MATCHED         = (110, 200, 130)
CARD_MATCHED_BORDER  = (60, 150, 80)
TEXT_COLOR           = (240, 240, 240)
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
menu_title_font = pygame.font.SysFont("arial", 52, bold=True)
menu_btn_font   = pygame.font.SysFont("arial", 30, bold=True)
small_font      = pygame.font.SysFont("arial", 17)
info_font       = pygame.font.SysFont("arial", 22, bold=True)
big_font        = pygame.font.SysFont("arial", 36, bold=True)
input_font      = pygame.font.SysFont("arial", 24)
score_font      = pygame.font.SysFont("arial", 18)
header_font     = pygame.font.SysFont("arial", 18, bold=True)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Memory Match - Pygame")
clock = pygame.time.Clock()


# --- Helpers ---
def format_time(ms):
    s = ms // 1000
    h = s // 3600
    m = (s % 3600) // 60
    sec = s % 60
    if h > 0:
        return f"{h}:{m:02d}:{sec:02d}"
    return f"{m:02d}:{sec:02d}"


# --- Scores persistence ---
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
    """Add a score and return its rank (1-indexed) or None if not in top N."""
    key = str(gsize)
    entries = scores.get(key, [])
    if not isinstance(entries, list):
        entries = []
    new_entry = {
        "name": name,
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


# --- Images ---
IMAGES_DIR = "images"


def scan_images():
    if not os.path.isdir(IMAGES_DIR):
        return []
    exts = (".png", ".jpg", ".jpeg")
    result = []
    for fname in sorted(os.listdir(IMAGES_DIR)):
        if fname.lower().endswith(exts):
            full = os.path.join(IMAGES_DIR, fname)
            try:
                img = pygame.image.load(full).convert_alpha()
                result.append((fname, img))
            except Exception as e:
                print(f"Skipping invalid image {full}: {e}")
    return result


AVAILABLE_IMAGES = scan_images()
if not AVAILABLE_IMAGES:
    print(f"⚠️  No images found in '{IMAGES_DIR}/' folder.")
    pygame.quit()
    sys.exit(1)
print(f"Loaded {len(AVAILABLE_IMAGES)} images from '{IMAGES_DIR}/' folder.")

SCORES = load_scores()


# --- Card ---
class Card:
    __slots__ = ("pair_id", "image", "flipped", "matched")

    def __init__(self, pair_id, image):
        self.pair_id = pair_id
        self.image = image
        self.flipped = False
        self.matched = False


# --- State ---
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
qm_surface = None
last_rank = None

scores_view_size = 4


# --- UI helpers ---
NAME_RECT = pygame.Rect((WIDTH - 320) // 2, 130, 320, 48)


def get_menu_buttons():
    btn_w, btn_h = 280, 76
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
    return pygame.Rect((WIDTH - 280) // 2, 680, 280, 52)


def get_scores_tab_rects():
    tab_w, tab_h, gap = 130, 42, 12
    total_w = 4 * tab_w + 3 * gap
    start_x = (WIDTH - total_w) // 2
    y = 130
    rects = []
    for i, gsize in enumerate(GRID_OPTIONS):
        x = start_x + i * (tab_w + gap)
        rects.append((gsize, pygame.Rect(x, y, tab_w, tab_h)))
    return rects


def get_back_button_rect():
    return pygame.Rect((WIDTH - 200) // 2, HEIGHT - 80, 200, 52)


# --- Menu drawing ---
def draw_menu():
    screen.fill(BG_COLOR)

    title = menu_title_font.render("Memory Match", True, TEXT_COLOR)
    screen.blit(title, title.get_rect(center=(WIDTH // 2, 60)))

    label = small_font.render("Your name:", True, HINT_COLOR)
    screen.blit(label, (NAME_RECT.x, NAME_RECT.y - 22))

    bg = INPUT_BG_FOCUS if name_input_active else INPUT_BG
    border = INPUT_BORDER_FOCUS if name_input_active else INPUT_BORDER
    pygame.draw.rect(screen, bg, NAME_RECT, border_radius=8)
    pygame.draw.rect(screen, border, NAME_RECT, 2, border_radius=8)

    display = player_name
    if name_input_active and cursor_visible:
        display += "|"
    if not display:
        display = " "
    name_surf = input_font.render(display, True, TEXT_COLOR)
    screen.blit(name_surf, (NAME_RECT.x + 12,
                            NAME_RECT.y + (NAME_RECT.height - name_surf.get_height()) // 2))

    mouse = pygame.mouse.get_pos()
    for gsize, pairs_needed, rect, playable in get_menu_buttons():
        if not playable:
            bg, text_color = BUTTON_DISABLED, BUTTON_TEXT_DISABLED
        elif rect.collidepoint(mouse):
            bg, text_color = BUTTON_HOVER, BUTTON_TEXT
        else:
            bg, text_color = BUTTON_BG, BUTTON_TEXT

        pygame.draw.rect(screen, bg, rect, border_radius=12)
        lbl = menu_btn_font.render(f"{gsize} × {gsize}", True, text_color)
        screen.blit(lbl, lbl.get_rect(center=(rect.centerx, rect.centery - 12)))

        if playable:
            best = get_scores_for(SCORES, gsize)
            if best:
                b = best[0]
                sub_text = f"Best: {b['moves']} moves / {format_time(b['time'])}"
                sub = small_font.render(sub_text, True, GOLD_COLOR)
            else:
                sub = small_font.render(f"{pairs_needed} pairs", True, SUB_COLOR_OK)
        else:
            sub = small_font.render(
                f"needs {pairs_needed} images (have {len(AVAILABLE_IMAGES)})",
                True, WARN_COLOR)
        screen.blit(sub, sub.get_rect(center=(rect.centerx, rect.centery + 18)))

    sb = get_scores_button_rect()
    sb_bg = BUTTON_HOVER if sb.collidepoint(mouse) else BUTTON_BG
    pygame.draw.rect(screen, sb_bg, sb, border_radius=10)
    sb_text = menu_btn_font.render("View Scores", True, WHITE)
    screen.blit(sb_text, sb_text.get_rect(center=sb.center))

    footer = small_font.render(
        f"Images loaded: {len(AVAILABLE_IMAGES)}    |    Esc: quit",
        True, HINT_COLOR)
    screen.blit(footer, footer.get_rect(center=(WIDTH // 2, HEIGHT - 20)))


# --- Scores screen ---
def draw_scores_screen():
    screen.fill(BG_COLOR)

    title = menu_title_font.render("Scoreboard", True, TEXT_COLOR)
    screen.blit(title, title.get_rect(center=(WIDTH // 2, 60)))

    subtitle = small_font.render(
        "Ranked by fewer moves, then less time", True, HINT_COLOR)
    screen.blit(subtitle, subtitle.get_rect(center=(WIDTH // 2, 100)))

    mouse = pygame.mouse.get_pos()

    for gsize, rect in get_scores_tab_rects():
        active = (gsize == scores_view_size)
        hover = rect.collidepoint(mouse)
        if active:
            bg, fg = HOVER_BORDER, (30, 30, 30)
        elif hover:
            bg, fg = BUTTON_HOVER, WHITE
        else:
            bg, fg = BUTTON_BG, WHITE
        pygame.draw.rect(screen, bg, rect, border_radius=8)
        lbl = menu_btn_font.render(f"{gsize}×{gsize}", True, fg)
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

    bb = get_back_button_rect()
    bb_bg = BUTTON_HOVER if bb.collidepoint(mouse) else BUTTON_BG
    pygame.draw.rect(screen, bb_bg, bb, border_radius=10)
    back = menu_btn_font.render("Back to Menu", True, WHITE)
    screen.blit(back, back.get_rect(center=bb.center))


# --- Game ---
def start_game(gsize):
    global grid_size, board_cols, board_rows, card_size, card_gap
    global board_x, board_y, deck, first_pick, second_pick
    global mismatch_time, moves, pairs_found, total_pairs
    global game_won, start_time, final_time, state, qm_surface, last_rank

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

    qm_font = pygame.font.SysFont("arial", max(16, card_size // 3), bold=True)
    qm_surface = qm_font.render("?", True, CARD_BACK_DARK)

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
    radius = max(6, min(12, card_size // 8))
    if card.matched:
        bg, border, bw = CARD_MATCHED, CARD_MATCHED_BORDER, 3
    elif card.flipped:
        bg, border, bw = CARD_FACE, CARD_FACE_BORDER, 3
    else:
        bg = CARD_BACK
        border = HOVER_BORDER if hovered else CARD_BACK_DARK
        bw = 4 if hovered else 3
    pygame.draw.rect(screen, bg, rect, border_radius=radius)
    pygame.draw.rect(screen, border, rect, bw, border_radius=radius)
    if card.flipped or card.matched:
        screen.blit(card.image, card.image.get_rect(center=rect.center))
    elif qm_surface:
        screen.blit(qm_surface, qm_surface.get_rect(center=rect.center))


def draw_hud():
    title = big_font.render(f"Memory Match  -  {grid_size} × {grid_size}", True, TEXT_COLOR)
    screen.blit(title, title.get_rect(center=(WIDTH // 2, 42)))
    moves_text = info_font.render(f"Moves: {moves}", True, TEXT_COLOR)
    pairs_text = info_font.render(f"Pairs: {pairs_found}/{total_pairs}", True, TEXT_COLOR)
    elapsed = final_time if game_won else (pygame.time.get_ticks() - start_time)
    time_text = info_font.render(f"Time: {format_time(elapsed)}", True, TEXT_COLOR)
    screen.blit(moves_text, (30, 82))
    screen.blit(pairs_text, (WIDTH // 2 - pairs_text.get_width() // 2, 82))
    screen.blit(time_text, (WIDTH - time_text.get_width() - 30, 82))
    if not game_won:
        hint = small_font.render("R: restart  -  Esc: back to menu", True, HINT_COLOR)
        screen.blit(hint, hint.get_rect(center=(WIDTH // 2, HEIGHT - 20)))


def draw_win_overlay():
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((20, 20, 30, 200))
    screen.blit(overlay, (0, 0))

    msg = big_font.render("You Win!", True, WIN_COLOR)
    screen.blit(msg, msg.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 100)))

    name_surf = info_font.render(
        f"Congratulations, {player_name or 'Player'}!", True, HINT_COLOR)
    screen.blit(name_surf, name_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 55)))

    stats = info_font.render(
        f"Moves: {moves}   |   Time: {format_time(final_time)}", True, TEXT_COLOR)
    screen.blit(stats, stats.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 5)))

    if last_rank is not None:
        if last_rank == 1:
            rank_text = f"★ New Record! Rank #{last_rank} ★"
            rank_color = GOLD_COLOR
        else:
            rank_text = f"Rank #{last_rank} on the {grid_size}×{grid_size} leaderboard"
            rank_color = HINT_COLOR
        rank_surf = info_font.render(rank_text, True, rank_color)
        screen.blit(rank_surf, rank_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 40)))

    hint = small_font.render(
        "R: play again   |   Esc: back to menu", True, HINT_COLOR)
    screen.blit(hint, hint.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 100)))


def check_win():
    global game_won, final_time, last_rank
    if pairs_found == total_pairs:
        game_won = True
        final_time = pygame.time.get_ticks() - start_time
        last_rank = add_score(
            SCORES, grid_size, player_name or "Player", moves, final_time)


# --- Main loop ---
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

        screen.fill(BG_COLOR)
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