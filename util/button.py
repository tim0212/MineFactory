import pygame
from util.screen import screen

class Button:
  def __init__(self, rect, color=(80, 120, 255), hover_color=(100, 150, 255), text=None, text_color=(255, 255, 255), bsign=None):
    self.rect = pygame.Rect(rect)
    self.color = color
    self.hover_color = hover_color
    self.text = text
    self.text_color = text_color
    self.bsign = bsign
    self._pressed = False

  def draw(self):
    mouse_pos = pygame.mouse.get_pos()
    is_hover = self.rect.collidepoint(mouse_pos)
    pygame.draw.rect(screen.surface, self.hover_color if is_hover else self.color, self.rect, border_radius=8)
    pygame.draw.rect(screen.surface, (30, 30, 50), self.rect, width=2, border_radius=8)

    if self.text:
      font = pygame.font.SysFont(None, 24)
      surf = font.render(self.text, True, self.text_color)
      r = surf.get_rect(center=self.rect.center)
      screen.surface.blit(surf, r)

  def handle_events(self, events):
    result = None
    mouse_pos = pygame.mouse.get_pos()
    is_hover = self.rect.collidepoint(mouse_pos)

    for e in events:
      if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
        if is_hover:
          self._pressed = True
      elif e.type == pygame.MOUSEBUTTONUP and e.button == 1:
        if self._pressed and is_hover:
          result = self.bsign
        self._pressed = False
    return result
