import pygame
import sys
import random
from dataclasses import dataclass

pygame.init()

CELL = 24
COLS = 10
ROWS = 20

PANEL_W = 220
WIDTH = COLS * CELL + PANEL_W
HEIGHT = ROWS * CELL

screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.SCALED)
pygame.display.set_caption("TETRIS • Modern Neon Deluxe (Smaller)")
clock = pygame.time.Clock()

FONT = pygame.font.SysFont("consolas", 18)
MID_FONT = pygame.font.SysFont("consolas", 24, bold=True)
BIG_FONT = pygame.font.SysFont("consolas", 46, bold=True)

BLACK = (6, 6, 12)
PANEL_BG = (12, 12, 22)
GLASS = (18, 18, 35)
WHITE = (245, 245, 255)
GRID_LINE = (42, 42, 75)

NEON = {
    "I": (0, 255, 255),
    "O": (255, 255, 0),
    "T": (210, 0, 255),
    "S": (0, 255, 120),
    "Z": (255, 60, 120),
    "J": (80, 140, 255),
    "L": (255, 160, 0),
    "GHOST": (200, 200, 220),
}

SHAPES = {
    "I": [
        [(0, 1), (1, 1), (2, 1), (3, 1)],
        [(2, 0), (2, 1), (2, 2), (2, 3)],
        [(0, 2), (1, 2), (2, 2), (3, 2)],
        [(1, 0), (1, 1), (1, 2), (1, 3)],
    ],
    "O": [
        [(1, 0), (2, 0), (1, 1), (2, 1)],
        [(1, 0), (2, 0), (1, 1), (2, 1)],
        [(1, 0), (2, 0), (1, 1), (2, 1)],
        [(1, 0), (2, 0), (1, 1), (2, 1)],
    ],
    "T": [
        [(1, 0), (0, 1), (1, 1), (2, 1)],
        [(1, 0), (1, 1), (2, 1), (1, 2)],
        [(0, 1), (1, 1), (2, 1), (1, 2)],
        [(1, 0), (0, 1), (1, 1), (1, 2)],
    ],
    "S": [
        [(1, 0), (2, 0), (0, 1), (1, 1)],
        [(1, 0), (1, 1), (2, 1), (2, 2)],
        [(1, 1), (2, 1), (0, 2), (1, 2)],
        [(0, 0), (0, 1), (1, 1), (1, 2)],
    ],
    "Z": [
        [(0, 0), (1, 0), (1, 1), (2, 1)],
        [(2, 0), (1, 1), (2, 1), (1, 2)],
        [(0, 1), (1, 1), (1, 2), (2, 2)],
        [(1, 0), (0, 1), (1, 1), (0, 2)],
    ],
    "J": [
        [(0, 0), (0, 1), (1, 1), (2, 1)],
        [(1, 0), (2, 0), (1, 1), (1, 2)],
        [(0, 1), (1, 1), (2, 1), (2, 2)],
        [(1, 0), (1, 1), (0, 2), (1, 2)],
    ],
    "L": [
        [(2, 0), (0, 1), (1, 1), (2, 1)],
        [(1, 0), (1, 1), (1, 2), (2, 2)],
        [(0, 1), (1, 1), (2, 1), (0, 2)],
        [(0, 0), (1, 0), (1, 1), (1, 2)],
    ],
}

def clamp(v, lo, hi):
    return max(lo, min(hi, v))

def lighten(c, amt=55):
    r, g, b = c
    return (clamp(r + amt, 0, 255), clamp(g + amt, 0, 255), clamp(b + amt, 0, 255))

def darken(c, amt=95):
    r, g, b = c
    return (clamp(r - amt, 0, 255), clamp(g - amt, 0, 255), clamp(b - amt, 0, 255))

@dataclass
class Piece:
    kind: str
    x: int
    y: int
    rot: int = 0
    def cells(self):
        return [(self.x + cx, self.y + cy) for cx, cy in SHAPES[self.kind][self.rot]]

