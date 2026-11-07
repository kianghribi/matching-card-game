import pygame
import sys
import random
import os

pygame.init()

# --- Configuration ---
WIDTH, HEIGHT = 700, 780
GRID_COLS, GRID_ROWS = 4, 4
CARD_SIZE = 140
CARD_GAP = 15
BOARD_WIDTH = GRID_COLS * CARD_SIZE + (GRID_COLS - 1) * CARD_GAP
BOARD_HEIGHT = GRID_ROWS * CARD_SIZE + (GRID_ROWS - 1) * CARD_GAP
BOARD_X = (WIDTH - BOARD_WIDTH) // 2
BOARD_Y = 120
MISMATCH_DELAY = 800  # milliseconds

# --- Images ---
IMAGES_DIR = "images"
NUM_PAIRS = 8
IMAGE_DISPLAY_SIZE = (100, 100)  # size of image inside each card

# --- Colors ---
BG_COLOR            = (28, 30, 48)
CARD_BACK           = (60, 110, 180)
CARD_BACK_DARK      = (40, 80, 140)
CARD_FACE           = (245, 245, 250)
CARD_FACE_BORDER    = (150, 150, 170)
CARD_MATCHED        = (110, 200, 130)
CARD_MATCHED_BORDER = (60, 150, 80)
TEXT_COLOR          = (240, 240, 240)
HOVER_BORDER        = (255, 210, 80)
WIN_COLOR           = (255, 220, 100)
HINT_COLOR          = (180, 200, 255)

# --- Fonts ---
back_font = pygame.font.SysFont("arial", 60, bold=True)
info_font = pygame.font.SysFont("arial", 24, bold=True)
big_font  = pygame.font.SysFont("arial", 44, bold=True)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Memory Match - Pygame")
clock = pygame.time.Clock()


# ---------- Load & prepare images ----------
def load_images():
    """Load card images 1..8, accepting .png / .jpg / .jpeg for each index."""
    surfaces = {}
    missing = []
    for i in range(1, NUM_PAIRS + 1):
        path = None
        for ext in (".png", ".jpg", ".jpeg"):
            candidate = os.path.join(IMAGES_DIR, f"{i}{ext}")
            if os.path.isfile(candidate):
                path = candidate
                break
        if path is None:
            missing.append(f"{i}.(png|jpg|jpeg)")
            continue
        try:
            img = pygame.image.load(path).convert_alpha()
            img = pygame.transform.smoothscale(img, IMAGE_DISPLAY_SIZE)
            surfaces[str(i)] = img
        except Exception as e:
            print(f"Error loading {path}: {e}")
            missing.append(path)

    if missing:
        print("\n⚠️  Missing or invalid images:")
        for m in missing:
            print("   -", m)
        print("\nPlace 8 images numbered 1..8 (.png/.jpg/.jpeg) inside the 'images/' folder.")
        pygame.quit()
        sys.exit(1)

    return surfaces


IMAGE_SURFACES = load_images()
IMAGE_KEYS = list(IMAGE_SURFACES.keys())  # ["1", "2", ..., "8"]


class Card:
    __slots__ = ("image_key", "flipped", "matched")

    def __init__(self, image_key):
        self.image_key = image_key
        self.flipped = False
        self.matched = False


def create_deck():
    deck = []
    for key in IMAGE_KEYS:
        deck.append(Card(key))
        deck.append(Card(key))
    random.shuffle(deck)
    return deck


# --- Game state ---
total_pairs = len(IMAGE_KEYS)
deck = []
first_pick = None
second_pick = None
mismatch_time = 0
moves = 0
pairs_found = 0
game_won = False
start_time = 0
final_time = 0


def reset_game():
    global deck, first_pick, second_pick, mismatch_time
    global moves, pairs_found, game_won, start_time, final_time
    deck = create_deck()
    first_pick = None
    second_pick = None
    mismatch_time = 0
    moves = 0
    pairs_found = 0
    game_won = False
    start_time = pygame.time.get_ticks()
    final_time = 0


def get_card_rect(index):
    row = index // GRID_COLS
    col = index % GRID_COLS
    x = BOARD_X + col * (CARD_SIZE + CARD_GAP)
    y = BOARD_Y + row * (CARD_SIZE + CARD_GAP)
    return pygame.Rect(x, y, CARD_SIZE, CARD_SIZE)


def draw_card(rect, card, hovered):
    if card.matched:
        bg, border, bw = CARD_MATCHED, CARD_MATCHED_BORDER, 3
    elif card.flipped:
        bg, border, bw = CARD_FACE, CARD_FACE_BORDER, 3
    else:
        bg = CARD_BACK
        border = HOVER_BORDER if hovered else CARD_BACK_DARK
        bw = 4 if hovered else 3

    pygame.draw.rect(screen, bg, rect, border_radius=12)
    pygame.draw.rect(screen, border, rect, bw, border_radius=12)

    # Card content
    if card.flipped or card.matched:
        img = IMAGE_SURFACES.get(card.image_key)
        if img is not None:
            screen.blit(img, img.get_rect(center=rect.center))
    else:
        inner = rect.inflate(-40, -40)
        pygame.draw.rect(screen, CARD_BACK_DARK, inner, 2, border_radius=8)
        qm = back_font.render("?", True, CARD_BACK_DARK)
        screen.blit(qm, qm.get_rect(center=rect.center))


def format_time(ms):
    s = ms // 1000
    return f"{s // 60:02d}:{s % 60:02d}"


def draw_hud():
    title = big_font.render("Memory Match", True, TEXT_COLOR)
    screen.blit(title, title.get_rect(center=(WIDTH // 2, 50)))

    moves_text = info_font.render(f"Moves: {moves}", True, TEXT_COLOR)
    pairs_text = info_font.render(f"Pairs: {pairs_found}/{total_pairs}", True, TEXT_COLOR)
    elapsed    = final_time if game_won else (pygame.time.get_ticks() - start_time)
    time_text  = info_font.render(f"Time: {format_time(elapsed)}", True, TEXT_COLOR)

    screen.blit(moves_text, (30, 90))
    screen.blit(pairs_text, (WIDTH // 2 - pairs_text.get_width() // 2, 90))
    screen.blit(time_text, (WIDTH - time_text.get_width() - 30, 90))

    if game_won:
        msg = big_font.render("You Win!", True, WIN_COLOR)
        screen.blit(msg, msg.get_rect(center=(WIDTH // 2, HEIGHT - 65)))
        hint = info_font.render(
            f"Moves: {moves}   |   Time: {format_time(final_time)}   |   Press R to play again",
            True, HINT_COLOR)
        screen.blit(hint, hint.get_rect(center=(WIDTH // 2, HEIGHT - 20)))
    else:
        hint = info_font.render("R: restart   -   Esc: quit", True, HINT_COLOR)
        screen.blit(hint, hint.get_rect(center=(WIDTH // 2, HEIGHT - 25)))


# ---------- Main loop ----------
reset_game()
running = True

while running:
    clock.tick(60)
    mouse_pos = pygame.mouse.get_pos()
    mouse_clicked = False

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                reset_game()
            elif event.key == pygame.K_ESCAPE:
                running = False
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_clicked = True

    # Handle card click
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
                    if first_pick.image_key == second_pick.image_key:
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

    # Mismatch timeout → flip both back
    if second_pick is not None:
        if pygame.time.get_ticks() - mismatch_time > MISMATCH_DELAY:
            if first_pick:
                first_pick.flipped = False
            second_pick.flipped = False
            first_pick = None
            second_pick = None

    # Render
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