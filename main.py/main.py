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
GREEN = (0, 255, 0)
MENU_BACKGROUND_COLOR = (0, 0, 50)  # AZUL MARINHO ESCURO
GAME_BACKGROUND_COLOR = (180, 180, 180) # CINZA CLARO
BUTTON_COLOR = (50, 150, 50) # Cor do botão
BUTTON_HOVER_COLOR = (80, 180, 80) # Cor do botão ao passar o mouse

# --- VARIÁVEIS DE ESTADO E INICIALIZAÇÃO DE PEÇAS ---

# Lista inicial de peças (configuração de xeque-mate)
def create_initial_pieces():
    return [
        Piece("assets/rainha_branca.png", 1, 4, "rainha", "branca"), # Posição e7
        Piece("assets/rei_branco.png", 2, 3, "rei", "branca"),      # Posição d6
        Piece("assets/cavalo_branco.png", 3, 6, "cavalo", "branca"), # Posição g5
        Piece("assets/rei_preto.png", 0, 7, "rei", "preta"),         # Posição h8
    ]

pieces = create_initial_pieces()
selected_piece = None
valid_moves = []
checkmate_message = None

# Estados do Jogo
STATE_MENU = "menu"
STATE_GAME = "playing"
game_state = STATE_MENU # O jogo começa no menu

# --- FUNÇÕES DE DESENHO ---

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
        background_surface = pygame.Surface((WIDTH, HEIGHT))
        background_surface.fill(BLACK) 
        background_surface.set_alpha(180) 
        screen.blit(background_surface, (0, 0))

        lines = message.split('! ')
        
        title_font = pygame.font.SysFont("Arial", 48, bold=True)
        title_text = title_font.render(lines[0] + "!", True, (255, 215, 0)) 
        title_rect = title_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 40))
        screen.blit(title_text, title_rect)
        
        if len(lines) > 1:
            message_font = pygame.font.SysFont("Arial", 36)
            message_text = message_font.render(lines[1], True, (200, 0, 0)) 
            message_rect = message_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 30))
            screen.blit(message_text, message_rect)

# FUNÇÃO DE DESENHO DO MENU COM BOTÃO
def draw_start_menu(screen):
    """Desenha a tela de início do jogo com o fundo do menu e um botão clicável."""
    screen.fill(MENU_BACKGROUND_COLOR) 
    
    # 1. Título
    title_font = pygame.font.SysFont("Arial", 72)
    title_text = title_font.render("XADREZ PROJETO", True, WHITE)
    title_rect = title_text.get_rect(center=(WIDTH // 2, HEIGHT // 3))
    screen.blit(title_text, title_rect)
    
    # 2. Botão "Iniciar Jogo"
    button_width = 250
    button_height = 70
    button_x = (WIDTH - button_width) // 2
    button_y = HEIGHT // 3 * 2 - button_height // 2 # Centraliza o botão verticalmente

    # Cria o retângulo do botão
    start_button_rect = pygame.Rect(button_x, button_y, button_width, button_height)

    # Verifica se o mouse está sobre o botão para mudar a cor
    mouse_pos = pygame.mouse.get_pos()
    current_button_color = BUTTON_COLOR
    if start_button_rect.collidepoint(mouse_pos):
        current_button_color = BUTTON_HOVER_COLOR

    pygame.draw.rect(screen, current_button_color, start_button_rect, border_radius=10) # Desenha o botão
    
    button_font = pygame.font.SysFont("Arial", 36)
    button_text = button_font.render("INICIAR JOGO", True, WHITE)
    button_text_rect = button_text.get_rect(center=start_button_rect.center)
    screen.blit(button_text, button_text_rect)

    return start_button_rect # Retorna o retângulo do botão para uso na detecção de cliques


# --- FUNÇÕES DE LÓGICA (Permanecem inalteradas) ---

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
                            moves.append((r, c))
                        break
                    else:
                        moves.append((r, c))
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

# --- LOOP PRINCIPAL DO JOGO ---

running = True
start_button_rect = None # Variável para armazenar o retângulo do botão

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if game_state == STATE_MENU:
            # Lógica de input para a Tela de Início (clique do mouse no botão)
            if event.type == pygame.MOUSEBUTTONDOWN:
                if start_button_rect and start_button_rect.collidepoint(event.pos):
                    game_state = STATE_GAME # Mudar o estado para o jogo
        
        elif game_state == STATE_GAME:
            # Lógica de input para o Jogo (Seu código original de clique)
            if event.type == pygame.MOUSEBUTTONDOWN and not checkmate_message:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                col = (mouse_x - MARGIN) // CELL_SIZE
                row = (mouse_y - MARGIN) // CELL_SIZE

                if 0 <= row < 8 and 0 <= col < 8:
                    if selected_piece:
                        if (row, col) in valid_moves:
                            captured_piece = next((p for p in pieces if p.row == row and p.col == col and p.cor != selected_piece.cor), None)
                            selected_piece.row = row
                            selected_piece.col = col

                            if captured_piece:
                                pieces.remove(captured_piece)

                            black_king = next((p for p in pieces if p.tipo == "rei" and p.cor == "preta"), None)
                            if black_king and is_checkmate(black_king, pieces):
                                checkmate_message = "Primeira Fase: Beijo da Morte! Xeque-mate. Fim de jogo." 

                            selected_piece = None
                            valid_moves = []
                        else:
                            selected_piece = None
                            valid_moves = []
                    else:
                        for piece in pieces:
                            if piece.row == row and piece.col == col:
                                selected_piece = piece
                                valid_moves = get_valid_moves(piece, pieces)
                                break

    # --- Bloco de Desenho ---
    
    if game_state == STATE_MENU:
        start_button_rect = draw_start_menu(screen) # Armazena o retângulo do botão retornado
        
    elif game_state == STATE_GAME:
        screen.fill(GAME_BACKGROUND_COLOR) 
        
        draw_board()
        draw_coordinates()
        draw_valid_moves(valid_moves)

        for piece in pieces:
            piece.draw(screen, MARGIN, MARGIN)

        draw_checkmate_message(checkmate_message)

    pygame.display.flip()

pygame.quit()