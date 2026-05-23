import pygame

class Piece:
    def __init__(self, image_path, row, col, tipo=None, cor=None):
        # Ajuste para carregar a imagem em tamanho padrão; o redimensionamento real ocorre no main.py
        loaded_image = pygame.image.load(image_path).convert_alpha()
        # Define o preto absoluto como transparente para remover bordas indesejadas
        loaded_image.set_colorkey((0, 0, 0)) 
        self.image = pygame.transform.scale(loaded_image, (80, 80))
        self.row = row
        self.col = col
        self.tipo = tipo
        self.cor = cor

    def draw(self, screen, offset_x=0, offset_y=0, board_inverted_display=False):
        draw_row = self.row
        if board_inverted_display:
            draw_row = 7 - self.row
            
        x = self.col * self.image.get_width() + offset_x
        y = draw_row * self.image.get_height() + offset_y
        screen.blit(self.image, (x, y))
