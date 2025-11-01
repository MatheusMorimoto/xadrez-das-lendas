import pygame

# Classe da peça
class Piece:
    def __init__(self, image_path, row, col, tipo, cor):
        loaded_image = pygame.image.load(image_path).convert_alpha()
        self.image = pygame.transform.scale(loaded_image, (80, 80))
        self.row = row
        self.col = col
        self.tipo = tipo
        self.image_path = image_path
        self.cor = cor  # "branca" ou "preta"

    def draw(self, screen, offset_x, offset_y):
        x = self.col * 80 + offset_x
        y = self.row * 80 + offset_y
        screen.blit(self.image, (x, y))

# Inicializa o PyGame
pygame.init()
font = pygame.font.SysFont("Arial", 24)

# Tamanho do tabuleiro e margens
CELL_SIZE = 80
BOARD_SIZE = CELL_SIZE * 8
MARGIN = 40
WIDTH = BOARD_SIZE + MARGIN * 2
HEIGHT = BOARD_SIZE + MARGIN * 2

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Tabuleiro de Xadrez")

# Cores
WHITE = (255, 255, 255)
LIGHT_GRAY = (200, 200, 200)
BLACK = (0, 0, 0)

# Lista de peças
# Posições configuradas para um cenário de captura do rei
pieces = [
    Piece("assets/rainha_branca.png", 1, 4, "rainha", "branca"), # Posição e7
    Piece("assets/rei_branco.png", 2, 3, "rei", "branca"),       # Posição d6
    Piece("assets/cavalo_branco.png", 3, 6, "cavalo", "branca"), # Posição g5
    Piece("assets/rei_preto.png", 0, 7, "rei", "preta"),        # Posição h8
]

selected_piece = None
valid_moves = []
checkmate_message = None


# Funções de desenho
def draw_board():
    pygame.draw.rect(screen, BLACK, (MARGIN - 2, MARGIN - 2, BOARD_SIZE + 4, BOARD_SIZE + 4), 2)
    for row in range(8):
        for col in range(8):
            color = WHITE if (row + col) % 2 == 0 else LIGHT_GRAY
            x = col * CELL_SIZE + MARGIN
            y = row * CELL_SIZE + MARGIN
            pygame.draw.rect(screen, color, (x, y, CELL_SIZE, CELL_SIZE))

def draw_coordinates():
    for col in range(8):
        letter = chr(ord('A') + col)
        text = font.render(letter, True, BLACK)
        x = col * CELL_SIZE + MARGIN + CELL_SIZE // 2 - text.get_width() // 2
        screen.blit(text, (x, HEIGHT - MARGIN + 5))
        screen.blit(text, (x, 5))
    for row in range(8):
        number = str(8 - row)
        text = font.render(number, True, BLACK)
        y = row * CELL_SIZE + MARGIN + CELL_SIZE // 2 - text.get_height() // 2
        screen.blit(text, (MARGIN - 30, y))

def draw_valid_moves(moves):
    for row, col in moves:
        x = col * CELL_SIZE + MARGIN + CELL_SIZE // 2
        y = row * CELL_SIZE + MARGIN + CELL_SIZE // 2
        pygame.draw.circle(screen, (0, 150, 0), (x, y), 10)

def draw_checkmate_message(message):
    if message:
        text = font.render(message, True, (200, 0, 0))
        rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        pygame.draw.rect(screen, (255, 255, 255), rect.inflate(20, 20))
        screen.blit(text, rect)