def empty_board():
    return [[None for _ in range(COLS)] for _ in range(ROWS)]

def in_bounds(x, y):
    return 0 <= x < COLS and y < ROWS

def valid(piece, board):
    for x, y in piece.cells():
        if not in_bounds(x, y):
            return False
        if y >= 0 and board[y][x] is not None:
            return False
    return True

def lock_piece(piece, board):
    for x, y in piece.cells():
        if y >= 0:
            board[y][x] = piece.kind

def clear_lines(board):
    full_rows = [i for i, row in enumerate(board) if all(cell is not None for cell in row)]
    if not full_rows:
        return board, 0, []
    new_board = [row for row in board if any(cell is None for cell in row)]
    cleared = ROWS - len(new_board)
    while len(new_board) < ROWS:
        new_board.insert(0, [None for _ in range(COLS)])
    return new_board, cleared, full_rows

def new_bag():
    bag = list(SHAPES.keys())
    random.shuffle(bag)
    return bag

def spawn_piece(kind):
    return Piece(kind=kind, x=3, y=-2, rot=0)

def get_drop_y(piece, board):
    ghost = Piece(piece.kind, piece.x, piece.y, piece.rot)
    while True:
        ghost.y += 1
        if not valid(ghost, board):
            ghost.y -= 1
            break
    return ghost.y

def fall_speed_ms(level, speed_multiplier=1.0):
    base = max(65, 720 - (level - 1) * 55)
    return int(base / speed_multiplier)

def scoring_for_lines(cleared, level):
    if cleared == 1: return 100 * level
    if cleared == 2: return 300 * level
    if cleared == 3: return 500 * level
    if cleared == 4: return 800 * level
    return 0

def is_tetris(cleared):
    return cleared == 4

def glow_circle(surface, x, y, radius, color, alpha):
    pygame.draw.circle(surface, (*color, alpha), (int(x), int(y)), int(radius))

def draw_background_glow():
    glow = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    glow_circle(glow, 95, 120, 120, (0, 255, 255), 38)
    glow_circle(glow, 160, 360, 160, (210, 0, 255), 32)
    glow_circle(glow, 360, 220, 160, (0, 255, 120), 28)
    glow_circle(glow, 430, 460, 180, (255, 60, 120), 20)
    screen.blit(glow, (0, 0))

def neon_text(text, font, x, y, color):
    shadow = font.render(text, True, color)
    glow = pygame.Surface((shadow.get_width() + 14, shadow.get_height() + 14), pygame.SRCALPHA)
    glow.blit(shadow, (7, 7))
    for _ in [28, 18]:
        screen.blit(glow, (x - 7, y - 7))
    screen.blit(font.render(text, True, WHITE), (x, y))

def draw_glass_playfield():
    rect = pygame.Rect(0, 0, COLS * CELL, HEIGHT)
    glass = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    glass.fill((*GLASS, 220))
    screen.blit(glass, rect.topleft)
    pygame.draw.rect(screen, (0, 255, 255), rect, 2, border_radius=8)

def draw_grid():
    for x in range(COLS + 1):
        pygame.draw.line(screen, GRID_LINE, (x * CELL, 0), (x * CELL, HEIGHT), 1)
    for y in range(ROWS + 1):
        pygame.draw.line(screen, GRID_LINE, (0, y * CELL), (COLS * CELL, y * CELL), 1)

