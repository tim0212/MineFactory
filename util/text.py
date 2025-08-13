import pygame
from util import screen

#===========================================text.py===========================================
class text:
  instance = False

  def __init__(self, font):
    if font == "basic":
      self.font = "malgungothic"
    else:
      self.font = font

  @classmethod
  def init(cls, font = "malgungothic"):
    text.instance = cls(font)

  @classmethod
  def render(cls,
    pos: tuple,
    texts: str,
    antialiased: bool,
    color: tuple,
    display_update: bool = False,
    centerpos: str = "center",
    return_rect_only: bool = False,
    unicode: bool = False,
    size: int = 46):

    font = pygame.font.SysFont(cls.font if unicode else None, size)
    text = font.render(texts, antialiased, color)
    rect = text.get_rect()

    if hasattr(rect, centerpos):
      setattr(rect, centerpos, pos)
    else:
      rect.center = pos

    if display_update:
      screen.fill((20, 20, 50))

    if return_rect_only:
      return rect

    return screen.surface.blit(text, rect)
