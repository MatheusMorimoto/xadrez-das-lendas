import pygame
import os
import math 
try:
    import cv2
    OPENCV_AVAILABLE = True
except ImportError:
    OPENCV_AVAILABLE = False

# Variável global para controle do vídeo interno
video_cap = None

# --- CONFIGURAÇÕES DE ESCALA PROPORCIONAL AO NOTEBOOK ---
pygame.init()
info = pygame.display.Info()

# Garante que a altura da tela não seja zero para evitar janelas invisíveis
screen_h = info.current_h if info.current_h > 0 else 720
# Calcula a escala para que o jogo ocupe aproximadamente 85% da altura da tela do notebook
SCALE = (screen_h * 0.85) / 720.0
# Define um limite mínimo para a escala
SCALE = max(0.5, SCALE)

CELL_SIZE = int(80 * SCALE)
MARGIN = int(40 * SCALE)
BOARD_SIZE = CELL_SIZE * 8
WIDTH = BOARD_SIZE + MARGIN * 2
HEIGHT = BOARD_SIZE + MARGIN * 2

# Define o diretório base como a raiz do projeto (um nível acima da pasta main.py)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
# Se a pasta 'assets' estiver diretamente em D:\projeto sabado, você pode tentar:
# ASSETS_DIR = os.path.join(os.getcwd(), "assets")
# Vou manter a primeira opção, pois é mais robusta para scripts Python.

# Função auxiliar para verificar a ocupação (útil dentro da classe Piece)
def get_piece_at(row, col, pieces):
    return next((p for p in pieces if p.row == row and p.col == col), None)

# Classe da peça (COM MÉTODO get_moves INTEGRADO)
class Piece:
    def __init__(self, image_path_relative, row, col, tipo, cor):
        # Extrai apenas o nome do arquivo e busca dentro de ASSETS_DIR
        file_name = os.path.basename(image_path_relative)
        full_image_path = os.path.join(ASSETS_DIR, file_name)
        
        try:
            # Tenta carregar usando o caminho completo a partir do diretório de trabalho atual
            loaded_image = pygame.image.load(full_image_path).convert_alpha()
            loaded_image.set_colorkey((0, 0, 0)) # Define a cor preta das bordas como transparente
            self.image = pygame.transform.scale(loaded_image, (CELL_SIZE, CELL_SIZE))
            print(f"Sucesso ao carregar: {full_image_path}") # Mensagem de sucesso
        except (pygame.error, FileNotFoundError) as e:
            # O erro persiste, exibe a peça magenta
            print(f"ERRO PERSISTENTE ao carregar a imagem {full_image_path}: {e}")
            self.image = pygame.Surface((CELL_SIZE, CELL_SIZE))
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
        # A lógica atual de desenho (y = self.row * CELL_SIZE) já faz isso se considerarmos row 0 como o topo.
        # Para inverter a perspectiva, row 0 (rank 8) deve ser desenhada no topo para brancas,
        # e row 0 (rank 8) deve ser desenhada no fundo para pretas.
        # Portanto, para a perspectiva das pretas, invertemos a coordenada Y.
        if board_inverted_display:
            draw_row = 7 - self.row
        
        x = self.col * CELL_SIZE + offset_x # Colunas não são invertidas por padrão
        y = draw_row * CELL_SIZE + offset_y
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
font = pygame.font.SysFont("Arial", int(24 * SCALE))
clock = pygame.time.Clock() # Criado para controlar a velocidade do vídeo e do jogo

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Tabuleiro de Xadrez")

# Cores (mantido)
WHITE = (255, 255, 255)
LIGHT_GRAY = (200, 200, 200)
BLACK = (0, 0, 0)
GREEN = (0, 150, 0)
GOLD = (255, 215, 0)
BOARD_LIGHT_GREEN = (144, 238, 144)
BOARD_DARK_GREEN = (0, 100, 0)
MENU_BACKGROUND_COLOR = (0, 0, 50)
WOOD_BROWN = (101, 67, 33)
GAME_BACKGROUND_COLOR = WOOD_BROWN
BUTTON_COLOR = (50, 150, 50) 
BUTTON_HOVER_COLOR = (80, 180, 80)

