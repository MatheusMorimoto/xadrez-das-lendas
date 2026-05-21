import pygame

class Piece:
    def __init__(self, image_path, row, col):
        # Ajuste para carregar a imagem em tamanho padrão; o redimensionamento real ocorre no main.py
        loaded_image = pygame.image.load(image_path)
        self.image = pygame.transform.scale(loaded_image, (80, 80))
        self.row = row
        self.col = col

    def draw(self, screen):
        x = self.col * self.image.get_width()
        y = self.row * self.image.get_height()
        screen.blit(self.image, (x, y))
