import pygame
import random
import json

# Configurações do jogo
SCREEN_WIDTH, SCREEN_HEIGHT = 300, 600
GRID_SIZE = 30
COLUMNS, ROWS = SCREEN_WIDTH // GRID_SIZE, SCREEN_HEIGHT // GRID_SIZE

# Cores
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

# Peças clássicas do Tetris (formato e rotação)
SHAPES = [
    [[1, 1, 1, 1]],  # I
    [[1, 1, 0], [0, 1, 1]],  # Z
    [[0, 1, 1], [1, 1, 0]],  # S
    [[1, 1], [1, 1]],  # O
    [[1, 0, 0], [1, 1, 1]],  # L
    [[0, 0, 1], [1, 1, 1]],  # J
    [[0, 1, 0], [1, 1, 1]],  # T
]

# Inicializa o Pygame
pygame.init()

# Configuração da tela
tela = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Tetris")
clock = pygame.time.Clock()

# Inicializa HighScore
HIGHSCORE_FILE = "highscore.json"
def load_highscore():
    try:
        with open(HIGHSCORE_FILE, "r") as file:
            return json.load(file).get("highscore", 0)
    except FileNotFoundError:
        return 0

def save_highscore(score):
    with open(HIGHSCORE_FILE, "w") as file:
        json.dump({"highscore": score}, file)

highscore = load_highscore()

# Classes
class Piece:
    def __init__(self):
        self.shape = random.choice(SHAPES)
        self.color = [random.randint(50, 255) for _ in range(3)]
        self.x = COLUMNS // 2 - len(self.shape[0]) // 2
        self.y = 0

    def rotate(self):
        self.shape = [list(row) for row in zip(*self.shape[::-1])]

class Tetris:
    def __init__(self):
        self.grid = [[BLACK for _ in range(COLUMNS)] for _ in range(ROWS)]
        self.current_piece = Piece()
        self.next_piece = Piece()
        self.score = 0
        self.lines_cleared = 0
        self.level = 1
        self.speed = 500
        self.game_over = False

    def check_collision(self, dx=0, dy=0, rotated_shape=None):
        shape = rotated_shape or self.current_piece.shape
        for y, row in enumerate(shape):
            for x, cell in enumerate(row):
                if cell:
                    new_x = self.current_piece.x + x + dx
                    new_y = self.current_piece.y + y + dy
                    if new_x < 0 or new_x >= COLUMNS or new_y >= ROWS:
                        return True
                    if new_y >= 0 and self.grid[new_y][new_x] != BLACK:
                        return True
        return False

    def freeze_piece(self):
        for y, row in enumerate(self.current_piece.shape):
            for x, cell in enumerate(row):
                if cell:
                    grid_x = self.current_piece.x + x
                    grid_y = self.current_piece.y + y
                    self.grid[grid_y][grid_x] = {
                        "color": self.current_piece.color,
                        "border": True,  # Marca como com borda
                    }

    def clear_lines(self):
        cleared = 0
        for y in range(ROWS):
            if all(self.grid[y][x] != BLACK for x in range(COLUMNS)):
                del self.grid[y]
                self.grid.insert(0, [BLACK for _ in range(COLUMNS)])
                cleared += 1
        self.lines_cleared += cleared
        self.score += cleared * 10
        return cleared

    def new_piece(self):
        self.current_piece = self.next_piece
        self.next_piece = Piece()
        if self.check_collision():
            self.game_over = True

    def move_piece(self, dx, dy):
        if not self.check_collision(dx=dx, dy=dy):
            self.current_piece.x += dx
            self.current_piece.y += dy
        elif dy:
            self.freeze_piece()
            self.clear_lines()
            self.new_piece()

    def drop_piece_to_bottom(self):
        while not self.check_collision(dy=1):
            self.current_piece.y += 1
        self.freeze_piece()
        self.clear_lines()
        self.new_piece()

    def rotate_piece(self):
        rotated_shape = [list(row) for row in zip(*self.current_piece.shape[::-1])]
        if not self.check_collision(rotated_shape=rotated_shape):
            self.current_piece.shape = rotated_shape

    def draw_grid(self):
        for y, row in enumerate(self.grid):
            for x, cell in enumerate(row):
                if isinstance(cell, dict):  # Verifica se o grid contém uma peça congelada
                    pygame.draw.rect(
                        tela, cell["color"], (x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE, GRID_SIZE)
                    )
                    if cell["border"]:  # Desenha borda se marcado
                        pygame.draw.rect(
                            tela,
                            BLACK,
                            (x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE, GRID_SIZE),
                            1,
                        )
                else:
                    pygame.draw.rect(
                        tela, cell, (x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE, GRID_SIZE)
                    )

    def draw_piece(self, piece):
        for y, row in enumerate(piece.shape):
            for x, cell in enumerate(row):
                if cell:
                    pygame.draw.rect(tela, piece.color, ((piece.x + x) * GRID_SIZE, (piece.y + y) * GRID_SIZE, GRID_SIZE, GRID_SIZE))
                    pygame.draw.rect(tela, BLACK, ((piece.x + x) * GRID_SIZE, (piece.y + y) * GRID_SIZE, GRID_SIZE, GRID_SIZE), 1)  # Adiciona borda preta

    def draw_next_piece(self):
        font = pygame.font.Font(None, 24)
        text = font.render("Próxima Peça:", True, WHITE)
        tela.blit(text, (SCREEN_WIDTH - 120, 10))
        for y, row in enumerate(self.next_piece.shape):
            for x, cell in enumerate(row):
                if cell:
                    pygame.draw.rect(tela, self.next_piece.color, (SCREEN_WIDTH - 120 + x * GRID_SIZE, 30 + y * GRID_SIZE, GRID_SIZE, GRID_SIZE))
                    pygame.draw.rect(tela, BLACK, (SCREEN_WIDTH - 120 + x * GRID_SIZE, 30 + y * GRID_SIZE, GRID_SIZE, GRID_SIZE), 1)  # Adiciona borda preta

    def update_level(self):
        self.level = 1 + self.lines_cleared // 10
        self.speed = max(100, 500 - (self.level - 1) * 40)

