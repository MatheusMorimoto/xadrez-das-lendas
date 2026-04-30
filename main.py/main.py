import pygame
import os
import math 

# Define o diretório de ativos, assumindo que a pasta 'assets' está no mesmo nível do main.py
ASSETS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
# Se a pasta 'assets' estiver diretamente em D:\projeto sabado, você pode tentar:
# ASSETS_DIR = os.path.join(os.getcwd(), "assets")
# Vou manter a primeira opção, pois é mais robusta para scripts Python.

# Função auxiliar para verificar a ocupação (útil dentro da classe Piece)
def get_piece_at(row, col, pieces):
    return next((p for p in pieces if p.row == row and p.col == col), None)

# Classe da peça (COM MÉTODO get_moves INTEGRADO)
class Piece:
    def __init__(self, image_path_relative, row, col, tipo, cor):
        # CORREÇÃO CRÍTICA AQUI: Construindo o caminho absoluto para a imagem
        full_image_path = os.path.join(os.getcwd(), image_path_relative)
        
        try:
            # Tenta carregar usando o caminho completo a partir do diretório de trabalho atual
            loaded_image = pygame.image.load(full_image_path).convert_alpha()
            self.image = pygame.transform.scale(loaded_image, (80, 80))
            print(f"Sucesso ao carregar: {full_image_path}") # Mensagem de sucesso
        except (pygame.error, FileNotFoundError) as e:
            # O erro persiste, exibe a peça magenta
            print(f"ERRO PERSISTENTE ao carregar a imagem {full_image_path}: {e}")
            self.image = pygame.Surface((80, 80))
            self.image.fill((255, 0, 255)) 
            
        self.row = row
        self.col = col
        self.tipo = tipo
        self.image_path = image_path_relative
        self.cor = cor  # "branca" ou "preta"

    def draw(self, screen, offset_x, offset_y, board_inverted_display=False):
        if not hasattr(self, 'image') or self.image is None:
            return
        
        draw_row = self.row
        # Para a perspectiva das pretas (board_inverted_display=True),
        # a linha 0 (rank 8) é desenhada na parte inferior da tela,
        # e a linha 7 (rank 1) é desenhada na parte superior.
        # A lógica atual de desenho (y = self.row * 80) já faz isso se considerarmos row 0 como o topo.
        # Para inverter a perspectiva, row 0 (rank 8) deve ser desenhada no topo para brancas,
        # e row 0 (rank 8) deve ser desenhada no fundo para pretas.
        # Portanto, para a perspectiva das pretas, invertemos a coordenada Y.
        if board_inverted_display:
            draw_row = 7 - self.row
        
        x = self.col * 80 + offset_x # Colunas não são invertidas por padrão
        y = draw_row * 80 + offset_y
        screen.blit(self.image, (x, y))

    # NOVO MÉTODO: Calcula os movimentos válidos da peça no tabuleiro atual
    def get_moves(self, board_pieces):
        moves = []
        
        # Função interna para calcular movimentos lineares/diagonais (Torre, Bispo, Rainha)
        def check_linear_moves(directions):
            possible_moves = []
            for dx, dy in directions:
                for i in range(1, 8):
                    r = self.row + dy * i
                    c = self.col + dx * i
                    if 0 <= r < 8 and 0 <= c < 8:
                        target_piece = get_piece_at(r, c, board_pieces)
                        if target_piece:
                            if target_piece.cor != self.cor:
                                possible_moves.append((r, c)) # Captura
                            break # Para se encontrar qualquer peça
                        else:
                            possible_moves.append((r, c)) # Movimento para casa vazia
                    else:
                        break
            return possible_moves

        # Lógica de movimento da Rainha (diagonal e reta)
        if self.tipo == "rainha":
            directions = [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, -1), (1, -1), (-1, 1)]
            moves.extend(check_linear_moves(directions))

        # Lógica de movimento do Rei (uma casa em qualquer direção)
        elif self.tipo == "rei":
            directions = [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, -1), (1, -1), (-1, 1)]
            for dx, dy in directions:
                r = self.row + dy
                c = self.col + dx
                if 0 <= r < 8 and 0 <= c < 8:
                    target_piece = get_piece_at(r, c, board_pieces)
                    if not target_piece or target_piece.cor != self.cor:
                        moves.append((r, c))

        # Lógica de movimento do Cavalo (formato L)
        elif self.tipo == "cavalo":
            jumps = [(2, 1), (1, 2), (-1, 2), (-2, 1), (-2, -1), (-1, -2), (1, -2), (2, -1)]
            for dx, dy in jumps:
                r = self.row + dy
                c = self.col + dx
                if 0 <= r < 8 and 0 <= c < 8:
                    target_piece = get_piece_at(r, c, board_pieces)
                    if not target_piece or target_piece.cor != self.cor:
                        moves.append((r, c))
                        
        # Lógica do Peão
        elif self.tipo == "peao":
            if self.cor == "branca":
                direction = -1
                start_row = 6 
            else: 
                direction = 1
                start_row = 1 
                
            # 1. Movimento para frente (uma casa)
            r = self.row + direction
            c = self.col
            if 0 <= r < 8 and not get_piece_at(r, c, board_pieces):
                moves.append((r, c))
                
                # 2. Movimento para frente (duas casas)
                if self.row == start_row:
                    r2 = self.row + 2 * direction
                    if not get_piece_at(r2, c, board_pieces):
                        moves.append((r2, c))
            
            # 3. Captura diagonal
            for dc in [-1, 1]:
                r_cap = self.row + direction
                c_cap = self.col + dc
                if 0 <= r_cap < 8 and 0 <= c_cap < 8:
                    target_piece = get_piece_at(r_cap, c_cap, board_pieces)
                    if target_piece and target_piece.cor != self.cor:
                        moves.append((r_cap, c_cap))
                        
        # Lógica da Torre (reta)
        elif self.tipo == "torre":
            directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
            moves.extend(check_linear_moves(directions))
        
        # Lógica do Bispo (diagonal)
        elif self.tipo == "bispo":
            directions = [(1, 1), (-1, -1), (1, -1), (-1, 1)]
            moves.extend(check_linear_moves(directions))

        return moves

    def copy(self):
        """Cria uma cópia da peça para salvar o estado do tabuleiro."""
        new_piece = Piece(self.image_path, self.row, self.col, self.tipo, self.cor)
        # Copiamos a imagem já carregada para não precisar ler o arquivo do disco novamente
        new_piece.image = self.image
        return new_piece


