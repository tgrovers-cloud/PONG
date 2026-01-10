import pygame
import sys
import random
import math
from array import array

pygame.init()
pygame.mixer.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("PONG - Single Player")

clock = pygame.time.Clock()

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (20, 120, 20)
RED = (220, 50, 50)

title_font = pygame.font.SysFont(None, 80)
menu_font = pygame.font.SysFont(None, 50)
small_font = pygame.font.SysFont(None, 36)
score_font = pygame.font.SysFont(None, 50)
game_over_font = pygame.font.SysFont(None, 70)
countdown_font = pygame.font.SysFont(None, 120)

WIN_SCORE = 5

paddle_width = 10
paddle_height = 100
player_speed = 6

BASE_BALL_SPEED_X = 5
MAX_BALL_SPEED_Y = 9
BALL_SPEEDUP_FACTOR = 1.05
MAX_BALL_SPEED_X = 12

left_paddle = pygame.Rect(20, HEIGHT // 2 - paddle_height // 2, paddle_width, paddle_height)
right_paddle = pygame.Rect(WIDTH - 30, HEIGHT // 2 - paddle_height // 2, paddle_width, paddle_height)

ball_size = 15
ball = pygame.Rect(WIDTH // 2, HEIGHT // 2, ball_size, ball_size)

ball_speed_x = BASE_BALL_SPEED_X
ball_speed_y = random.choice([-4, -3, 3, 4])

left_score = 0
right_score = 0

ai_speed = 4
difficulty_name = ""
ai_error = 60
ai_delay_frames = 6
ai_frame_counter = 0

STATE_MENU = "menu"
STATE_COUNTDOWN = "countdown"
STATE_PLAYING = "playing"
STATE_PAUSED = "paused"
STATE_GAME_OVER = "game_over"

game_state = STATE_MENU
winner_text = ""

countdown_value = 3
countdown_last_tick = 0
serve_direction = 1

COURT_MARGIN = 18
COURT_LINE_THICKNESS = 4
CENTER_LINE_THICKNESS = 4
CENTER_CIRCLE_RADIUS = 70
HUD_PAD = 10


def make_beep(freq=440, duration=0.08, volume=0.35, sample_rate=44100):
    n_samples = int(sample_rate * duration)
    buf = array("h")
    amplitude = int(32767 * volume)
    for i in range(n_samples):
        t = i / sample_rate
        sample = int(amplitude * math.sin(2 * math.pi * freq * t))
        buf.append(sample)
    return pygame.mixer.Sound(buffer=buf.tobytes())


sound_paddle = make_beep(880, 0.06, 0.35)
sound_wall = make_beep(660, 0.05, 0.30)
sound_score = make_beep(330, 0.10, 0.40)
sound_win = make_beep(990, 0.20, 0.45)
sound_lose = make_beep(220, 0.20, 0.45)


def draw_court():
    pygame.draw.rect(
        screen,
        WHITE,
        (COURT_MARGIN, COURT_MARGIN, WIDTH - 2 * COURT_MARGIN, HEIGHT - 2 * COURT_MARGIN),
        COURT_LINE_THICKNESS
    )

    pygame.draw.line(
        screen,
        WHITE,
        (WIDTH // 2, COURT_MARGIN),
        (WIDTH // 2, HEIGHT - COURT_MARGIN),
        CENTER_LINE_THICKNESS
    )

    pygame.draw.circle(
        screen,
        WHITE,
        (WIDTH // 2, HEIGHT // 2),
        CENTER_CIRCLE_RADIUS,
        COURT_LINE_THICKNESS
    )


def clamp_paddle(paddle):
    if paddle.top < COURT_MARGIN + COURT_LINE_THICKNESS:
        paddle.top = COURT_MARGIN + COURT_LINE_THICKNESS
    if paddle.bottom > HEIGHT - (COURT_MARGIN + COURT_LINE_THICKNESS):
        paddle.bottom = HEIGHT - (COURT_MARGIN + COURT_LINE_THICKNESS)


def reset_positions(direction=1):
    global ball_speed_x, ball_speed_y, ai_frame_counter, serve_direction

    left_paddle.y = HEIGHT // 2 - paddle_height // 2
    right_paddle.y = HEIGHT // 2 - paddle_height // 2
    ball.center = (WIDTH // 2, HEIGHT // 2)

    serve_direction = direction
    ball_speed_x = direction * BASE_BALL_SPEED_X
    ball_speed_y = random.choice([-4, -3, 3, 4])

    ai_frame_counter = 0


def set_state(new_state):
    global game_state
    game_state = new_state


def start_countdown(direction=1):
    global countdown_value, countdown_last_tick
    reset_positions(direction)
    countdown_value = 3
    countdown_last_tick = pygame.time.get_ticks()
    set_state(STATE_COUNTDOWN)


def reset_match():
    global left_score, right_score, winner_text
    left_score = 0
    right_score = 0
    winner_text = ""
    start_countdown(direction=random.choice([-1, 1]))


def apply_difficulty(level):
    global ai_speed, ai_error, ai_delay_frames, difficulty_name

    if level == 1:
        difficulty_name = "Beginner"
        ai_speed = 4
        ai_error = 60
        ai_delay_frames = 6

    elif level == 2:
        difficulty_name = "Intermediate"
        ai_speed = 6
        ai_error = 30
        ai_delay_frames = 3

    elif level == 3:
        difficulty_name = "Expert"
        ai_speed = 9
        ai_error = 10
        ai_delay_frames = 1


def bounce_ball_off_paddle(paddle, direction):
    global ball_speed_x, ball_speed_y

    speed_x = min(abs(ball_speed_x) * BALL_SPEEDUP_FACTOR, MAX_BALL_SPEED_X)
    ball_speed_x = direction * speed_x

    hit_pos = (ball.centery - paddle.centery) / (paddle_height / 2)
    hit_pos = max(-1, min(1, hit_pos))

    ball_speed_y = hit_pos * MAX_BALL_SPEED_Y

    if direction == 1:
        ball.left = paddle.right
    else:
        ball.right = paddle.left

    sound_paddle.play()


def draw_hud():
    score_text = score_font.render(f"{left_score}  :  {right_score}", True, WHITE)
    diff_text = small_font.render(f"Difficulty: {difficulty_name}", True, WHITE)
    controls_text = small_font.render("Controls: W/S or ↑/↓   |   P = Pause", True, WHITE)

    hud_w = max(score_text.get_width(), diff_text.get_width()) + 2 * HUD_PAD
    hud_h = score_text.get_height() + diff_text.get_height() + 3 * HUD_PAD

    hud_x = WIDTH // 2 - hud_w // 2
    hud_y = COURT_MARGIN + 10

    pygame.draw.rect(screen, BLACK, (hud_x, hud_y, hud_w, hud_h))
    pygame.draw.rect(screen, WHITE, (hud_x, hud_y, hud_w, hud_h), 2)

    screen.blit(score_text, (hud_x + HUD_PAD, hud_y + HUD_PAD))
    screen.blit(diff_text, (hud_x + HUD_PAD, hud_y + HUD_PAD + score_text.get_height() + 6))

    screen.blit(controls_text, (COURT_MARGIN, HEIGHT - COURT_MARGIN - controls_text.get_height()))


def draw_menu():
    screen.fill(GREEN)
    draw_court()

    title = title_font.render("PONG", True, WHITE)
    subtitle = small_font.render("Select Difficulty", True, WHITE)

    option1 = menu_font.render("1 - Beginner", True, WHITE)
    option2 = menu_font.render("2 - Intermediate", True, WHITE)
    option3 = menu_font.render("3 - Expert", True, WHITE)

    hint = small_font.render("Press 1, 2, or 3 to start", True, WHITE)

    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 110))
    screen.blit(subtitle, (WIDTH // 2 - subtitle.get_width() // 2, 200))

    screen.blit(option1, (WIDTH // 2 - option1.get_width() // 2, 280))
    screen.blit(option2, (WIDTH // 2 - option2.get_width() // 2, 340))
    screen.blit(option3, (WIDTH // 2 - option3.get_width() // 2, 400))

    screen.blit(hint, (WIDTH // 2 - hint.get_width() // 2, 490))

    pygame.display.flip()


def draw_game(extra_line=""):
    screen.fill(GREEN)
    draw_court()

    pygame.draw.rect(screen, RED, left_paddle)
    pygame.draw.rect(screen, BLACK, right_paddle)
    pygame.draw.ellipse(screen, WHITE, ball)

    draw_hud()

    if extra_line:
        extra_text = small_font.render(extra_line, True, WHITE)
        screen.blit(extra_text, (WIDTH // 2 - extra_text.get_width() // 2, HEIGHT - COURT_MARGIN - 70))

    pygame.display.flip()


def draw_countdown():
    draw_game()
    text = countdown_font.render(str(countdown_value), True, WHITE)
    screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - text.get_height() // 2))
    pygame.display.flip()


def draw_paused():
    draw_game("PAUSED")
    overlay = small_font.render("Press P to Resume", True, WHITE)
    screen.blit(overlay, (WIDTH // 2 - overlay.get_width() // 2, HEIGHT // 2 + 80))
    pygame.display.flip()


def draw_game_over():
    screen.fill(GREEN)
    draw_court()

    game_over_title = game_over_font.render("GAME OVER", True, WHITE)
    winner_line = menu_font.render(winner_text, True, WHITE)

    option_restart = small_font.render("Press R to Restart", True, WHITE)
    option_menu = small_font.render("Press M for Main Menu", True, WHITE)
    option_quit = small_font.render("Press ESC to Quit", True, WHITE)

    screen.blit(game_over_title, (WIDTH // 2 - game_over_title.get_width() // 2, 140))
    screen.blit(winner_line, (WIDTH // 2 - winner_line.get_width() // 2, 240))

    screen.blit(option_restart, (WIDTH // 2 - option_restart.get_width() // 2, 360))
    screen.blit(option_menu, (WIDTH // 2 - option_menu.get_width() // 2, 410))
    screen.blit(option_quit, (WIDTH // 2 - option_quit.get_width() // 2, 460))

    pygame.display.flip()


def update_ai():
    global ai_frame_counter
    ai_frame_counter += 1

    if ball_speed_x > 0:
        if ai_frame_counter % ai_delay_frames == 0:
            target_y = ball.centery + random.randint(-ai_error, ai_error)

            if target_y > right_paddle.centery:
                right_paddle.y += ai_speed
            elif target_y < right_paddle.centery:
                right_paddle.y -= ai_speed

    clamp_paddle(right_paddle)


def update_ball_and_collisions():
    global ball_speed_y, winner_text, left_score, right_score

    ball.x += ball_speed_x
    ball.y += ball_speed_y

    top_limit = COURT_MARGIN + COURT_LINE_THICKNESS
    bottom_limit = HEIGHT - (COURT_MARGIN + COURT_LINE_THICKNESS)

    if ball.top <= top_limit:
        ball.top = top_limit
        ball_speed_y *= -1
        sound_wall.play()

    if ball.bottom >= bottom_limit:
        ball.bottom = bottom_limit
        ball_speed_y *= -1
        sound_wall.play()

    if ball.colliderect(left_paddle):
        bounce_ball_off_paddle(left_paddle, direction=1)

    if ball.colliderect(right_paddle):
        bounce_ball_off_paddle(right_paddle, direction=-1)

    if ball.left <= 0:
        right_score += 1
        sound_score.play()

        if right_score >= WIN_SCORE:
            winner_text = "AI Wins!"
            sound_lose.play()
            set_state(STATE_GAME_OVER)
        else:
            start_countdown(direction=1)

    if ball.right >= WIDTH:
        left_score += 1
        sound_score.play()

        if left_score >= WIN_SCORE:
            winner_text = "You Win!"
            sound_win.play()
            set_state(STATE_GAME_OVER)
        else:
            start_countdown(direction=-1)


def handle_player_input():
    keys = pygame.key.get_pressed()

    if keys[pygame.K_w] or keys[pygame.K_UP]:
        left_paddle.y -= player_speed
    if keys[pygame.K_s] or keys[pygame.K_DOWN]:
        left_paddle.y += player_speed

    clamp_paddle(left_paddle)


def update_countdown():
    global countdown_value, countdown_last_tick

    now = pygame.time.get_ticks()
    if now - countdown_last_tick >= 700:
        countdown_value -= 1
        countdown_last_tick = now

    if countdown_value <= 0:
        set_state(STATE_PLAYING)


running = True
while running:
    clock.tick(60)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if game_state == STATE_MENU and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_1:
                apply_difficulty(1)
                reset_match()
            elif event.key == pygame.K_2:
                apply_difficulty(2)
                reset_match()
            elif event.key == pygame.K_3:
                apply_difficulty(3)
                reset_match()

        if game_state in (STATE_PLAYING, STATE_PAUSED, STATE_COUNTDOWN) and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_p:
                if game_state == STATE_PLAYING:
                    set_state(STATE_PAUSED)
                elif game_state == STATE_PAUSED:
                    set_state(STATE_PLAYING)

        if game_state == STATE_GAME_OVER and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                reset_match()
            elif event.key == pygame.K_m:
                set_state(STATE_MENU)
            elif event.key == pygame.K_ESCAPE:
                running = False

    if game_state == STATE_MENU:
        draw_menu()

    elif game_state == STATE_COUNTDOWN:
        update_countdown()
        draw_countdown()

    elif game_state == STATE_PLAYING:
        handle_player_input()
        update_ai()
        update_ball_and_collisions()
        draw_game()

    elif game_state == STATE_PAUSED:
        draw_paused()

    elif game_state == STATE_GAME_OVER:
        draw_game_over()

pygame.quit()
sys.exit()
