class Board:
    def __init__(self):
        self.grid = self.create_board()

    def create_board(self):
        board = [[None for _ in range(8)] for _ in range(8)]
        # Inicializar peças aqui
        return board

    def draw(self, screen):
        for row in range(8):
            for col in range(8):
                color = (255, 255, 255) if (row + col) % 2 == 0 else (0, 0, 0)
                pygame.draw.rect(screen, color, (col*80, row*80, 80, 80))