def draw_block_neon(px, py, color, alpha=255):
    glow = pygame.Surface((CELL * 3, CELL * 3), pygame.SRCALPHA)
    gx, gy = CELL, CELL
    for r, a in [(14, 28), (9, 40)]:
        pygame.draw.rect(
            glow,
            (*color, int(a * (alpha / 255))),
            (gx - r // 2, gy - r // 2, CELL + r, CELL + r),
            border_radius=10
        )
    screen.blit(glow, (px - CELL, py - CELL))

    surf = pygame.Surface((CELL, CELL), pygame.SRCALPHA)
    surf.fill((*color, alpha))

    top = lighten(color, 60)
    bottom = darken(color, 100)

    pygame.draw.polygon(surf, (*top, alpha), [(0, 0), (CELL, 0), (CELL - 5, 5), (5, 5)])
    pygame.draw.polygon(surf, (*bottom, alpha), [(0, CELL), (CELL, CELL), (CELL - 5, CELL - 5), (5, CELL - 5)])

    pygame.draw.rect(surf, (255, 255, 255, 70), (3, 3, CELL - 6, CELL - 6), 2)
    pygame.draw.rect(surf, (0, 0, 0, 140), (0, 0, CELL, CELL), 2)
    screen.blit(surf, (px, py))

def draw_board(board):
    for y in range(ROWS):
        for x in range(COLS):
            kind = board[y][x]
            if kind:
                draw_block_neon(x * CELL, y * CELL, NEON[kind])

def draw_piece(piece, color, alpha=255):
    for x, y in piece.cells():
        if y >= 0:
            draw_block_neon(x * CELL, y * CELL, color, alpha)

def draw_mini_piece(px, py, kind, scale=0.7):
    mini_cell = int(CELL * scale)
    coords = SHAPES[kind][0]
    minx = min(c[0] for c in coords)
    miny = min(c[1] for c in coords)
    coords = [(c[0] - minx, c[1] - miny) for c in coords]

    for cx, cy in coords:
        x = px + cx * mini_cell
        y = py + cy * mini_cell
        surf = pygame.Surface((mini_cell, mini_cell), pygame.SRCALPHA)
        col = NEON[kind]
        surf.fill((*col, 255))
        pygame.draw.rect(surf, (255, 255, 255, 110), (3, 3, mini_cell - 6, mini_cell - 6), 2)
        pygame.draw.rect(surf, (0, 0, 0, 140), (0, 0, mini_cell, mini_cell), 2)
        screen.blit(surf, (x, y))

def draw_panel(score, level, lines, hold, next_queue, paused, combo, b2b):
    px = COLS * CELL
    pygame.draw.rect(screen, PANEL_BG, (px, 0, PANEL_W, HEIGHT))
    pygame.draw.line(screen, (0, 255, 255), (px, 0), (px, HEIGHT), 2)

    neon_text("TETRIS", BIG_FONT, px + 22, 14, (0, 255, 255))

    screen.blit(FONT.render(f"Score: {score}", True, WHITE), (px + 16, 92))
    screen.blit(FONT.render(f"Level: {level}", True, WHITE), (px + 16, 118))
    screen.blit(FONT.render(f"Lines: {lines}", True, WHITE), (px + 16, 144))
    screen.blit(FONT.render(f"Combo: {combo}", True, WHITE), (px + 16, 170))
    screen.blit(FONT.render(f"B2B: {'ON' if b2b else 'OFF'}", True, WHITE), (px + 16, 196))

    screen.blit(FONT.render("Hold:", True, WHITE), (px + 16, 235))
    if hold:
        draw_mini_piece(px + 26, 262, hold)

    screen.blit(FONT.render("Next:", True, WHITE), (px + 16, 340))
    if next_queue:
        draw_mini_piece(px + 26, 370, next_queue[0], scale=0.78)

    if paused:
        overlay = pygame.Surface((COLS * CELL, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 170))
        screen.blit(overlay, (0, 0))
        neon_text("PAUSED", BIG_FONT, 55, HEIGHT // 2 - 55, (210, 0, 255))

class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.vx = random.uniform(-2.0, 2.0)
        self.vy = random.uniform(-4.0, -1.0)
        self.life = random.randint(22, 40)
        self.color = color

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.20
        self.life -= 1

    def draw(self):
        if self.life <= 0:
            return
        a = clamp(self.life * 6, 0, 170)
        p = pygame.Surface((10, 10), pygame.SRCALPHA)
        pygame.draw.circle(p, (*self.color, a), (5, 5), 4)
        screen.blit(p, (self.x, self.y))

JLSTZ_KICKS = {
    (0, 1): [(0,0), (-1,0), (-1,1), (0,-2), (-1,-2)],
    (1, 0): [(0,0), (1,0), (1,-1), (0,2), (1,2)],
    (1, 2): [(0,0), (1,0), (1,-1), (0,2), (1,2)],
    (2, 1): [(0,0), (-1,0), (-1,1), (0,-2), (-1,-2)],
    (2, 3): [(0,0), (1,0), (1,1), (0,-2), (1,-2)],
    (3, 2): [(0,0), (-1,0), (-1,-1), (0,2), (-1,2)],
    (3, 0): [(0,0), (-1,0), (-1,-1), (0,2), (-1,2)],
    (0, 3): [(0,0), (1,0), (1,1), (0,-2), (1,-2)],
}
I_KICKS = {
    (0, 1): [(0,0), (-2,0), (1,0), (-2,-1), (1,2)],
    (1, 0): [(0,0), (2,0), (-1,0), (2,1), (-1,-2)],
    (1, 2): [(0,0), (-1,0), (2,0), (-1,2), (2,-1)],
    (2, 1): [(0,0), (1,0), (-2,0), (1,-2), (-2,1)],
    (2, 3): [(0,0), (2,0), (-1,0), (2,1), (-1,-2)],
    (3, 2): [(0,0), (-2,0), (1,0), (-2,-1), (1,2)],
    (3, 0): [(0,0), (1,0), (-2,0), (1,-2), (-2,1)],
    (0, 3): [(0,0), (-1,0), (2,0), (-1,2), (2,-1)],
}

def srs_kicks(kind, old_rot, new_rot):
    if kind == "O":
        return [(0, 0)]
    if kind == "I":
        return I_KICKS.get((old_rot, new_rot), [(0, 0)])
    return JLSTZ_KICKS.get((old_rot, new_rot), [(0, 0)])

STATE_MENU = "menu"
STATE_CONTROLS = "controls"
STATE_PLAYING = "playing"

def draw_menu(selected, speed_name):
    screen.fill(BLACK)
    draw_background_glow()
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 170))
    screen.blit(overlay, (0, 0))

    neon_text("TETRIS", BIG_FONT, 90, 70, (0, 255, 255))
    neon_text("Modern Neon Deluxe", MID_FONT, 90, 125, (210, 0, 255))

    options = ["PLAY", "CONTROLS", "QUIT"]
    y = 210
    for i, opt in enumerate(options):
        col = (0, 255, 255) if i == selected else (200, 200, 230)
        neon_text(opt, MID_FONT, 120, y, col)
        y += 52

    neon_text(f"Speed: {speed_name}  (Press D to toggle)", FONT, 90, 420, (255, 255, 0))
    neon_text("Use ↑/↓ then ENTER", FONT, 125, 460, (200, 200, 230))
    pygame.display.flip()

