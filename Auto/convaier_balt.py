import pygame
from itemstorge.itemsprites import item

class convaier(pygame.sprite.Sprite):
  def __init__(self, group, direction):
    super().__init__(group)