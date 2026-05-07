import json
import os
import random
import sys
from dataclasses import dataclass

import pygame

# ----------------------------
# Configuração geral
# ----------------------------
WIDTH, HEIGHT = 1080, 720
PLAY_WIDTH, PLAY_HEIGHT = 360, 600
BLOCK = 30
COLS, ROWS = PLAY_WIDTH // BLOCK, PLAY_HEIGHT // BLOCK
TOP_LEFT_X = 60
TOP_LEFT_Y = 60
SIDEBAR_X = TOP_LEFT_X + PLAY_WIDTH + 40
FPS = 60

HIGH_SCORE_FILE = "highscore.json"

BG = (12, 14, 24)
PANEL = (22, 28, 44)
PANEL_2 = (18, 22, 34)
GRID = (36, 42, 60)
WHITE = (245, 245, 245)
CYAN = (0, 255, 255)
GHOST = (255, 255, 255, 70)
BLACK = (0, 0, 0)
SHADOW = (0, 0, 0, 80)

# Tabela de peças: formato 5x5 com offsets de blocos
S = [[".....",
      ".....",
      "..00.",
      ".00..",
      "....."],
     [".....",
      "..0..",
      "..00.",
      "...0.",
      "....."]]

Z = [[".....",
      ".....",
      ".00..",
      "..00.",
      "....."],
     [".....",
      "..0..",
      ".00..",
      ".0...",
      "....."]]

I = [["..0..",
      "..0..",
      "..0..",
      "..0..",
      "....."],
     [".....",
      "0000.",
      ".....",
      ".....",
      "....."]]

O = [[".....",
      ".....",
      ".00..",
      ".00..",
      "....."]]

J = [[".....",
      ".0...",
      ".000.",
      ".....",
      "....."],
     [".....",
      "..00.",
      "..0..",
      "..0..",
      "....."],
     [".....",
      ".....",
      ".000.",
      "...0.",
      "....."],
     [".....",
      "..0..",
      "..0..",
      ".00..",
      "....."]]

L = [[".....",
      "...0.",
      ".000.",
      ".....",
      "....."],
     [".....",
      "..0..",
      "..0..",
      "..00.",
      "....."],
     [".....",
      ".....",
      ".000.",
      ".0...",
      "....."],
     [".....",
      ".00..",
      "..0..",
      "..0..",
      "....."]]

T = [[".....",
      "..0..",
      ".000.",
      ".....",
      "....."],
     [".....",
      "..0..",
      "..00.",
      "..0..",
      "....."],
     [".....",
      ".....",
      ".000.",
      "..0..",
      "....."],
     [".....",
      "..0..",
      ".00..",
      "..0..",
      "....."]]

PIECES = [S, Z, I, O, J, L, T]
PIECE_COLORS = [
    (0, 240, 120),
    (255, 70, 70),
    (70, 220, 255),
    (255, 215, 70),
    (90, 130, 255),
    (255, 160, 60),
    (190, 90, 255),
]


@dataclass
class Piece:
    x: int
    y: int
    shape: list
    color: tuple
    rotation: int = 0

    @property
    def variant_count(self):
        return len(self.shape)


