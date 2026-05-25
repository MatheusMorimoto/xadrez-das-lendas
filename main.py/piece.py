import pygame
import os

class Piece:
    def __init__(self, image_path_relative, row, col, tipo, cor, cell_size, assets_dir):
        # Extrai apenas o nome do arquivo e busca dentro de assets_dir
        file_name = os.path.basename(image_path_relative)
        full_image_path = os.path.join(assets_dir, file_name)
        
        try:
            # Para set_colorkey funcionar da forma mais robusta em fundos sólidos:
            # Carregamos com convert_alpha para suportar imagens que já têm transparência,
            # mas aplicamos o colorkey preto para as que têm fundo sólido.
            loaded_image = pygame.image.load(full_image_path).convert_alpha()
            loaded_image.set_colorkey((0, 0, 0)) # Define o preto absoluto como transparente
            self.image = pygame.transform.scale(loaded_image, (cell_size, cell_size))
        except (pygame.error, FileNotFoundError):
            # Fallback para peça magenta se a imagem falhar
            self.image = pygame.Surface((cell_size, cell_size))
            self.image.fill((255, 0, 255))
            
        self.row = row
        self.col = col
        self.tipo = tipo
        self.cor = cor
        self.image_path = image_path_relative
        self.cell_size = cell_size
        self.assets_dir = assets_dir

    def draw(self, screen, offset_x, offset_y, board_inverted_display=False):
        draw_row = self.row
        if board_inverted_display:
            draw_row = 7 - self.row
            
        x = self.col * self.cell_size + offset_x
        y = draw_row * self.cell_size + offset_y
        screen.blit(self.image, (x, y))

    def get_moves(self, board_pieces):
        moves = []
        
        def get_piece_at(r, c):
            return next((p for p in board_pieces if p.row == r and p.col == c), None)

        def check_linear_moves(directions):
            possible_moves = []
            for dx, dy in directions:
                for i in range(1, 8):
                    r, c = self.row + dy * i, self.col + dx * i
                    if 0 <= r < 8 and 0 <= c < 8:
                        target = get_piece_at(r, c)
                        if target:
                            if target.cor != self.cor: possible_moves.append((r, c))
                            break
                        possible_moves.append((r, c))
                    else: break
            return possible_moves

        if self.tipo == "rainha":
            moves.extend(check_linear_moves([(1,0),(-1,0),(0,1),(0,-1),(1,1),(-1,-1),(1,-1),(-1,1)]))
        elif self.tipo == "rei":
            for dx, dy in [(1,0),(-1,0),(0,1),(0,-1),(1,1),(-1,-1),(1,-1),(-1,1)]:
                r, c = self.row + dy, self.col + dx
                if 0 <= r < 8 and 0 <= c < 8:
                    target = get_piece_at(r, c)
                    if not target or target.cor != self.cor: moves.append((r, c))
        elif self.tipo == "cavalo":
            for dx, dy in [(2,1),(1,2),(-1,2),(-2,1),(-2,-1),(-1,-2),(1,-2),(2,-1)]:
                r, c = self.row + dy, self.col + dx
                if 0 <= r < 8 and 0 <= c < 8:
                    target = get_piece_at(r, c)
                    if not target or target.cor != self.cor: moves.append((r, c))
        elif self.tipo == "peao":
            direction = -1 if self.cor == "branca" else 1
            start_row = 6 if self.cor == "branca" else 1
            if 0 <= self.row + direction < 8 and not get_piece_at(self.row + direction, self.col):
                moves.append((self.row + direction, self.col))
                if self.row == start_row and not get_piece_at(self.row + 2 * direction, self.col):
                    moves.append((self.row + 2 * direction, self.col))
            for dc in [-1, 1]:
                r_cap, c_cap = self.row + direction, self.col + dc
                if 0 <= r_cap < 8 and 0 <= c_cap < 8:
                    target = get_piece_at(r_cap, c_cap)
                    if target and target.cor != self.cor: moves.append((r_cap, c_cap))
        elif self.tipo == "torre":
            moves.extend(check_linear_moves([(1,0),(-1,0),(0,1),(0,-1)]))
        elif self.tipo == "bispo":
            moves.extend(check_linear_moves([(1,1),(-1,-1),(1,-1),(-1,1)]))
        return moves

    def copy(self):
        new_piece = Piece(self.image_path, self.row, self.col, self.tipo, self.cor, self.cell_size, self.assets_dir)
        new_piece.image = self.image
        return new_piece
