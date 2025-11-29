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

    def draw(self, screen, offset_x, offset_y):
        x = self.col * 80 + offset_x
        y = self.row * 80 + offset_y
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

# --- VARIÁVEIS DE ESTADO E INICIALIZAÇÃO DE PEÇAS ---

# Lista inicial de peças (Fase 1 - Exemplo de Xeque-mate: Beijo da Morte)
def create_initial_pieces_phase1():
    return [
        Piece("assets/rainha_branca.png", 1, 4, "rainha", "branca"), # Posição e7
        Piece("assets/rei_branco.png", 2, 3, "rei", "branca"),       # Posição d6
        Piece("assets/cavalo_branco.png", 3, 6, "cavalo", "branca"), # Posição g5
        Piece("assets/rei_preto.png", 0, 7, "rei", "preta"),         # Posição h8
    ]

# Jogo completo de xadrez - Fase 3
def create_initial_pieces_full_game():
    return [
        # Peças brancas (linha 7 = row 7, linha 6 = row 6)
        Piece("assets/torre_branca.png", 7, 0, "torre", "branca"),
        Piece("assets/cavalo_branco.png", 7, 1, "cavalo", "branca"),
        Piece("assets/bispo_branco 1 .png", 7, 2, "bispo", "branca"),
        Piece("assets/rainha_branca.png", 7, 3, "rainha", "branca"),
        Piece("assets/rei_branco.png", 7, 4, "rei", "branca"),
        Piece("assets/bispo_branco_2.png", 7, 5, "bispo", "branca"),
        Piece("assets/cavalo_branco_2.png", 7, 6, "cavalo", "branca"),
        Piece("assets/torre_branca_2.png", 7, 7, "torre", "branca"),
        # Peões brancos
        Piece("assets/peao_branco 1.png", 6, 0, "peao", "branca"),
        Piece("assets/peao_branco 2.png", 6, 1, "peao", "branca"),
        Piece("assets/peao_branco 3.png", 6, 2, "peao", "branca"),
        Piece("assets/peao_branco 4.png", 6, 3, "peao", "branca"),
        Piece("assets/peao_branco 5.png", 6, 4, "peao", "branca"),
        Piece("assets/peao_branco 6.png", 6, 5, "peao", "branca"),
        Piece("assets/peao_branco 7.png", 6, 6, "peao", "branca"),
        Piece("assets/peao_branco 8.png", 6, 7, "peao", "branca"),
        
        # Peças pretas (linha 0 = row 0, linha 1 = row 1)
        Piece("assets/torre_preta.png", 0, 0, "torre", "preta"),
        Piece("assets/cavalo_preto .png", 0, 1, "cavalo", "preta"),
        Piece("assets/bispo_preta.png", 0, 2, "bispo", "preta"),
        Piece("assets/rainha_preta.png", 0, 3, "rainha", "preta"),
        Piece("assets/rei_preto.png", 0, 4, "rei", "preta"),
        Piece("assets/bispo_preta_2.png", 0, 5, "bispo", "preta"),
        Piece("assets/cavalo_preto_2.png", 0, 6, "cavalo", "preta"),
        Piece("assets/torre_preta_2.png", 0, 7, "torre", "preta"),
        # Peões pretos
        Piece("assets/peão_preto 1.png", 1, 0, "peao", "preta"),
        Piece("assets/peão_preto 2.png", 1, 1, "peao", "preta"),
        Piece("assets/peão_preto 3.png", 1, 2, "peao", "preta"),
        Piece("assets/peão_preto 4.png", 1, 3, "peao", "preta"),
        Piece("assets/peão_preto 5.png", 1, 4, "peao", "preta"),
        Piece("assets/peão_preto 6.png", 1, 5, "peao", "preta"),
        Piece("assets/peão_preto 7 .png", 1, 6, "peao", "preta"),
        Piece("assets/peão_preto 8.png", 1, 7, "peao", "preta")
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
def start_phase(phase):
    global pieces, selected_piece, valid_moves, checkmate_message, game_state
    
    if phase == 1:
        pieces = create_initial_pieces_phase1()
        game_state = STATE_GAME # Inicia a Fase 1 (usando o estado original)
    elif phase == 2:
        pieces = create_initial_pieces_phase2()
        game_state = STATE_GAME_PHASE2 # Inicia a Fase 2
    elif phase == 3:
        pieces = create_initial_pieces_full_game()
        game_state = "playing_full_game" # Jogo completo
    
    selected_piece = None
    valid_moves = []
    checkmate_message = None

pieces = create_initial_pieces_phase1() # Inicia com a Fase 1
selected_piece = None
valid_moves = []
checkmate_message = None


# Estados do Jogo (ADICIONADO NOVO ESTADO E ALTERADO O NOME DO JOGO)
STATE_MENU = "menu"
STATE_GAME = "playing_phase1"
STATE_VICTORY_MENU = "victory_menu" # NOVO ESTADO para menu de vitória com botão de vídeo
STATE_VIDEO = "playing_video" # NOVO ESTADO para reproduzir vídeo
STATE_PHASE2_START = "phase2_menu" # NOVO ESTADO para o menu da Fase 2
STATE_GAME_PHASE2 = "playing_phase2" # NOVO ESTADO para o jogo da Fase 2
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

# Função para reproduzir vídeo
def play_video():
    import subprocess
    import os
    
    # Tentar vários caminhos possíveis para YARA.MP4
    possible_paths = [
        os.path.join(os.getcwd(), "assets", "YARA.MP4"),
        os.path.join("assets", "YARA.MP4"),
        "assets/YARA.MP4",
        "YARA.MP4"
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
def draw_checkmate_message(message, phase_number=1):
    global game_state, video_start_time # Adicionada para mudar o estado após a Fase 1
    
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
            
        # Adicionar o botão para ir para o menu de vitória APENAS SE A MENSAGEM FOR DA FASE 1
        if phase_number == 1 and game_state == STATE_GAME:
            game_state = STATE_VICTORY_MENU # Muda para o menu de vitória

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
            
            elif game_state in [STATE_GAME, STATE_GAME_PHASE2] and not checkmate_message:
                col = (mouse_x - MARGIN) // CELL_SIZE
                row = (mouse_y - MARGIN) // CELL_SIZE
                
                if 0 <= row < 8 and 0 <= col < 8:
                    if selected_piece:
                        if (row, col) in valid_moves:
                            captured_piece = next((p for p in pieces if p.row == row and p.col == col and p.cor != selected_piece.cor), None)
                            
                            if captured_piece:
                                pieces.remove(captured_piece)
                            
                            selected_piece.row = row
                            selected_piece.col = col
                            
                            enemy_king_color = "preta" if selected_piece.cor == "branca" else "branca"
                            enemy_king = next((p for p in pieces if p.tipo == "rei" and p.cor == enemy_king_color), None)
                            
                            if enemy_king and is_checkmate(enemy_king, pieces):
                                if game_state == STATE_GAME:
                                    checkmate_message = "Primeira Fase: Beijo da Morte! Vitória! Prepare-se para a Fase 2."
                                else:
                                    checkmate_message = "Segunda Fase: Vitória! Fim de jogo."
                            
                            selected_piece = None
                            valid_moves = []
                        else:
                            selected_piece = None
                            valid_moves = []
                    else:
                        for piece in pieces:
                            if piece.row == row and piece.col == col:
                                # Permitir seleção de peças brancas E pretas
                                selected_piece = piece
                                all_moves = get_valid_moves(piece, pieces)
                                king = next((p for p in pieces if p.tipo == "rei" and p.cor == piece.cor), None)
                                valid_moves = [
                                    move for move in all_moves
                                    if king and not would_king_be_in_check(king, pieces, piece, move[0], move[1])
                                ]
                                break
    
    # Desenho
    if game_state == STATE_MENU:
        start_button_rect = draw_start_menu(screen, "XADREZ PROJETO", "INICIAR JOGO FASE 1")
    
    elif game_state == STATE_PHASE2_START:
        phase2_button_rect = draw_start_menu(screen, "FASE 1 CONCLUÍDA!", "INICIAR JOGO FASE 2")
    
    elif game_state == STATE_VICTORY_MENU:
        video_button_rect, skip_button_rect = draw_victory_menu()
        
        # Verificar cliques nos botões
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = event.pos
                
                if video_button_rect.collidepoint(mouse_x, mouse_y):
                    print("Botão de vídeo clicado!")
                    play_video()
                    game_state = STATE_PHASE2_START
                elif skip_button_rect.collidepoint(mouse_x, mouse_y):
                    game_state = STATE_PHASE2_START
    
    elif game_state in [STATE_GAME, STATE_GAME_PHASE2]:
        screen.fill(GAME_BACKGROUND_COLOR)
        
        draw_board()
        draw_coordinates()
        draw_valid_moves(valid_moves)
        
        for piece in pieces:
            piece.draw(screen, MARGIN, MARGIN)
        
        draw_checkmate_message(checkmate_message, 1 if game_state == STATE_GAME else 2)
    
    pygame.display.flip()

pygame.quit()