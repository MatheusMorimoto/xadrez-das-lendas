import pygame
pygame.init()

import pygame

import pygame

class Piece:
    def __init__(self, image_path, row, col):
        self.image = pygame.image.load(image_path)
        self.row = row
        self.col = col

    def draw(self, screen):
        x = self.col * 80
        y = self.row * 80
        screen.blit(self.image, (x, y))