def load_highscore():
    if not os.path.exists(HIGH_SCORE_FILE):
        return 0
    try:
        with open(HIGH_SCORE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return int(data.get("highscore", 0))
    except Exception:
        return 0


def save_highscore(score):
    try:
        with open(HIGH_SCORE_FILE, "w", encoding="utf-8") as f:
            json.dump({"highscore": int(score)}, f, indent=2, ensure_ascii=False)
    except Exception:
        pass


def create_grid(locked_positions=None):
    grid = [[(15, 18, 30) for _ in range(COLS)] for _ in range(ROWS)]
    if locked_positions:
        for (x, y), color in locked_positions.items():
            if 0 <= x < COLS and 0 <= y < ROWS:
                grid[y][x] = color
    return grid


def convert_shape_format(piece):
    positions = []
    shape = piece.shape[piece.rotation % len(piece.shape)]

    for i, line in enumerate(shape):
        for j, char in enumerate(line):
            if char == "0":
                positions.append((piece.x + j - 2, piece.y + i - 4))
    return positions


def valid_space(piece, grid):
    accepted_positions = [[(j, i) for j in range(COLS) if grid[i][j] == (15, 18, 30)] for i in range(ROWS)]
    accepted_positions = [j for sub in accepted_positions for j in sub]

    formatted = convert_shape_format(piece)
    for pos in formatted:
        if pos[0] < 0 or pos[0] >= COLS or pos[1] >= ROWS:
            return False
        
        if pos[1] >= 0:
            if pos not in accepted_positions:
                return False
    return True


def check_lost(locked_positions):
    for (x, y) in locked_positions:
        if y < 0: # O jogo só acaba se as peças ultrapassarem o limite visível (y=0)
            return True
    return False


def get_shape():
    idx = random.randrange(len(PIECES))
    return Piece(x=COLS // 2, y=2, shape=PIECES[idx], color=PIECE_COLORS[idx])


def draw_window(screen, grid, score, highscore, level, lines, next_pieces, font, small_font):
    screen.fill(BG)

    # Painéis laterais
    pygame.draw.rect(screen, PANEL, (20, 20, WIDTH - 40, HEIGHT - 40), border_radius=22)
    pygame.draw.rect(screen, PANEL_2, (TOP_LEFT_X - 14, TOP_LEFT_Y - 14, PLAY_WIDTH + 28, PLAY_HEIGHT + 28), border_radius=20)
    pygame.draw.rect(screen, CYAN, (TOP_LEFT_X - 14, TOP_LEFT_Y - 14, PLAY_WIDTH + 28, PLAY_HEIGHT + 28), width=3, border_radius=20)

    # Área de jogo e grade
    for i in range(ROWS):
        for j in range(COLS):
            x = TOP_LEFT_X + j * BLOCK
            y = TOP_LEFT_Y + i * BLOCK
            color = grid[i][j]
            pygame.draw.rect(screen, color, (x, y, BLOCK, BLOCK), border_radius=6)
            pygame.draw.rect(screen, GRID, (x, y, BLOCK, BLOCK), width=1, border_radius=6)

    # Título
    title = font.render("TETRIS", True, WHITE)
    screen.blit(title, (SIDEBAR_X, 35))
    pygame.draw.line(screen, CYAN, (SIDEBAR_X, 80), (WIDTH - 55, 80), 2)

    # Painel de informações
    labels = [
        ("Score", score),
        ("Highscore", highscore),
        ("Nível", level),
        ("Linhas", lines),
    ]
    y = 110
    for label, value in labels:
        text = small_font.render(f"{label}: {value}", True, WHITE)
        screen.blit(text, (SIDEBAR_X, y))
        y += 36

    # Próximas peças
    next_title = small_font.render("Próximas peças", True, WHITE)
    screen.blit(next_title, (SIDEBAR_X, 280))

    preview_box_y = 320
    for index, piece in enumerate(next_pieces[:3]):
        box_y = preview_box_y + index * 135
        pygame.draw.rect(screen, (30, 35, 52), (SIDEBAR_X, box_y, 220, 110), border_radius=18)
        pygame.draw.rect(screen, CYAN, (SIDEBAR_X, box_y, 220, 110), width=2, border_radius=18)
        draw_piece_preview(screen, piece, SIDEBAR_X + 24, box_y + 18, 22)

    # Linha de ajuda
    help_lines = [
        "← → mover",
        "↓ descer",
        "↑ rotacionar",
        "ESPAÇO cair",
    ]

    help_x = SIDEBAR_X + 240
    help_y = HEIGHT - 180

    for line in help_lines:
        txt = small_font.render(line, True, (200, 208, 224))
        screen.blit(txt, (help_x, help_y)) # Usando a nova posição help_x
        help_y += 30


def draw_piece_preview(screen, piece, x_offset, y_offset, size):
    shape = piece.shape[0]
    for i, line in enumerate(shape):
        for j, char in enumerate(line):
            if char == "0":
                rx = x_offset + j * size
                ry = y_offset + i * size
                draw_block(screen, piece.color, rx, ry, size, preview=True)


def draw_block(screen, color, x, y, size=BLOCK, preview=False, alpha=255):
    rect = pygame.Rect(x, y, size, size)
    shadow_rect = rect.copy()
    shadow_rect.move_ip(3, 4)
    shadow = pygame.Surface((size, size), pygame.SRCALPHA)
    highlight = pygame.Surface((size, size), pygame.SRCALPHA)

    shadow.fill((0, 0, 0, 90 if preview else 100))
    highlight.fill((255, 255, 255, 30 if preview else 45))
    base = pygame.Surface((size, size), pygame.SRCALPHA)
    base.fill((*color, alpha))

    pygame.draw.rect(screen, (0, 0, 0), shadow_rect, border_radius=7)
    screen.blit(shadow, rect.topleft)
    screen.blit(base, rect.topleft)
    pygame.draw.rect(screen, highlight.get_at((0, 0))[:3], rect, width=1, border_radius=7)
    pygame.draw.rect(screen, (255, 255, 255), rect, width=1, border_radius=7)


def draw_ghost_piece(screen, piece, grid):
    ghost = Piece(piece.x, piece.y, piece.shape, piece.color, piece.rotation)
    while True:
        ghost.y += 1
        if not valid_space(ghost, grid):
            ghost.y -= 1
            break
    for x, y in convert_shape_format(ghost):
        if y > -1:
            px = TOP_LEFT_X + x * BLOCK
            py = TOP_LEFT_Y + y * BLOCK
            ghost_surface = pygame.Surface((BLOCK, BLOCK), pygame.SRCALPHA)
            ghost_surface.fill((255, 255, 255, 55))
            screen.blit(ghost_surface, (px, py))
            pygame.draw.rect(screen, (200, 210, 230), (px, py, BLOCK, BLOCK), 1, border_radius=7)


def draw_current_piece(screen, piece):
    for x, y in convert_shape_format(piece):
        if y > -1:
            px = TOP_LEFT_X + x * BLOCK
            py = TOP_LEFT_Y + y * BLOCK
            draw_block(screen, piece.color, px, py)


def clear_rows(locked_positions):
    cleared_rows = [
        i for i in range(ROWS)
        if all((j, i) in locked_positions for j in range(COLS))
    ]

    if not cleared_rows:
        return 0

    cleared_rows_set = set(cleared_rows)

    for row in cleared_rows:
        for j in range(COLS):
            locked_positions.pop((j, row), None)

    # Move tudo que ficou acima das linhas limpas para baixo.
    original_items = list(locked_positions.items())
    locked_positions.clear()
    for (x, y), color in original_items:
        shift = sum(1 for row in cleared_rows if y < row)
        locked_positions[(x, y + shift)] = color

    return len(cleared_rows)


def score_for_lines(lines_cleared):
    if lines_cleared == 1:
        return 10
    if lines_cleared == 2:
        return 25
    if lines_cleared == 3:
        return 50
    if lines_cleared == 4:
        return 100
    return 0


def level_from_lines(lines):
    return lines // 10 + 1


def fall_speed_for_level(level):
    # Começa lento e acelera gradativamente.
    return max(0.08, 0.75 - (level - 1) * 0.06)


def main():
    pygame.init()
    pygame.display.set_caption("Tetris - Python")
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()

    font = pygame.font.SysFont("arialblack", 42)
    small_font = pygame.font.SysFont("arial", 24, bold=True)
    tiny_font = pygame.font.SysFont("arial", 18)

    highscore = load_highscore()

    locked_positions = {}
    grid = create_grid(locked_positions)

    current_piece = get_shape()
    next_pieces = [get_shape() for _ in range(3)]

    fall_time = 0.0
    current_level = 1
    total_lines = 0
    score = 0
    landed_random_bonus = 0

    running = True
    while running:
        clock.tick(FPS)
        fall_time += clock.get_rawtime() / 1000.0

        grid = create_grid(locked_positions)
        level = level_from_lines(total_lines)
        speed = fall_speed_for_level(level)

        if level != current_level:
            current_level = level

        hard_drop = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    current_piece.x -= 1
                    if not valid_space(current_piece, grid):
                        current_piece.x += 1
                elif event.key == pygame.K_RIGHT:
                    current_piece.x += 1
                    if not valid_space(current_piece, grid):
                        current_piece.x -= 1
                elif event.key == pygame.K_DOWN:
                    current_piece.y += 1
                    if not valid_space(current_piece, grid):
                        current_piece.y -= 1
                elif event.key == pygame.K_UP:
                    current_piece.rotation = (current_piece.rotation + 1) % len(current_piece.shape)
                    if not valid_space(current_piece, grid):
                        current_piece.rotation = (current_piece.rotation - 1) % len(current_piece.shape)
                elif event.key == pygame.K_SPACE:
                    while True:
                        current_piece.y += 1
                        if not valid_space(current_piece, grid):
                            current_piece.y -= 1
                            break
                    hard_drop = True

        def lock_piece_and_spawn():
            nonlocal current_piece, next_pieces, score, total_lines, highscore, grid, landed_random_bonus, fall_time

            for pos in convert_shape_format(current_piece):
                locked_positions[pos] = current_piece.color

            landed_random_bonus = random.randint(0, 6) * max(1, level)
            lines_cleared = clear_rows(locked_positions)

            if lines_cleared > 0:
                score += score_for_lines(lines_cleared)
                total_lines += lines_cleared

            score += landed_random_bonus

            current_piece = next_pieces.pop(0)
            next_pieces.append(get_shape())
            grid = create_grid(locked_positions)

            if score > highscore:
                highscore = score
                save_highscore(highscore)

            fall_time = 0

        # Se o jogador apertou ESPAÇO, o bloqueio acontece imediatamente.
        if hard_drop:
            lock_piece_and_spawn()
            # Verifica se a NOVA peça que acabou de nascer colidiu imediatamente
            if not valid_space(current_piece, grid):
                running = False

        # Gravidade automática
        if running and fall_time >= speed:
            fall_time = 0
            current_piece.y += 1
            if not valid_space(current_piece, grid):
                current_piece.y -= 1
                lock_piece_and_spawn()
                if not valid_space(current_piece, grid):
                    running = False

        draw_window(screen, grid, score, highscore, current_level, total_lines, next_pieces, font, small_font)
        draw_ghost_piece(screen, current_piece, grid)
        draw_current_piece(screen, current_piece)

        # Barra inferior e brilho
        bottom_bar = pygame.Surface((PLAY_WIDTH + 28, 10), pygame.SRCALPHA)
        bottom_bar.fill((0, 255, 255, 50))
        screen.blit(bottom_bar, (TOP_LEFT_X - 14, TOP_LEFT_Y + PLAY_HEIGHT + 14))

        pygame.display.flip()

    # Tela final
    screen.fill(BG)
    pygame.draw.rect(screen, PANEL, (140, 180, 800, 250), border_radius=24)
    pygame.draw.rect(screen, CYAN, (140, 180, 800, 250), width=3, border_radius=24)
    over = font.render("GAME OVER", True, WHITE)
    score_text = small_font.render(f"Score final: {score}", True, WHITE)
    hs_text = small_font.render(f"Highscore: {highscore}", True, WHITE)
    exit_text = tiny_font.render("Feche a janela para sair.", True, (210, 218, 230))
    screen.blit(over, (WIDTH // 2 - over.get_width() // 2, 220))
    screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, 300))
    screen.blit(hs_text, (WIDTH // 2 - hs_text.get_width() // 2, 334))
    screen.blit(exit_text, (WIDTH // 2 - exit_text.get_width() // 2, 380))
    pygame.display.flip()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()


if __name__ == "__main__":
    main()