# Funções de lógica
def get_valid_moves(piece, pieces):
    moves = []

    if piece.tipo == "rainha":
        directions = [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, -1), (1, -1), (-1, 1)]
        for dx, dy in directions:
            for i in range(1, 8):
                r = piece.row + dy * i
                c = piece.col + dx * i
                if 0 <= r < 8 and 0 <= c < 8:
                    target_piece = next((p for p in pieces if p.row == r and p.col == c), None)
                    if target_piece:
                        if target_piece.cor != piece.cor:
                            moves.append((r, c))  # Pode capturar
                        break
                    else:
                        moves.append((r, c))  # Casa vazia
                else:
                    break

    elif piece.tipo == "rei":
        directions = [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, -1), (1, -1), (-1, 1)]
        for dx, dy in directions:
            r = piece.row + dy
            c = piece.col + dx
            if 0 <= r < 8 and 0 <= c < 8:
                target_piece = next((p for p in pieces if p.row == r and p.col == c), None)
                if not target_piece or target_piece.cor != piece.cor:
                    moves.append((r, c))

    elif piece.tipo == "cavalo":
        jumps = [(2, 1), (1, 2), (-1, 2), (-2, 1), (-2, -1), (-1, -2), (1, -2), (2, -1)]
        for dx, dy in jumps:
            r = piece.row + dy
            c = piece.col + dx
            if 0 <= r < 8 and 0 <= c < 8:
                target_piece = next((p for p in pieces if p.row == r and p.col == c), None)
                if not target_piece or target_piece.cor != piece.cor:
                    moves.append((r, c))

    return moves

def is_king_in_check(king, pieces):
    for piece in pieces:
        if piece != king:
            moves = get_valid_moves(piece, pieces)
            if (king.row, king.col) in moves:
                return True
    return False

def would_king_be_in_check(king, pieces, move_piece, new_row, new_col):
    """Simula um movimento e verifica se o rei estaria em xeque."""
    original_row, original_col = move_piece.row, move_piece.col
    captured_piece = next((p for p in pieces if p.row == new_row and p.col == new_col), None)
    
    # Simula o movimento
    move_piece.row, move_piece.col = new_row, new_col
    if captured_piece:
        pieces.remove(captured_piece)

    in_check = is_king_in_check(king, pieces)

    # Desfaz o movimento
    move_piece.row, move_piece.col = original_row, original_col
    if captured_piece:
        pieces.append(captured_piece)
        
    return in_check

def is_checkmate(king, pieces):
    if not is_king_in_check(king, pieces):
        return False

    # Verifica se qualquer peça da mesma cor do rei pode fazer um movimento legal
    for piece in pieces:
        if piece.cor == king.cor:
            moves = get_valid_moves(piece, pieces)
            for move in moves:
                # Se um movimento resultar em uma posição onde o rei não está em xeque, não é xeque-mate
                if not would_king_be_in_check(king, pieces, piece, move[0], move[1]):
                    return False

    # Se nenhum movimento legal tira o rei do xeque, é xeque-mate
    return True

# Loop principal
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN and not checkmate_message:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            col = (mouse_x - MARGIN) // CELL_SIZE
            row = (mouse_y - MARGIN) // CELL_SIZE

            if 0 <= row < 8 and 0 <= col < 8:
                if selected_piece:
                    if (row, col) in valid_moves:
                        # Move a peça selecionada
                        captured_piece = next((p for p in pieces if p.row == row and p.col == col and p.cor != selected_piece.cor), None)
                        selected_piece.row = row
                        selected_piece.col = col

                        # Remove a peça capturada, se houver
                        if captured_piece:
                            pieces.remove(captured_piece)

                        # Verifica se o movimento resultou em xeque-mate
                        black_king = next((p for p in pieces if p.tipo == "rei" and p.cor == "preta"), None)
                        if black_king and is_checkmate(black_king, pieces):
                            checkmate_message = "Xeque-mate! Fim de jogo."

                    selected_piece = None
                    valid_moves = []
                else:
                    for piece in pieces:
                        if piece.row == row and piece.col == col:
                            selected_piece = piece
                            valid_moves = get_valid_moves(piece, pieces)
                            break

    screen.fill((180, 180, 180))
    draw_board()
    draw_coordinates()
    draw_valid_moves(valid_moves)

    for piece in pieces:
        piece.draw(screen, MARGIN, MARGIN)

    draw_checkmate_message(checkmate_message)
    pygame.display.flip()

pygame.quit()