# Carregamento da imagem de fundo do menu
MENU_BG_IMAGE = None
possible_image_names = [
    os.path.join(ASSETS_DIR, "tela_inicio.png"),
    os.path.join(ASSETS_DIR, "tela inicio.png"),
    "assets/tela_inicio.png",
    "assets/tela inicio.png",
    "tela_inicio.png"
]
for img_path in possible_image_names:
    if os.path.exists(img_path):
        try:
            MENU_BG_IMAGE = pygame.image.load(img_path).convert()
            MENU_BG_IMAGE = pygame.transform.scale(MENU_BG_IMAGE, (WIDTH, HEIGHT))
            break
        except Exception as e:
            print(f"Erro ao carregar {img_path}: {e}")

RESTART_BUTTON_RECT = pygame.Rect(WIDTH // 2 - int(125 * SCALE), HEIGHT // 2 + int(80 * SCALE), int(250 * SCALE), int(60 * SCALE))

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
STATE_CAMPAIGN_FINISHED = "campaign_finished" # Novo estado para fim da campanha
game_state = STATE_MENU # O jogo começa no menu

# Variáveis para controle de vídeo
video_start_time = 0
video_duration = 10000  # 10 segundos para o vídeo

# --- FUNÇÕES DE DESENHO ---

def draw_board():
    pygame.draw.rect(screen, BLACK, (MARGIN - 2, MARGIN - 2, BOARD_SIZE + 4, BOARD_SIZE + 4), int(2 * SCALE))
    for row in range(8):
        for col in range(8):
            color = BOARD_LIGHT_GREEN if (row + col) % 2 == 0 else BOARD_DARK_GREEN
            
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
        screen.blit(text, (MARGIN - int(30 * SCALE), y_coord))
        # Coordenadas da direita (sempre visíveis)
        screen.blit(text, (WIDTH - MARGIN + int(10 * SCALE), y_coord))

def draw_valid_moves(moves):
    for row, col in moves:
        draw_row = row
        # Inverte a linha para a perspectiva das pretas
        if board_inverted_display:
            draw_row = 7 - row
        
        x = col * CELL_SIZE + MARGIN + CELL_SIZE // 2
        y = draw_row * CELL_SIZE + MARGIN + CELL_SIZE // 2
        pygame.draw.circle(screen, GREEN, (x, y), int(10 * SCALE))


# Função para desenhar menu de vitória com botão de vídeo
def draw_victory_menu():
    screen.fill(MENU_BACKGROUND_COLOR)
    
    # Título de vitória
    title_font = pygame.font.SysFont("Arial", int(72 * SCALE), bold=True)
    title_text = title_font.render("BEIJO DA MORTE!", True, (255, 215, 0))
    title_rect = title_text.get_rect(center=(WIDTH // 2, HEIGHT // 3 - int(50 * SCALE)))
    screen.blit(title_text, title_rect)
    
    subtitle_font = pygame.font.SysFont("Arial", int(48 * SCALE))
    subtitle_text = subtitle_font.render("VITÓRIA!", True, (255, 100, 100))
    subtitle_rect = subtitle_text.get_rect(center=(WIDTH // 2, HEIGHT // 3))
    screen.blit(subtitle_text, subtitle_rect)
    
    # Botão para reproduzir vídeo
    button_width = int(300 * SCALE)
    button_height = int(70 * SCALE)
    button_x = (WIDTH - button_width) // 2
    button_y = HEIGHT // 2
    
    video_button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
    
    mouse_pos = pygame.mouse.get_pos()
    button_color = BUTTON_HOVER_COLOR if video_button_rect.collidepoint(mouse_pos) else BUTTON_COLOR
    
    pygame.draw.rect(screen, button_color, video_button_rect, border_radius=10)
    
    button_font = pygame.font.SysFont("Arial", int(36 * SCALE))
    button_text = button_font.render("ASSISTIR VÍDEO", True, WHITE)
    button_text_rect = button_text.get_rect(center=video_button_rect.center)
    screen.blit(button_text, button_text_rect)
    
    # Botão para pular para Fase 2
    skip_button_y = HEIGHT // 2 + int(100 * SCALE)
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
    title_font = pygame.font.SysFont("Arial", int(60 * SCALE), bold=True)
    title_text = title_font.render("SEGUNDA FASE CONCLUÍDA!", True, (255, 215, 0)) # Amarelo
    title_rect = title_text.get_rect(center=(WIDTH // 2, HEIGHT // 3 - 50))
    screen.blit(title_text, title_rect)
    
    # Subtexto: Rosa/Coral, Caixa Alta
    subtitle_font = pygame.font.SysFont("Arial", int(48 * SCALE), bold=True)
    subtitle_text = subtitle_font.render("VITÓRIA!", True, (255, 127, 127)) # Rosa/Coral
    subtitle_rect = subtitle_text.get_rect(center=(WIDTH // 2, HEIGHT // 3 + 20))
    screen.blit(subtitle_text, subtitle_rect)
    
    button_width = int(350 * SCALE)
    button_height = int(70 * SCALE)
    button_x = (WIDTH - button_width) // 2
    
    VIBRANT_GREEN = (0, 200, 0)
    HOVER_GREEN = (0, 230, 0)
    mouse_pos = pygame.mouse.get_pos()
    
    # Botão Superior: ASSISTIR VÍDEO
    video_rect = pygame.Rect(button_x, HEIGHT // 2, button_width, button_height)
    color1 = HOVER_GREEN if video_rect.collidepoint(mouse_pos) else VIBRANT_GREEN
    pygame.draw.rect(screen, color1, video_rect, border_radius=15)
    txt1 = font.render("ASSISTIR VÍDEO", True, WHITE)
    screen.blit(txt1, txt1.get_rect(center=video_rect.center))
    
    # Botão Inferior: PULAR PARA FASE 3
    skip_rect = pygame.Rect(button_x, HEIGHT // 2 + int(100 * SCALE), button_width, button_height)
    color2 = HOVER_GREEN if skip_rect.collidepoint(mouse_pos) else VIBRANT_GREEN
    pygame.draw.rect(screen, color2, skip_rect, border_radius=15)
    txt2 = font.render("PULAR PARA FASE 3", True, WHITE)
    screen.blit(txt2, txt2.get_rect(center=skip_rect.center))
    
    return video_rect, skip_rect

# Função para desenhar menu de vitória da Fase 3
def draw_victory_menu_phase3(title="VITÓRIA TOTAL!"):
    screen.fill(MENU_BACKGROUND_COLOR)
    
    title_font = pygame.font.SysFont("Arial", int(72 * SCALE), bold=True)
    title_text = title_font.render(title, True, (255, 215, 0))
    title_rect = title_text.get_rect(center=(WIDTH // 2, HEIGHT // 3 - 50))
    screen.blit(title_text, title_rect)
    
    subtitle_font = pygame.font.SysFont("Arial", int(48 * SCALE))
    subtitle_text = subtitle_font.render("LENDA DO XADREZ!", True, (255, 100, 100))
    subtitle_rect = subtitle_text.get_rect(center=(WIDTH // 2, HEIGHT // 3))
    screen.blit(subtitle_text, subtitle_rect)
    
    button_width = int(320 * SCALE)
    button_height = int(70 * SCALE)
    button_x = (WIDTH - button_width) // 2
    button_y = HEIGHT // 2
    
    menu_button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
    mouse_pos = pygame.mouse.get_pos()
    color = BUTTON_HOVER_COLOR if menu_button_rect.collidepoint(mouse_pos) else BUTTON_COLOR
    pygame.draw.rect(screen, color, menu_button_rect, border_radius=15)
    
    btn_font = pygame.font.SysFont("Arial", int(36 * SCALE))
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
        
        title_font = pygame.font.SysFont("Arial", int(48 * SCALE), bold=True)
        title_text = title_font.render(lines[0] + ("!" if len(lines) > 1 else ""), True, (255, 215, 0)) 
        title_rect = title_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - int(40 * SCALE)))
        screen.blit(title_text, title_rect)
        
        if len(lines) > 1:
            message_font = pygame.font.SysFont("Arial", int(36 * SCALE))
            message_text = message_font.render(lines[1], True, (200, 0, 0)) 
            message_rect = message_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + int(30 * SCALE)))
            screen.blit(message_text, message_rect)
        
        # Exibe a descrição do último movimento durante a transição
        move_font = pygame.font.SysFont("Arial", int(28 * SCALE))
        move_text = move_font.render(last_move_desc, True, WHITE)
        move_rect = move_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + int(80 * SCALE)))
        screen.blit(move_text, move_rect)

# Nova função para desenhar mensagens temporárias (erros, etc.)
def draw_temporary_message(message):
    if message:
        # Fundo semi-transparente para a mensagem temporária
        overlay_surface = pygame.Surface((WIDTH, int(100 * SCALE)), pygame.SRCALPHA) # Altura fixa para a mensagem
        overlay_surface.fill((0, 0, 0, 180)) # Preto semi-transparente
        
        # Posição centralizada no topo da tela
        overlay_rect = overlay_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2 - int(150 * SCALE)))
        screen.blit(overlay_surface, overlay_rect)
        
        # Fonte menor para mensagens de erro
        message_font = pygame.font.SysFont("Arial", int(24 * SCALE)) 
        message_text = message_font.render(message, True, (255, 255, 0)) # Amarelo para destaque
        message_text_rect = message_text.get_rect(center=overlay_rect.center)
        screen.blit(message_text, message_text_rect)

# Modificado para desenhar seta e quadrado no canto inferior direito
def draw_turn_indicator():
    # Define a cor do quadrado e da seta com base no turno
    indicator_square_color = WHITE if current_turn == "branca" else BLACK
    
    # Ocupa o espaço total da margem até o tabuleiro
    square_size = MARGIN 
    
    # Posiciona no canto inferior direito
    square_x = WIDTH - square_size
    square_y = HEIGHT - square_size

    # Desenha o quadrado
    pygame.draw.rect(screen, indicator_square_color, (square_x, square_y, square_size, square_size))
    
    # Desenha a seta apontando para cima dentro do quadrado
    arrow_center_x = square_x + square_size // 2
    arrow_center_y = square_y + square_size // 2
    
    arrow_height = int(15 * SCALE) 
    arrow_width = int(15 * SCALE)  
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
def draw_start_menu(screen, title_text, button_text, show_quit_button=False, bg_image=None):
    """Desenha uma tela de menu genérica com título e botão."""
    mouse_pos = pygame.mouse.get_pos()
    
    if bg_image:
        # Preenche o fundo de preto e desenha a imagem levemente reduzida e centralizada
        screen.fill(BLACK)
        screen.blit(bg_image, (0, 0)) 
        
        # Dimensões precisas para cobrir as placas de madeira
        button_width = int(450 * SCALE) 
        button_height = int(41 * SCALE)
        
        button_x = int(340 * SCALE) - (button_width // 2)
        # Coordenadas ajustadas: Iniciar sobe 6mm (-23px), Sair desce 12mm (+45px)
        # Centros originais: 211 e 361 -> Novos centros: 188 e 406
        start_y = int(237 * SCALE) - (button_height // 2)
        quit_y = int(390 * SCALE) - (button_height // 2)
    else:
        screen.fill(MENU_BACKGROUND_COLOR) 
        title_font = pygame.font.SysFont("Arial", int(56 * SCALE), bold=True)
        title_surf = title_font.render(title_text, True, WHITE)
        title_rect = title_surf.get_rect(center=(WIDTH // 2, HEIGHT // 3))
        screen.blit(title_surf, title_rect)
        button_width = int(330 * SCALE)
        button_height = int(30 * SCALE)
        button_x = (WIDTH - button_width) // 2
        start_y = HEIGHT // 2 + 60
        quit_y = start_y + button_height + 20

    start_button_rect = pygame.Rect(button_x, start_y, button_width, button_height)
    quit_button_rect = pygame.Rect(button_x, quit_y, button_width, button_height) if show_quit_button else None

    # Desenha efeito de destaque (hover) transparente se o mouse estiver sobre o botão
    if start_button_rect.collidepoint(mouse_pos):
        s = pygame.Surface((button_width, button_height), pygame.SRCALPHA)
        s.fill((255, 255, 255, 60)) # Brilho branco suave
        screen.blit(s, (button_x, start_y))
        # Desenha a borda delimitada
        pygame.draw.rect(screen, (255, 255, 255), start_button_rect, 1)

    if quit_button_rect and quit_button_rect.collidepoint(mouse_pos) and show_quit_button:
        s = pygame.Surface((button_width, button_height), pygame.SRCALPHA)
        s.fill((255, 255, 255, 40)) # Brilho suave para o realce
        screen.blit(s, (button_x, quit_y))
        pygame.draw.rect(screen, (255, 100, 100), quit_button_rect, 1)

    # Desenha os rótulos de texto. Se houver imagem, desenha por cima para garantir a nova ordem.
    button_font = pygame.font.SysFont("Arial", int(30 * SCALE), bold=True)
    if bg_image:
        # Texto omitido para ficar "transparente", usando apenas a escrita da imagem
        pass
    else:
        btn_surf = button_font.render(button_text, True, WHITE)
        screen.blit(btn_surf, btn_surf.get_rect(center=start_button_rect.center))
        if show_quit_button:
            quit_surf = button_font.render("SAIR DO JOGO", True, WHITE)
            screen.blit(quit_surf, quit_surf.get_rect(center=quit_button_rect.center))

    return start_button_rect, quit_button_rect

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
quit_button_rect = None
phase2_button_rect = None
phase3_button_rect = None
menu_button_rect_p3 = None
video_button_rect, skip_button_rect = None, None
video_button_rect_p2, skip_button_rect_p2 = None, None

while running:
    clock.tick(30) # Garante que o jogo e o vídeo rodem a 30 frames por segundo
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = event.pos

            if game_state == STATE_MENU:
                if start_button_rect and start_button_rect.collidepoint(mouse_x, mouse_y):
                    start_phase(1)
                elif quit_button_rect and quit_button_rect.collidepoint(mouse_x, mouse_y):
                    running = False
            
            elif game_state == STATE_PHASE2_START:
                if phase2_button_rect and phase2_button_rect.collidepoint(mouse_x, mouse_y):
                    start_phase(2)
            elif game_state == STATE_PHASE3_START:
                if phase3_button_rect and phase3_button_rect.collidepoint(mouse_x, mouse_y):
                    start_phase(3)
            elif game_state == STATE_VICTORY_MENU_PHASE2:
                if video_button_rect_p2 and video_button_rect_p2.collidepoint(mouse_x, mouse_y):
                    play_video("cucacaldeirao.MP4")
                    start_phase(3)
                    game_state = STATE_PHASE3_START
                elif skip_button_rect_p2 and skip_button_rect_p2.collidepoint(mouse_x, mouse_y):
                    start_phase(3)
            
            elif game_state in [STATE_VICTORY_MENU_PHASE3, STATE_CAMPAIGN_FINISHED]:
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
        start_button_rect, quit_button_rect = draw_start_menu(screen, "", "INICIAR JOGADA", True, MENU_BG_IMAGE)
    
    elif game_state == STATE_PHASE2_START:
        phase2_button_rect, _ = draw_start_menu(screen, "FASE 1 CONCLUÍDA!", "START GAME FASE 2", False, None)
    
    elif game_state == STATE_PHASE3_START:
        phase3_button_rect, _ = draw_start_menu(screen, "FASE 2 CONCLUÍDA!", "START GAME FASE 3", False, None)

    elif game_state == STATE_VICTORY_MENU:
        video_button_rect, skip_button_rect = draw_victory_menu()
    
    elif game_state == STATE_VICTORY_MENU_PHASE2:
        video_button_rect_p2, skip_button_rect_p2 = draw_victory_menu_phase2()
    
    elif game_state == STATE_VICTORY_MENU_PHASE3:
        menu_button_rect_p3 = draw_victory_menu_phase3()

    elif game_state == STATE_CAMPAIGN_FINISHED:
        menu_button_rect_p3 = draw_victory_menu_phase3("CAMPANHA FINALIZADA!")
    
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
                # Tenta iniciar o vídeo interno
                video_name = "YARA.MP4"
                found_video_path = ""
                # Lista de caminhos possíveis (mesma lógica robusta do play_video)
                possible_video_paths = [
                    os.path.join(ASSETS_DIR, video_name),
                    os.path.join(os.getcwd(), "assets", video_name),
                    os.path.join(os.getcwd(), video_name),
                    video_name
                ]
                for p in possible_video_paths:
                    if os.path.exists(p):
                        found_video_path = p
                        break
                
                if OPENCV_AVAILABLE and found_video_path:
                    video_cap = cv2.VideoCapture(found_video_path)
                    if video_cap.isOpened():
                        game_state = STATE_VIDEO
                    else:
                        play_video(video_name)
                        start_phase(2)
                else:
                    # Fallback caso não tenha OpenCV ou vídeo não encontrado
                    play_video() 
                    start_phase(2) 
            elif game_state == STATE_TRANSITION_PHASE2_VICTORY:
                # Tenta iniciar o vídeo interno da fase 2 automaticamente
                video_name = "cucacaldeirao.MP4"
                found_video_path = ""
                possible_video_paths = [
                    os.path.join(ASSETS_DIR, video_name),
                    os.path.join(os.getcwd(), "assets", video_name),
                    os.path.join(os.getcwd(), video_name),
                    video_name
                ]
                for p in possible_video_paths:
                    if os.path.exists(p):
                        found_video_path = p
                        break
                
                if OPENCV_AVAILABLE and found_video_path:
                    video_cap = cv2.VideoCapture(found_video_path)
                    if video_cap.isOpened():
                        game_state = STATE_VIDEO
                    else:
                        play_video(video_name)
                        start_phase(3)
                else:
                    play_video(video_name) 
                    start_phase(3)
            elif game_state == STATE_TRANSITION_PHASE3_VICTORY:
                # Tenta iniciar o vídeo final automaticamente
                video_name = "cuca.mp4"
                found_video_path = ""
                possible_video_paths = [
                    os.path.join(ASSETS_DIR, video_name),
                    os.path.join(os.getcwd(), "assets", video_name),
                    os.path.join(os.getcwd(), video_name),
                    video_name
                ]
                for p in possible_video_paths:
                    if os.path.exists(p):
                        found_video_path = p
                        break
                
                if OPENCV_AVAILABLE and found_video_path:
                    video_cap = cv2.VideoCapture(found_video_path)
                    if video_cap.isOpened():
                        game_state = STATE_VIDEO
                    else:
                        play_video(video_name)
                        game_state = STATE_CAMPAIGN_FINISHED
                else:
                    play_video(video_name) 
                    game_state = STATE_CAMPAIGN_FINISHED
            
            # Reseta as variáveis de transição
            transition_start_time = 0
            transition_message = ""
            last_move_description = "" # Limpa a descrição do último movimento

    elif game_state == STATE_VIDEO:
        if video_cap and video_cap.isOpened():
            ret, frame = video_cap.read()
            if ret:
                # Redimensiona o frame para o tamanho da tela do jogo
                frame = cv2.resize(frame, (WIDTH, HEIGHT))
                # Converte de BGR (OpenCV) para RGB (Pygame)
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                # Cria a superfície do Pygame a partir do frame
                video_surf = pygame.image.frombuffer(frame.tobytes(), (WIDTH, HEIGHT), 'RGB')
                screen.blit(video_surf, (0, 0))
            else:
                # Vídeo terminou
                video_cap.release()
                video_cap = None
                if current_phase == 3:
                    game_state = STATE_CAMPAIGN_FINISHED
                else:
                    start_phase(current_phase + 1)
        else:
            if current_phase == 3:
                game_state = STATE_CAMPAIGN_FINISHED
            else:
                start_phase(current_phase + 1)

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
            move_desc_font = pygame.font.SysFont("Arial", int(18 * SCALE), bold=True)
            move_desc_text = move_desc_font.render(last_successful_move_text, True, (200, 0, 0)) # Vermelho para erro
            
            if error_piece_pos:
                r, c = error_piece_pos
                draw_row = 7 - r if board_inverted_display else r
                x = c * CELL_SIZE + MARGIN + CELL_SIZE // 2
                y = draw_row * CELL_SIZE + MARGIN - int(15 * SCALE) # Posiciona acima da peça
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