def draw_controls():
    screen.fill(BLACK)
    draw_background_glow()

    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 175))
    screen.blit(overlay, (0, 0))

    neon_text("CONTROLS", BIG_FONT, 90, 50, (0, 255, 255))

    lines = [
        "← / →     Move left / right",
        "↓         Soft drop",
        "SPACE     Hard drop",
        "↑         Rotate clockwise",
        "Z         Rotate counter-clockwise",
        "C         Hold piece",
        "P         Pause",
        "H         Toggle controls overlay",
        "ESC       Menu / Back",
        "",
        "Press BACKSPACE to return"
    ]

    y = 150
    for line in lines:
        screen.blit(FONT.render(line, True, WHITE), (70, y))
        y += 28

    pygame.display.flip()

def run_game(speed_multiplier):
    board = empty_board()
    particles = []

    bag = new_bag()
    next_queue = []
    while len(next_queue) < 6:
        if not bag:
            bag = new_bag()
        next_queue.append(bag.pop())

    current = spawn_piece(next_queue.pop(0))
    if not bag:
        bag = new_bag()
    next_queue.append(bag.pop())

    hold = None
    can_hold = True

    score = 0
    level = 1
    total_lines = 0
    combo = 0
    b2b = False

    fall_timer = 0
    soft_drop = False
    paused = False

    flash_lines = []
    flash_timer = 0

    show_controls_overlay = False

    def try_rotate(dir_):
        nonlocal current
        old_rot = current.rot
        new_rot = (current.rot + dir_) % 4
        rotated = Piece(current.kind, current.x, current.y, new_rot)
        if valid(rotated, board):
            current = rotated
            return True
        for dx, dy in srs_kicks(current.kind, old_rot, new_rot):
            kicked = Piece(current.kind, current.x + dx, current.y + dy, new_rot)
            if valid(kicked, board):
                current = kicked
                return True
        return False

    def try_move(dx, dy):
        nonlocal current
        moved = Piece(current.kind, current.x + dx, current.y + dy, current.rot)
        if valid(moved, board):
            current = moved
            return True
        return False

    def spawn_next():
        nonlocal current, next_queue, bag
        current = spawn_piece(next_queue.pop(0))
        if not bag:
            bag = new_bag()
        next_queue.append(bag.pop())
        return valid(current, board)

    def apply_clear_effect(lines_):
        for _ in range(55):
            px = random.randint(10, COLS * CELL - 10)
            py = random.choice(lines_) * CELL + random.randint(0, CELL)
            particles.append(Particle(px, py, (0, 255, 255)))

    def handle_line_clear(cleared, lines_cleared):
        nonlocal score, combo, b2b, total_lines, level, flash_lines, flash_timer
        if cleared > 0:
            combo += 1
            total_lines += cleared
            level = 1 + total_lines // 10

            base_points = scoring_for_lines(cleared, level)
            combo_bonus = 50 * (combo - 1) * level if combo > 1 else 0

            if is_tetris(cleared):
                if b2b:
                    base_points = int(base_points * 1.5)
                b2b = True
            else:
                b2b = False

            score += base_points + combo_bonus

            flash_lines = lines_cleared[:]
            flash_timer = 130
            apply_clear_effect(lines_cleared)
        else:
            combo = 0

    def hard_drop():
        nonlocal current, score, can_hold
        drop_y = get_drop_y(current, board)
        distance = drop_y - current.y
        current.y = drop_y
        score += distance * 2

        if any(y < 0 for _, y in current.cells()):
            return False

        lock_piece(current, board)
        board2, cleared, lines_cleared = clear_lines(board)
        board[:] = board2
        handle_line_clear(cleared, lines_cleared)

        can_hold = True
        ok = spawn_next()
        return ok

    game_over = False
    running = True

    while running:
        dt = clock.tick(60)
        fall_timer += dt

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return "menu"

                if event.key == pygame.K_h:
                    show_controls_overlay = not show_controls_overlay

                if event.key == pygame.K_p:
                    paused = not paused

                if game_over:
                    if event.key == pygame.K_r:
                        return "restart"
                    continue

                if paused or show_controls_overlay:
                    continue

                if event.key == pygame.K_LEFT:
                    try_move(-1, 0)
                elif event.key == pygame.K_RIGHT:
                    try_move(1, 0)
                elif event.key == pygame.K_DOWN:
                    soft_drop = True
                elif event.key == pygame.K_UP:
                    try_rotate(1)
                elif event.key == pygame.K_z:
                    try_rotate(-1)
                elif event.key == pygame.K_SPACE:
                    ok = hard_drop()
                    if not ok:
                        game_over = True
                elif event.key == pygame.K_c:
                    if can_hold:
                        can_hold = False
                        if hold is None:
                            hold = current.kind
                            ok = spawn_next()
                            if not ok:
                                game_over = True
                        else:
                            hold, current.kind = current.kind, hold
                            current.x, current.y, current.rot = 3, -2, 0
                            if not valid(current, board):
                                game_over = True

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_DOWN:
                    soft_drop = False

        if not paused and not game_over and not show_controls_overlay:
            speed = fall_speed_ms(level, speed_multiplier=speed_multiplier)
            if soft_drop:
                speed = max(30, speed // 10)

            if fall_timer >= speed:
                fall_timer = 0
                if not try_move(0, 1):
                    if any(y < 0 for _, y in current.cells()):
                        game_over = True
                    else:
                        lock_piece(current, board)
                        board2, cleared, lines_cleared = clear_lines(board)
                        board[:] = board2
                        handle_line_clear(cleared, lines_cleared)
                        can_hold = True
                        ok = spawn_next()
                        if not ok:
                            game_over = True

        screen.fill(BLACK)
        draw_background_glow()
        draw_glass_playfield()
        draw_grid()
        draw_board(board)

        if flash_timer > 0 and flash_lines:
            flash_timer -= dt
            flash = pygame.Surface((COLS * CELL, CELL), pygame.SRCALPHA)
            flash.fill((255, 255, 255, 110))
            for ly in flash_lines:
                screen.blit(flash, (0, ly * CELL))

        for p in particles[:]:
            p.update()
            p.draw()
            if p.life <= 0:
                particles.remove(p)

        if not game_over:
            ghost_y = get_drop_y(current, board)
            ghost = Piece(current.kind, current.x, ghost_y, current.rot)
            draw_piece(ghost, NEON["GHOST"], alpha=55)
            draw_piece(current, NEON[current.kind])

        draw_panel(score, level, total_lines, hold, next_queue, paused, combo, b2b)

        if show_controls_overlay:
            overlay = pygame.Surface((COLS * CELL, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 185))
            screen.blit(overlay, (0, 0))
            neon_text("CONTROLS", BIG_FONT, 35, 50, (0, 255, 255))
            lines = [
                "←/→ Move",
                "↓ Soft Drop",
                "SPACE Hard Drop",
                "↑ Rotate",
                "Z Rotate Back",
                "C Hold",
                "P Pause",
                "H Close",
                "ESC Menu",
            ]
            y = 135
            for line in lines:
                screen.blit(MID_FONT.render(line, True, WHITE), (50, y))
                y += 34

        if game_over:
            overlay = pygame.Surface((COLS * CELL, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 190))
            screen.blit(overlay, (0, 0))
            neon_text("GAME OVER", BIG_FONT, 35, HEIGHT // 2 - 80, (255, 60, 120))
            screen.blit(FONT.render("Press R to Restart", True, WHITE), (52, HEIGHT // 2 - 10))
            screen.blit(FONT.render("ESC to Menu", True, WHITE), (78, HEIGHT // 2 + 18))

        pygame.display.flip()

def main():
    state = STATE_MENU
    menu_selected = 0

    speed_modes = [
        ("Normal", 1.0),
        ("Fast", 1.25),
        ("Insane", 1.5),
    ]
    speed_idx = 0

    while True:
        if state == STATE_MENU:
            draw_menu(menu_selected, speed_modes[speed_idx][0])

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()

                    if event.key == pygame.K_UP:
                        menu_selected = (menu_selected - 1) % 3
                    elif event.key == pygame.K_DOWN:
                        menu_selected = (menu_selected + 1) % 3
                    elif event.key == pygame.K_d:
                        speed_idx = (speed_idx + 1) % len(speed_modes)

                    elif event.key == pygame.K_RETURN:
                        if menu_selected == 0:
                            state = STATE_PLAYING
                        elif menu_selected == 1:
                            state = STATE_CONTROLS
                        elif menu_selected == 2:
                            pygame.quit()
                            sys.exit()

        elif state == STATE_CONTROLS:
            draw_controls()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key in (pygame.K_BACKSPACE, pygame.K_ESCAPE):
                        state = STATE_MENU

        elif state == STATE_PLAYING:
            speed_multiplier = speed_modes[speed_idx][1]
            result = run_game(speed_multiplier)
            if result == "quit":
                pygame.quit()
                sys.exit()
            if result == "restart":
                state = STATE_PLAYING
            else:
                state = STATE_MENU

if __name__ == "__main__":
    main()