# Loop principal
def main():
    tetris = Tetris()
    drop_time = pygame.time.get_ticks()

    while not tetris.game_over:
        tela.fill(BLACK)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                tetris.game_over = True

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    tetris.move_piece(-1, 0)
                elif event.key == pygame.K_RIGHT:
                    tetris.move_piece(1, 0)
                elif event.key == pygame.K_DOWN:
                    tetris.move_piece(0, 1)
                elif event.key == pygame.K_UP:
                    tetris.rotate_piece()
                elif event.key == pygame.K_SPACE:
                    tetris.drop_piece_to_bottom()

        if pygame.time.get_ticks() - drop_time > tetris.speed:
            tetris.move_piece(0, 1)
            drop_time = pygame.time.get_ticks()

        tetris.update_level()
        tetris.draw_grid()
        tetris.draw_piece(tetris.current_piece)
        tetris.draw_next_piece()

        # Exibe placares
        font = pygame.font.Font(None, 24)
        score_text = font.render(f"Score: {tetris.score}", True, WHITE)
        highscore_text = font.render(f"HighScore: {highscore}", True, WHITE)
        level_text = font.render(f"Nível: {tetris.level}", True, WHITE)
        lines_text = font.render(f"Linhas: {tetris.lines_cleared}", True, WHITE)
        next_level_text = font.render(f"Próx. Nível: {200 - (tetris.score % 200)} pts", True, WHITE)

        tela.blit(score_text, (10, 10))
        tela.blit(highscore_text, (10, 30))
        tela.blit(level_text, (10, 50))
        tela.blit(lines_text, (10, 70))
        tela.blit(next_level_text, (10, 90))

        pygame.display.flip()
        clock.tick(60)

    # Game Over
    if tetris.score > highscore:
        save_highscore(tetris.score)
    font = pygame.font.Font(None, 48)
    game_over_text = font.render("GAME OVER", True, WHITE)
    tela.blit(game_over_text, (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 24))
    pygame.display.flip()
    pygame.time.wait(3000)

if __name__ == "__main__":
    main()
    pygame.quit()