# Inicializa o PyGame (mantido)
pygame.init()
font = pygame.font.SysFont("Arial", 24)

# Tamanho do tabuleiro e margens (mantido)
CELL_SIZE = 80
BOARD_SIZE = CELL_SIZE * 8
MARGIN = 40
WIDTH = BOARD_SIZE + MARGIN * 2
HEIGHT = BOARD_SIZE + MARGIN * 2

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Tabuleiro de Xadrez")

# Cores (mantido)
WHITE = (255, 255, 255)
LIGHT_GRAY = (200, 200, 200)
BLACK = (0, 0, 0)
GREEN = (0, 150, 0)
MENU_BACKGROUND_COLOR = (0, 0, 50)  
GAME_BACKGROUND_COLOR = (180, 180, 180) 
BUTTON_COLOR = (50, 150, 50) 
BUTTON_HOVER_COLOR = (80, 180, 80) 

RESTART_BUTTON_RECT = pygame.Rect(WIDTH // 2 - 125, HEIGHT // 2 + 80, 250, 60)

# --- VARIÁVEIS DE ESTADO E INICIALIZAÇÃO DE PEÇAS ---

# Global game state variables
current_turn = "branca" # Default for Phase 1
board_inverted_display = False # Default for Phase 1
last_move_description = "" # Stores the description of the winning move for transitions
last_successful_move_text = "" # Stores the description of the last non-winning move
last_successful_move_time = 0 # Timer for displaying the last successful move
transition_start_time = 0 # Timer for victory transitions
transition_message = "" # Message to display during transition
current_phase = 1 # Tracks the current phase for resets
reset_timer_active = False # Flag for 3-second reset delay
reset_timer_start = 0 # Start time for the reset delay
error_piece_pos = None # Stores (row, col) of the piece that moved incorrectly

# Lista inicial de peças (Fase 1 - Exemplo de Xeque-mate: Beijo da Morte)
def create_initial_pieces_phase1():
    return [
        Piece("assets/rainha_branca.png", 1, 4, "rainha", "branca"), # Posição e7 (row 1, col 4)
        Piece("assets/rei_branco.png", 2, 3, "rei", "branca"),       # Posição d6
        Piece("assets/cavalo_branco.png", 3, 6, "cavalo", "branca"), # Posição g5
        Piece("assets/rei_preto.png", 0, 7, "rei", "preta"),         # Posição h8
    ]

# Layout para a Fase 3
def create_initial_pieces_phase3():
    return [
        # --- PEÇAS PRETAS ---
        Piece("assets/rei_preto.png", 1, 3, "rei", "preta"),          
        Piece("assets/rainha_preta.png", 4, 5, "rainha", "preta"),    
        Piece("assets/cavalo_preto .png", 4, 4, "cavalo", "preta"),   
        Piece("assets/peão_preto 1.png", 1, 0, "peao", "preta"),      
        Piece("assets/peão_preto 2.png", 1, 2, "peao", "preta"),      
        Piece("assets/peão_preto 3.png", 1, 5, "peao", "preta"),      
        Piece("assets/peão_preto 4.png", 1, 6, "peao", "preta"),      
        Piece("assets/peão_preto 5.png", 1, 7, "peao", "preta"),      

        # --- PEÇAS BRANCAS ---
        Piece("assets/rei_branco.png", 4, 7, "rei", "branca"),        
        Piece("assets/rainha_branca.png", 0, 7, "rainha", "branca"),  
        Piece("assets/torre_branca.png", 7, 7, "torre", "branca"),    
        Piece("assets/torre_branca_2.png", 4, 0, "torre", "branca"),  
        Piece("assets/bispo_branco 1 .png", 7, 5, "bispo", "branca"), 
        Piece("assets/cavalo_branco.png", 5, 5, "cavalo", "branca"),  
        Piece("assets/peao_branco 1.png", 6, 4, "peao", "branca"),    
        Piece("assets/peao_branco 2.png", 6, 7, "peao", "branca"),    
        Piece("assets/peao_branco 4.png", 4, 6, "peao", "branca"),    
        Piece("assets/peao_branco 5.png", 5, 7, "peao", "branca"),    
    ]

# Lista de peças para a Fase 2 (COM NOMES DE ARQUIVOS CORRIGIDOS FINALMENTE)
def create_initial_pieces_phase2():
    # Mapeamento: Fileira 8 = row 0, Fileira 1 = row 7. Coluna A = col 0, Coluna H = col 7.
    
    return [
        # --- PEÇAS BRANCAS (White) ---
        
        # Rei: h1 (7, 7)
        Piece("assets/rei_branco.png", 7, 7, "rei", "branca"),      
        
        # Rainha: c2 (6, 2)
        Piece("assets/rainha_branca.png", 6, 2, "rainha", "branca"),
        
        # Torre: g1 (7, 6)
        Piece("assets/torre_branca.png", 7, 6, "torre", "branca"),
        
        # Bispo: d3 (5, 3) 
        Piece("assets/bispo_branco 1 .png", 5, 3, "bispo", "branca"),
        
        # Cavalos: c3 (5, 2), d2 (6, 3) 
        Piece("assets/cavalo_branco.png", 5, 2, "cavalo", "branca"),
        Piece("assets/cavalo_branco_2.png", 6, 3, "cavalo", "branca"),
        
        # Peões Brancos
        Piece("assets/peao_branco 1.png", 6, 0, "peao", "branca"),
        Piece("assets/peao_branco 2.png", 6, 1, "peao", "branca"),
        Piece("assets/peao_branco 4.png", 4, 3, "peao", "branca"),
        Piece("assets/peao_branco 5.png", 5, 5, "peao", "branca"),
        Piece("assets/peao_branco 6.png", 6, 6, "peao", "branca"),  # G2
        Piece("assets/peao_branco 7.png", 6, 7, "peao", "branca"),  # H2

        # --- PEÇAS PRETAS (Black) ---
        
        # Rei: g8 (0, 6)
        Piece("assets/rei_preto.png", 0, 6, "rei", "preta"),        
        
        # Torres: a8 (0, 0), f8 (0, 5) 
        Piece("assets/torre_preta.png", 0, 0, "torre", "preta"),
        Piece("assets/torre_preta_2.png", 0, 5, "torre", "preta"),
        
        # Bispo: f4 (4, 5)
        Piece("assets/bispo_preta.png", 4, 5, "bispo", "preta"),
        
        # Cavalos
        Piece("assets/cavalo_preto .png", 1, 3, "cavalo", "preta"),
        Piece("assets/cavalo_preto_2.png", 5, 7, "cavalo", "preta"),
        
        # Peões Pretos
        Piece("assets/peão_preto 1.png", 1, 0, "peao", "preta"),
        Piece("assets/peão_preto 2.png", 1, 1, "peao", "preta"),
        Piece("assets/peão_preto 3.png", 2, 2, "peao", "preta"),
        Piece("assets/peão_preto 4.png", 3, 5, "peao", "preta"),
        Piece("assets/peão_preto 5.png", 1, 6, "peao", "preta"),
        Piece("assets/peão_preto 6.png", 1, 7, "peao", "preta")
    ]

# Função para iniciar uma fase específica
def start_phase(phase, reset_pieces=True):
    global pieces, selected_piece, valid_moves, checkmate_message, game_state, \
           current_turn, board_inverted_display, last_move_description, \
           transition_start_time, transition_message, \
           temporary_message, temporary_message_start_time, \
           last_successful_move_text, last_successful_move_time, \
           current_phase, reset_timer_active, reset_timer_start, \
           error_piece_pos
    
    selected_piece = None
    valid_moves = []
    checkmate_message = None
    reset_timer_active = False
    reset_timer_start = 0
    last_move_description = ""
    transition_start_time = 0
    transition_message = ""
    temporary_message = None # Clear temporary message
    temporary_message_start_time = 0
    last_successful_move_text = "" # Clear successful move message
    last_successful_move_time = 0
    error_piece_pos = None
    
    current_phase = phase

    if phase == 1:
        pieces = create_initial_pieces_phase1()
        game_state = STATE_GAME
        current_turn = "branca"
        board_inverted_display = False
    elif phase == 2:
        pieces = create_initial_pieces_phase2()
        game_state = STATE_GAME_PHASE2
        current_turn = "preta" # Black's turn in Phase 2
        board_inverted_display = True # Invert board for Phase 2
    elif phase == 3:
        pieces = create_initial_pieces_phase3()
        game_state = STATE_GAME_PHASE3
        current_turn = "preta" # Black's turn in Phase 3
        board_inverted_display = True # Invert board for Phase 3

pieces = create_initial_pieces_phase1() # Inicia com a Fase 1
selected_piece = None
valid_moves = []
temporary_message = None # For temporary error/info messages
temporary_message_start_time = 0 # Timer for temporary messages


# Estados do Jogo (ADICIONADO NOVO ESTADO E ALTERADO O NOME DO JOGO)
STATE_MENU = "menu"
STATE_GAME = "playing_phase1"
STATE_VICTORY_MENU = "victory_menu" # NOVO ESTADO para menu de vitória com botão de vídeo
STATE_VIDEO = "playing_video" # NOVO ESTADO para reproduzir vídeo
STATE_PHASE2_START = "phase2_menu" # NOVO ESTADO para o menu da Fase 2
STATE_PHASE3_START = "phase3_menu" # NOVO ESTADO para o menu da Fase 3
STATE_GAME_PHASE2 = "playing_phase2" # NOVO ESTADO para o jogo da Fase 2
STATE_GAME_PHASE3 = "playing_phase3" # NOVO ESTADO para o jogo da Fase 3
STATE_VICTORY_MENU_PHASE2 = "victory_menu_phase2" # Menu de vitória da Fase 2
STATE_VICTORY_MENU_PHASE3 = "victory_menu_phase3" # Menu de vitória da Fase 3
STATE_TRANSITION_PHASE1_VICTORY = "transition_phase1_victory" # Novo estado para transição de vitória
STATE_TRANSITION_PHASE2_VICTORY = "transition_phase2_victory" # Novo estado para transição de vitória
STATE_TRANSITION_PHASE3_VICTORY = "transition_phase3_victory" # Novo estado para transição de vitória
game_state = STATE_MENU # O jogo começa no menu

# Variáveis para controle de vídeo
video_start_time = 0
video_duration = 10000  # 10 segundos para o vídeo

# --- FUNÇÕES DE DESENHO ---

def draw_board():
    pygame.draw.rect(screen, BLACK, (MARGIN - 2, MARGIN - 2, BOARD_SIZE + 4, BOARD_SIZE + 4), 2)
    for row in range(8):
        for col in range(8):
            color = WHITE if (row + col) % 2 == 0 else LIGHT_GRAY
            
            draw_row = row
            # Inverte a linha para a perspectiva das pretas
            if board_inverted_display:
                draw_row = 7 - row
            
            x = col * CELL_SIZE + MARGIN
            y = draw_row * CELL_SIZE + MARGIN
            pygame.draw.rect(screen, color, (x, y, CELL_SIZE, CELL_SIZE))

def draw_coordinates():
    for col in range(8):
        letter = chr(ord('A') + col)
        text = font.render(letter, True, BLACK)
        
        # Colunas não são invertidas por padrão
        draw_col = col
        
        x_coord = draw_col * CELL_SIZE + MARGIN + CELL_SIZE // 2 - text.get_width() // 2
        
        # Coordenadas superiores (sempre visíveis)
        screen.blit(text, (x_coord, 5))
        # Coordenadas inferiores (sempre visíveis)
        screen.blit(text, (x_coord, HEIGHT - MARGIN + 5))
        
    for row in range(8):
        # O número do rank depende da perspectiva de exibição
        if board_inverted_display:
            number = str(row + 1) # Se a linha 0 da tela é rank 1, linha 7 da tela é rank 8
        else:
            number = str(8 - row) # Se a linha 0 da tela é rank 8, linha 7 da tela é rank 1
        text = font.render(number, True, BLACK)
        
        y_coord = row * CELL_SIZE + MARGIN + CELL_SIZE // 2 - text.get_height() // 2
        
        # Coordenadas da esquerda (sempre visíveis)
        screen.blit(text, (MARGIN - 30, y_coord))
        # Coordenadas da direita (sempre visíveis)
        screen.blit(text, (WIDTH - MARGIN + 10, y_coord))

def draw_valid_moves(moves):
    for row, col in moves:
        draw_row = row
        # Inverte a linha para a perspectiva das pretas
        if board_inverted_display:
            draw_row = 7 - row
        
        x = col * CELL_SIZE + MARGIN + CELL_SIZE // 2
        y = draw_row * CELL_SIZE + MARGIN + CELL_SIZE // 2
        pygame.draw.circle(screen, GREEN, (x, y), 10)


# Função para desenhar menu de vitória com botão de vídeo
def draw_victory_menu():
    screen.fill(MENU_BACKGROUND_COLOR)
    
    # Título de vitória
    title_font = pygame.font.SysFont("Arial", 72, bold=True)
    title_text = title_font.render("BEIJO DA MORTE!", True, (255, 215, 0))
    title_rect = title_text.get_rect(center=(WIDTH // 2, HEIGHT // 3 - 50))
    screen.blit(title_text, title_rect)
    
    subtitle_font = pygame.font.SysFont("Arial", 48)
    subtitle_text = subtitle_font.render("VITÓRIA!", True, (255, 100, 100))
    subtitle_rect = subtitle_text.get_rect(center=(WIDTH // 2, HEIGHT // 3))
    screen.blit(subtitle_text, subtitle_rect)
    
    # Botão para reproduzir vídeo
    button_width = 300
    button_height = 70
    button_x = (WIDTH - button_width) // 2
    button_y = HEIGHT // 2
    
    video_button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
    
    mouse_pos = pygame.mouse.get_pos()
    button_color = BUTTON_HOVER_COLOR if video_button_rect.collidepoint(mouse_pos) else BUTTON_COLOR
    
    pygame.draw.rect(screen, button_color, video_button_rect, border_radius=10)
    
    button_font = pygame.font.SysFont("Arial", 36)
    button_text = button_font.render("ASSISTIR VÍDEO", True, WHITE)
    button_text_rect = button_text.get_rect(center=video_button_rect.center)
    screen.blit(button_text, button_text_rect)
    
    # Botão para pular para Fase 2
    skip_button_y = HEIGHT // 2 + 100
    skip_button_rect = pygame.Rect(button_x, skip_button_y, button_width, button_height)
    
    skip_button_color = BUTTON_HOVER_COLOR if skip_button_rect.collidepoint(mouse_pos) else BUTTON_COLOR
    
    pygame.draw.rect(screen, skip_button_color, skip_button_rect, border_radius=10)
    
    skip_text = button_font.render("PULAR PARA FASE 2", True, WHITE)
    skip_text_rect = skip_text.get_rect(center=skip_button_rect.center)
    screen.blit(skip_text, skip_text_rect)
    
    return video_button_rect, skip_button_rect

# Função para desenhar a tela de vitória da Fase 2 (Estilo image_7.png)
def draw_victory_menu_phase2():
    screen.fill((0, 0, 50)) # Fundo Azul marinho profundo
    
    # Texto Principal: Amarelo, Negrito, Caixa Alta
    title_font = pygame.font.SysFont("Arial", 60, bold=True)
    title_text = title_font.render("SEGUNDA FASE CONCLUÍDA!", True, (255, 215, 0)) # Amarelo
    title_rect = title_text.get_rect(center=(WIDTH // 2, HEIGHT // 3 - 50))
    screen.blit(title_text, title_rect)
    
    # Subtexto: Rosa/Coral, Caixa Alta
    subtitle_font = pygame.font.SysFont("Arial", 48, bold=True)
    subtitle_text = subtitle_font.render("VITÓRIA!", True, (255, 127, 127)) # Rosa/Coral
    subtitle_rect = subtitle_text.get_rect(center=(WIDTH // 2, HEIGHT // 3 + 20))
    screen.blit(subtitle_text, subtitle_rect)
    
    button_width = 350
    button_height = 70
    button_x = (WIDTH - button_width) // 2
    
    VIBRANT_GREEN = (0, 200, 0)
    HOVER_GREEN = (0, 230, 0)
    mouse_pos = pygame.mouse.get_pos()
    
    # Botão Superior: VER REPLAY DA FASE
    replay_rect = pygame.Rect(button_x, HEIGHT // 2, button_width, button_height)
    color1 = HOVER_GREEN if replay_rect.collidepoint(mouse_pos) else VIBRANT_GREEN
    pygame.draw.rect(screen, color1, replay_rect, border_radius=15)
    txt1 = font.render("VER REPLAY DA FASE", True, WHITE)
    screen.blit(txt1, txt1.get_rect(center=replay_rect.center))
    # Botão Superior: ASSISTIR VÍDEO
    video_rect = pygame.Rect(button_x, HEIGHT // 2, button_width, button_height)
    color1 = HOVER_GREEN if video_rect.collidepoint(mouse_pos) else VIBRANT_GREEN
    pygame.draw.rect(screen, color1, video_rect, border_radius=15)
    txt1 = font.render("ASSISTIR VÍDEO", True, WHITE)
    screen.blit(txt1, txt1.get_rect(center=video_rect.center))
    
    # Botão Inferior: PULAR PARA FASE 3
    skip_rect = pygame.Rect(button_x, HEIGHT // 2 + 100, button_width, button_height)
    color2 = HOVER_GREEN if skip_rect.collidepoint(mouse_pos) else VIBRANT_GREEN
    pygame.draw.rect(screen, color2, skip_rect, border_radius=15)
    txt2 = font.render("PULAR PARA FASE 3", True, WHITE)
    screen.blit(txt2, txt2.get_rect(center=skip_rect.center))
    
    return replay_rect, skip_rect
    return video_rect, skip_rect

# Função para desenhar menu de vitória da Fase 3
def draw_victory_menu_phase3():
    screen.fill(MENU_BACKGROUND_COLOR)
    
    title_font = pygame.font.SysFont("Arial", 72, bold=True)
    title_text = title_font.render("VITÓRIA TOTAL!", True, (255, 215, 0))
    title_rect = title_text.get_rect(center=(WIDTH // 2, HEIGHT // 3 - 50))
    screen.blit(title_text, title_rect)
    
    subtitle_font = pygame.font.SysFont("Arial", 48)
    subtitle_text = subtitle_font.render("LENDA DO XADREZ!", True, (255, 100, 100))
    subtitle_rect = subtitle_text.get_rect(center=(WIDTH // 2, HEIGHT // 3))
    screen.blit(subtitle_text, subtitle_rect)
    
    button_width = 320
    button_height = 70
    button_x = (WIDTH - button_width) // 2
    button_y = HEIGHT // 2
    
    menu_button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
    mouse_pos = pygame.mouse.get_pos()
    color = BUTTON_HOVER_COLOR if menu_button_rect.collidepoint(mouse_pos) else BUTTON_COLOR
    pygame.draw.rect(screen, color, menu_button_rect, border_radius=15)
    
    btn_font = pygame.font.SysFont("Arial", 36)
    btn_text = btn_font.render("VOLTAR AO MENU", True, WHITE)
    screen.blit(btn_text, btn_text.get_rect(center=menu_button_rect.center))
    
    return menu_button_rect

def play_video(video_name="YARA.MP4"):
    import subprocess
    import os
    
    # Tentar vários caminhos possíveis para o vídeo solicitado
    possible_paths = [
        os.path.join(os.getcwd(), "assets", video_name),
        os.path.join("assets", video_name),
        "assets/" + video_name,
        video_name
    ]
    
    for video_path in possible_paths:
        if os.path.exists(video_path):
            try:
                # Tentar diferentes métodos para abrir o vídeo
                subprocess.run(["start", "", video_path], shell=True, check=False)
                print(f"Vídeo encontrado e reproduzido: {video_path}")
                return
            except Exception as e:
                print(f"Erro ao reproduzir vídeo: {e}")
                try:
                    # Método alternativo
                    os.startfile(video_path)
                    print(f"Vídeo reproduzido com os.startfile: {video_path}")
                    return
                except Exception as e2:
                    print(f"Erro com os.startfile: {e2}")
    
    print("Vídeo não encontrado em nenhum caminho:") 
    for path in possible_paths:
        print(f"  - {path}: {'Existe' if os.path.exists(path) else 'Não existe'}")
    print(f"Diretório atual: {os.getcwd()}")
    print(f"Arquivos na pasta assets: {os.listdir('assets') if os.path.exists('assets') else 'Pasta assets não existe'}")

# Função de desenho da mensagem de fim de jogo (AJUSTADA)
# Esta função será usada APENAS para as mensagens de transição de vitória
def draw_victory_transition_message(message, last_move_desc):
    
    if message:
        background_surface = pygame.Surface((WIDTH, HEIGHT))
        background_surface.fill(BLACK) 
        background_surface.set_alpha(180) 
        screen.blit(background_surface, (0, 0))
        
        # Divide a mensagem em título e subtítulo, se houver "! "
        lines = message.split('! ', 1) # Divide apenas na primeira ocorrência
        
        title_font = pygame.font.SysFont("Arial", 48, bold=True)
        title_text = title_font.render(lines[0] + ("!" if len(lines) > 1 else ""), True, (255, 215, 0)) 
        title_rect = title_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 40))
        screen.blit(title_text, title_rect)
        
        if len(lines) > 1:
            message_font = pygame.font.SysFont("Arial", 36)
            message_text = message_font.render(lines[1], True, (200, 0, 0)) 
            message_rect = message_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 30))
            screen.blit(message_text, message_rect)
        
        # Exibe a descrição do último movimento durante a transição
        move_font = pygame.font.SysFont("Arial", 28)
        move_text = move_font.render(last_move_desc, True, WHITE)
        move_rect = move_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 80))
        screen.blit(move_text, move_rect)

# Nova função para desenhar mensagens temporárias (erros, etc.)
def draw_temporary_message(message):
    if message:
        # Fundo semi-transparente para a mensagem temporária
        overlay_surface = pygame.Surface((WIDTH, 100), pygame.SRCALPHA) # Altura fixa para a mensagem
        overlay_surface.fill((0, 0, 0, 180)) # Preto semi-transparente
        
        # Posição centralizada no topo da tela
        overlay_rect = overlay_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 150))
        screen.blit(overlay_surface, overlay_rect)
        
        # Fonte menor para mensagens de erro
        message_font = pygame.font.SysFont("Arial", 24) 
        message_text = message_font.render(message, True, (255, 255, 0)) # Amarelo para destaque
        message_text_rect = message_text.get_rect(center=overlay_rect.center)
        screen.blit(message_text, message_text_rect)

# Modificado para desenhar seta e quadrado no canto inferior direito
def draw_turn_indicator():
    # Define a cor do quadrado e da seta com base no turno
    indicator_square_color = WHITE if current_turn == "branca" else BLACK
    
    square_size = 45 
    # Ocupa o espaço total da margem até o tabuleiro (40x40 se MARGIN for 40)
    square_size = MARGIN 
    
    # Posiciona o quadrado rente ao canto inferior direito do tabuleiro (dentro da área visível)
    square_x = WIDTH - square_size - 5
    square_y = HEIGHT - square_size - 5
    # Posiciona exatamente no canto inferior direito, preenchendo a margem
    square_x = WIDTH - square_size
    square_y = HEIGHT - square_size
    
    # Desenha o quadrado
    pygame.draw.rect(screen, indicator_square_color, (square_x, square_y, square_size, square_size))
    
    # Desenha a seta apontando para cima dentro do quadrado
    arrow_center_x = square_x + square_size // 2
    arrow_center_y = square_y + square_size // 2
    
    arrow_height = 15 
    arrow_width = 15  
    arrow_height = square_size // 2
    arrow_width = square_size // 2
    
    # A cor da seta deve ser contrastante com o quadrado
    arrow_color = BLACK if current_turn == "branca" else WHITE
    
    pygame.draw.polygon(screen, arrow_color, [
        (arrow_center_x, arrow_center_y - arrow_height // 2), # Topo
        (arrow_center_x - arrow_width // 2, arrow_center_y + arrow_height // 2), # Base esquerda
        (arrow_center_x + arrow_width // 2, arrow_center_y + arrow_height // 2)  # Base direita
    ])

# FUNÇÃO DE DESENHO DO MENU COM BOTÃO (MANTIDA/AJUSTADA)
def draw_start_menu(screen, title_text, button_text):
    """Desenha uma tela de menu genérica com título e botão."""
    screen.fill(MENU_BACKGROUND_COLOR) 
    
    # 1. Título
    title_font = pygame.font.SysFont("Arial", 72)
    title = title_font.render(title_text, True, WHITE)
    title_rect = title.get_rect(center=(WIDTH // 2, HEIGHT // 3))
    screen.blit(title, title_rect)
    
    # 2. Botão "Iniciar Jogo"
    button_width = 350
    button_height = 70
    button_x = (WIDTH - button_width) // 2
    button_y = HEIGHT // 3 * 2 - button_height // 2 

    start_button_rect = pygame.Rect(button_x, button_y, button_width, button_height)

    mouse_pos = pygame.mouse.get_pos()
    current_button_color = BUTTON_COLOR
    if start_button_rect.collidepoint(mouse_pos):
        current_button_color = BUTTON_HOVER_COLOR

    pygame.draw.rect(screen, current_button_color, start_button_rect, border_radius=10) 
    
    button_font = pygame.font.SysFont("Arial", 36)
    button = button_font.render(button_text, True, WHITE)
    button_text_rect = button.get_rect(center=start_button_rect.center)
    screen.blit(button, button_text_rect)

    return start_button_rect

# Funções de lógica do jogo
def get_valid_moves(piece, pieces):
    return piece.get_moves(pieces)

def is_king_in_check(king, pieces):
    for piece in pieces:
        if piece.cor != king.cor:
            moves = piece.get_moves(pieces)
            if (king.row, king.col) in moves:
                return True
    return False

def would_king_be_in_check(king, pieces, move_piece, new_row, new_col):
    original_row, original_col = move_piece.row, move_piece.col
    captured_piece = next((p for p in pieces if p.row == new_row and p.col == new_col), None)
    
    move_piece.row, move_piece.col = new_row, new_col
    if captured_piece:
        pieces.remove(captured_piece)
    
    in_check = is_king_in_check(king, pieces)
    
    move_piece.row, move_piece.col = original_row, original_col
    if captured_piece:
        pieces.append(captured_piece)
    
    return in_check

def is_checkmate(king, pieces):
    if not is_king_in_check(king, pieces):
        return False
    
    for piece in pieces:
        if piece.cor == king.cor:
            all_moves = piece.get_moves(pieces)
            legal_moves = [
                move for move in all_moves
                if not would_king_be_in_check(king, pieces, piece, move[0], move[1])
            ]
            if legal_moves:
                return False
    return True

# Loop principal do jogo
running = True
start_button_rect = None
phase2_button_rect = None
phase3_button_rect = None
menu_button_rect_p3 = None
video_button_rect, skip_button_rect = None, None
video_button_rect_p2, skip_button_rect_p2 = None, None

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = event.pos

            if game_state == STATE_MENU:
                if start_button_rect and start_button_rect.collidepoint(mouse_x, mouse_y):
                    start_phase(1)
            
            elif game_state == STATE_PHASE2_START:
                if phase2_button_rect and phase2_button_rect.collidepoint(mouse_x, mouse_y):
                    start_phase(2)
            elif game_state == STATE_PHASE3_START:
                if phase3_button_rect and phase3_button_rect.collidepoint(mouse_x, mouse_y):
                    start_phase(3)
            elif game_state == STATE_VICTORY_MENU_PHASE2:
                if replay_button_rect_p2 and replay_button_rect_p2.collidepoint(mouse_x, mouse_y):
                    start_phase(2)
                if video_button_rect_p2 and video_button_rect_p2.collidepoint(mouse_x, mouse_y):
                    play_video("cucacaldeirao.MP4")
                    start_phase(3)
                    game_state = STATE_PHASE3_START
                elif skip_button_rect_p2 and skip_button_rect_p2.collidepoint(mouse_x, mouse_y):
                    start_phase(3)
            
            elif game_state == STATE_VICTORY_MENU_PHASE3:
                if menu_button_rect_p3 and menu_button_rect_p3.collidepoint(mouse_x, mouse_y):
                    game_state = STATE_MENU
                    start_phase(1) # Volta para o menu e reinicia a fase 1
            
            # Lógica de jogo (movimento de peças)
            elif game_state in [STATE_GAME, STATE_GAME_PHASE2, STATE_GAME_PHASE3]:
                # Ignora cliques durante a transição de vitória ou durante o delay de erro
                if game_state in [STATE_TRANSITION_PHASE1_VICTORY, STATE_TRANSITION_PHASE2_VICTORY, STATE_TRANSITION_PHASE3_VICTORY] or reset_timer_active:
                    continue

                col = (mouse_x - MARGIN) // CELL_SIZE
                row = (mouse_y - MARGIN) // CELL_SIZE
                
                # Ajusta a linha se o tabuleiro estiver invertido para exibição
                if board_inverted_display:
                    row = 7 - row
                
                if 0 <= row < 8 and 0 <= col < 8:
                    if selected_piece:
                        if (row, col) in valid_moves:
                            # Salva o estado atual do tabuleiro antes de fazer o movimento para possível reversão
                            temp_pieces_state = [p.copy() for p in pieces]
                            original_selected_piece_pos = (selected_piece.row, selected_piece.col)

                            captured_piece = next((p for p in pieces if p.row == row and p.col == col and p.cor != selected_piece.cor), None)
                            
                            if captured_piece:
                                pieces.remove(captured_piece)
                            
                            selected_piece.row = row
                            selected_piece.col = col

                            # Define a descrição do movimento aqui, antes de qualquer verificação de vitória ou xeque
                            move_description_for_display = f"{selected_piece.tipo.capitalize()} {selected_piece.cor} de {chr(ord('a') + original_selected_piece_pos[1])}{8 - original_selected_piece_pos[0]} para {chr(ord('a') + col)}{8 - row}"

                            # Verifica se o movimento coloca o próprio rei em xeque
                            current_player_king = next((p for p in pieces if p.tipo == "rei" and p.cor == current_turn), None)
                            if current_player_king and is_king_in_check(current_player_king, pieces):
                                print("Movimento inválido: Rei em xeque após o movimento.")
                                pieces = temp_pieces_state # Reverte o tabuleiro
                                selected_piece = None
                                valid_moves = []
                                temporary_message = "Movimento incorreto! Seu rei estaria em xeque."
                                temporary_message_start_time = pygame.time.get_ticks()
                                continue # Pula para o próximo evento

                            enemy_king_color = "preta" if selected_piece.cor == "branca" else "branca"
                            enemy_king = next((p for p in pieces if p.tipo == "rei" and p.cor == enemy_king_color), None)
                            
                            move_successful = False # Flag para indicar se o movimento levou à vitória

                            # Condição especial da Fase 3: Vitória ao levar a Rainha para o alvo (ajustado para linha 3 após inversão)
                            if game_state == STATE_GAME_PHASE3 and selected_piece.tipo == "rainha" and row == 3 and col == 6:
                                last_move_description = move_description_for_display
                                transition_message = "Terceira Fase: Rainha em G4! Vitória Total!"
                                game_state = STATE_TRANSITION_PHASE3_VICTORY
                                transition_start_time = pygame.time.get_ticks()
                                move_successful = True
                            
                            elif enemy_king and is_checkmate(enemy_king, pieces):
                                last_move_description = f"{selected_piece.tipo.capitalize()} {selected_piece.cor} de {chr(ord('a') + original_selected_piece_pos[1])}{8 - original_selected_piece_pos[0]} para {chr(ord('a') + col)}{8 - row}"
                                last_move_description = move_description_for_display
                                if game_state == STATE_GAME: # Fase 1
                                    transition_message = "Vitória das Brancas! Movimento correto:"
                                    game_state = STATE_TRANSITION_PHASE1_VICTORY
                                elif game_state == STATE_GAME_PHASE2: # Fase 2
                                    transition_message = "Pretas venceram! Movimento vencedor:"
                                    game_state = STATE_TRANSITION_PHASE2_VICTORY
                                elif game_state == STATE_GAME_PHASE3: # Fase 3 (se xeque-mate for uma condição de vitória além da rainha em g4)
                                    transition_message = "Vitória das Pretas! Movimento vencedor:"
                                    game_state = STATE_TRANSITION_PHASE3_VICTORY
                                
                                transition_start_time = pygame.time.get_ticks()
                                move_successful = True
                            
                            # Se o movimento foi válido mas não vencedor, mostra por 3 segundos e reinicia a fase
                            if not move_successful:
                                last_successful_move_text = "Movimento incorreto para vencer"
                                error_piece_pos = (row, col)
                                last_successful_move_time = pygame.time.get_ticks()
                                reset_timer_active = True
                                reset_timer_start = pygame.time.get_ticks()
                            
                            selected_piece = None
                            valid_moves = []
                        else:
                            selected_piece = None
                            valid_moves = []
                    else:
                        for piece in pieces:
                            if piece.row == row and piece.col == col:
                                # Permite selecionar apenas peças do turno atual
                                if piece.cor == current_turn:
                                    selected_piece = piece
                                    all_moves = get_valid_moves(piece, pieces)
                                    
                                    # Filtra movimentos para garantir que não coloquem o próprio rei em xeque
                                    current_player_king = next((p for p in pieces if p.tipo == "rei" and p.cor == piece.cor), None)
                                    if current_player_king:
                                        valid_moves = [
                                            move for move in all_moves
                                            if not would_king_be_in_check(current_player_king, pieces, piece, move[0], move[1])
                                        ]
                                    else:
                                        valid_moves = [] # Não deve acontecer em um jogo de xadrez válido
                                    break
                                else:
                                    # Clicou em uma peça do oponente ou da cor errada
                                    selected_piece = None
                                    valid_moves = [] # Clear valid moves
                                    temporary_message = "Não é sua vez de mover esta peça."
                                    temporary_message_start_time = pygame.time.get_ticks()
                                    break
            
            elif game_state == STATE_VICTORY_MENU:
                if video_button_rect and video_button_rect.collidepoint(mouse_x, mouse_y):
                    play_video()
                    game_state = STATE_PHASE2_START
                elif skip_button_rect and skip_button_rect.collidepoint(mouse_x, mouse_y):
                    game_state = STATE_PHASE2_START
    

    # Desenho
    if game_state == STATE_MENU:
        start_button_rect = draw_start_menu(screen, "XADREZ DAS LENDAS", "INICIAR FASE 1")
    
    elif game_state == STATE_PHASE2_START:
        phase2_button_rect = draw_start_menu(screen, "FASE 1 CONCLUÍDA!", "START GAME FASE 2")
    
    elif game_state == STATE_PHASE3_START:
        phase3_button_rect = draw_start_menu(screen, "FASE 2 CONCLUÍDA!", "START GAME FASE 3")

    elif game_state == STATE_VICTORY_MENU:
        video_button_rect, skip_button_rect = draw_victory_menu()
    
    elif game_state == STATE_VICTORY_MENU_PHASE2:
        replay_button_rect_p2, skip_button_rect_p2 = draw_victory_menu_phase2()
        video_button_rect_p2, skip_button_rect_p2 = draw_victory_menu_phase2()
    
    elif game_state == STATE_VICTORY_MENU_PHASE3:
        menu_button_rect_p3 = draw_victory_menu_phase3()
    
    # Novos estados de transição de vitória
    elif game_state in [STATE_TRANSITION_PHASE1_VICTORY, STATE_TRANSITION_PHASE2_VICTORY, STATE_TRANSITION_PHASE3_VICTORY]:
        screen.fill(BLACK) # Fundo preto para a transição
        # Desenha o tabuleiro e as peças em seu estado final
        screen.fill(GAME_BACKGROUND_COLOR) # Preenche o fundo primeiro
        draw_board()
        draw_coordinates()
        for piece in pieces:
            piece.draw(screen, MARGIN, MARGIN, board_inverted_display)

        # Exibe a mensagem de transição e o último movimento
        draw_victory_transition_message(transition_message, last_move_description)
        if pygame.time.get_ticks() - transition_start_time > 6000: # Reduzido para 6 segundos
            if game_state == STATE_TRANSITION_PHASE1_VICTORY:
                game_state = STATE_VICTORY_MENU
            elif game_state == STATE_TRANSITION_PHASE2_VICTORY:
                game_state = STATE_VICTORY_MENU_PHASE2
            elif game_state == STATE_TRANSITION_PHASE3_VICTORY:
                game_state = STATE_VICTORY_MENU_PHASE3
            
            # Reseta as variáveis de transição
            transition_start_time = 0
            transition_message = ""
            last_move_description = "" # Limpa a descrição do último movimento

    elif game_state in [STATE_GAME, STATE_GAME_PHASE2, STATE_GAME_PHASE3]:
        screen.fill(GAME_BACKGROUND_COLOR)
        
        draw_board()
        draw_coordinates()
        draw_valid_moves(valid_moves)
        
        for piece in pieces:
            # Passa o flag board_inverted_display para o método draw da peça
            piece.draw(screen, MARGIN, MARGIN, board_inverted_display)
        
        draw_turn_indicator() # Desenha o indicador de turno (seta e quadrado)
        
        # Desenha mensagens temporárias (erros)
        if temporary_message and pygame.time.get_ticks() - temporary_message_start_time < 3000:
            draw_temporary_message(temporary_message)
        else:
            temporary_message = None # Limpa a mensagem após 3 segundos

        # Desenha a descrição do último movimento bem-sucedido (não vencedor)
        if last_successful_move_text and pygame.time.get_ticks() - last_successful_move_time < 4000:
            move_desc_font = pygame.font.SysFont("Arial", 18, bold=True)
            move_desc_text = move_desc_font.render(last_successful_move_text, True, (200, 0, 0)) # Vermelho para erro
            
            if error_piece_pos:
                r, c = error_piece_pos
                draw_row = 7 - r if board_inverted_display else r
                x = c * CELL_SIZE + MARGIN + CELL_SIZE // 2
                y = draw_row * CELL_SIZE + MARGIN - 15 # Posiciona acima da peça
                move_desc_rect = move_desc_text.get_rect(center=(x, y))
                
                # Desenha um pequeno fundo para garantir que o texto seja legível sobre o tabuleiro
                bg_rect = move_desc_rect.inflate(10, 4)
                pygame.draw.rect(screen, WHITE, bg_rect, border_radius=3)
                pygame.draw.rect(screen, BLACK, bg_rect, 1, border_radius=3)
            else:
                move_desc_rect = move_desc_text.get_rect(center=(WIDTH // 2, MARGIN // 2))
                
            screen.blit(move_desc_text, move_desc_rect)
    
    # Lógica de reinício após movimento errado
    if reset_timer_active and pygame.time.get_ticks() - reset_timer_start > 3000:
        start_phase(current_phase)
        reset_timer_active = False
        reset_timer_start = 0

    pygame.display.flip()

pygame.quit()