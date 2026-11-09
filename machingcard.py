import pygame
import sys
import random
import os

pygame.init()

# --- Configuration ---
WIDTH, HEIGHT = 700, 800
MISMATCH_DELAY = 800
GRID_OPTIONS = [4, 6, 8, 10]

# --- Colors ---
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

# --- Fonts ---
menu_title_font = pygame.font.SysFont("arial", 52, bold=True)
menu_btn_font   = pygame.font.SysFont("arial", 32, bold=True)
small_font      = pygame.font.SysFont("arial", 17)
info_font       = pygame.font.SysFont("arial", 22, bold=True)
big_font        = pygame.font.SysFont("arial", 36, bold=True)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Memory Match - Pygame")
clock = pygame.time.Clock()

# --- Load images ---
IMAGES_DIR = "images"

def scan_images():
    """Auto-scan images/ folder for all valid image files."""
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
    print("Place images named like 1.png, 2.jpg, etc. inside the folder.")
    pygame.quit()
    sys.exit(1)

print(f"Loaded {len(AVAILABLE_IMAGES)} images from '{IMAGES_DIR}/' folder.")


# --- Card class ---
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
state = STATE_MENU

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


# --- Menu ---
def get_menu_buttons():
    btn_w, btn_h = 280, 76
    gap = 22
    start_y = 230
    x = (WIDTH - btn_w) // 2
    buttons = []
    for i, gsize in enumerate(GRID_OPTIONS):
        pairs_needed = (gsize * gsize) // 2
        y = start_y + i * (btn_h + gap)
        rect = pygame.Rect(x, y, btn_w, btn_h)
        playable = len(AVAILABLE_IMAGES) >= pairs_needed
        buttons.append((gsize, pairs_needed, rect, playable))
    return buttons


def draw_menu():
    screen.fill(BG_COLOR)

    title = menu_title_font.render("Memory Match", True, TEXT_COLOR)
    screen.blit(title, title.get_rect(center=(WIDTH // 2, 100)))

    subtitle = info_font.render("Select a board size", True, HINT_COLOR)
    screen.blit(subtitle, subtitle.get_rect(center=(WIDTH // 2, 165)))

    mouse = pygame.mouse.get_pos()
    for gsize, pairs_needed, rect, playable in get_menu_buttons():
        if not playable:
            bg = BUTTON_DISABLED
            text_color = BUTTON_TEXT_DISABLED
        elif rect.collidepoint(mouse):
            bg = BUTTON_HOVER
            text_color = BUTTON_TEXT
        else:
            bg = BUTTON_BG
            text_color = BUTTON_TEXT

        pygame.draw.rect(screen, bg, rect, border_radius=12)

        label = f"{gsize} × {gsize}"
        lbl = menu_btn_font.render(label, True, text_color)
        screen.blit(lbl, lbl.get_rect(center=(rect.centerx, rect.centery - 10)))

        if playable:
            sub = small_font.render(f"{pairs_needed} pairs", True, SUB_COLOR_OK)
        else:
            sub = small_font.render(
                f"needs {pairs_needed} images (have {len(AVAILABLE_IMAGES)})",
                True, WARN_COLOR
            )
        screen.blit(sub, sub.get_rect(center=(rect.centerx, rect.centery + 20)))

    footer = small_font.render(
        f"Images loaded: {len(AVAILABLE_IMAGES)}    |    Esc: quit",
        True, HINT_COLOR
    )
    screen.blit(footer, footer.get_rect(center=(WIDTH // 2, HEIGHT - 40)))


# --- Start game ---
def start_game(gsize):
    global grid_size, board_cols, board_rows, card_size, card_gap
    global board_x, board_y, deck, first_pick, second_pick
    global mismatch_time, moves, pairs_found, total_pairs
    global game_won, start_time, final_time, state, qm_surface

    grid_size = gsize
    board_cols = gsize
    board_rows = gsize
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

    # Pre-render "?" for card backs, scaled to card size
    qm_font_size = max(16, card_size // 3)
    qm_font = pygame.font.SysFont("arial", qm_font_size, bold=True)
    qm_surface = qm_font.render("?", True, CARD_BACK_DARK)

    # Build deck with unique pair IDs
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
    state = STATE_PLAY


# --- Rendering helpers ---
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
    else:
        if qm_surface:
            screen.blit(qm_surface, qm_surface.get_rect(center=rect.center))


def format_time(ms):
    s = ms // 1000
    return f"{s // 60:02d}:{s % 60:02d}"


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

    if game_won:
        msg = big_font.render("You Win!", True, WIN_COLOR)
        screen.blit(msg, msg.get_rect(center=(WIDTH // 2, HEIGHT - 60)))
        hint = small_font.render(
            f"Moves: {moves}   |   Time: {format_time(final_time)}   |   R: again   |   Esc: menu",
            True, HINT_COLOR)
        screen.blit(hint, hint.get_rect(center=(WIDTH // 2, HEIGHT - 22)))
    else:
        hint = small_font.render("R: restart  -  Esc: back to menu", True, HINT_COLOR)
        screen.blit(hint, hint.get_rect(center=(WIDTH // 2, HEIGHT - 22)))


# --- Main loop ---
running = True
while running:
    clock.tick(60)
    mouse_pos = pygame.mouse.get_pos()
    mouse_clicked = False

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if state == STATE_PLAY:
                    AVAILABLE_IMAGES = scan_images()  # refresh on return
                    state = STATE_MENU
                else:
                    running = False
            elif event.key == pygame.K_r and state == STATE_PLAY:
                start_game(grid_size)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_clicked = True

    if state == STATE_MENU:
        if mouse_clicked:
            for gsize, pairs_needed, rect, playable in get_menu_buttons():
                if rect.collidepoint(mouse_pos) and playable:
                    start_game(gsize)
                    break
        draw_menu()

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
                            if pairs_found == total_pairs:
                                game_won = True
                                final_time = pygame.time.get_ticks() - start_time
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

    pygame.display.flip()

pygame.quit()
sys.exit()