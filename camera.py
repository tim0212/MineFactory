import pygame
from pygame.sprite import Group
from util import screen

class Camera:
  instance = None  # 싱글톤처럼 저장

  @classmethod
  def init(cls, target, objects: Group = None):
    if objects is None:
      if hasattr(target, "group"):
        objects = target.group
      else:
        raise ValueError("objects를 명시하거나 target에 group이 있어야 합니다.")
    cls.instance = cls(target, objects)

  def __init__(self, target, objects: Group):
    self.target = target
    self.objects = objects
    self.offset = pygame.math.Vector2(0, 0)
    self.shake_offset = pygame.math.Vector2(0, 0)
    self.shake_power = 0

    w, h = screen.surface.get_size()
    self.screen_center = pygame.math.Vector2(w // 2, h // 2)

    self.zoom_level = 1.0

  def update(self):
    target_center = pygame.math.Vector2(self.target.rect.center)
    self.offset = target_center - self.screen_center

    if self.shake_power > 0:
      import random
      self.shake_offset.x = random.uniform(-self.shake_power, self.shake_power)
      self.shake_offset.y = random.uniform(-self.shake_power, self.shake_power)
      self.shake_power *= 0.9
      if self.shake_power < 0.2:
        self.shake_power = 0
        self.shake_offset = pygame.math.Vector2(0, 0)

  def apply(self, rect: pygame.Rect) -> pygame.Vector2:
    return rect.topleft - self.offset + self.shake_offset

  def draw(self):
    self.update()
    for sprite in self.objects:
      zoomed_size = self.get_zoomed_size(sprite.image)
      if zoomed_size == sprite.image.get_size():
        image = sprite.image
      else:
        image = pygame.transform.scale(sprite.image, zoomed_size)
      screen.surface.blit(image, self.apply(sprite.rect))

  def get_zoomed_size(self, image):
    w, h = image.get_size()
    if self.zoom_level == 1.0:
      return (w, h)
    else:
      return (int(w * self.zoom_level), int(h * self.zoom_level))

  # === 화면->월드 좌표 변환 ===
  def screen_to_world(self, screen_pos):
    return pygame.math.Vector2(screen_pos) + self.offset - self.shake_offset

  @classmethod
  def screen_to_world_pos(cls, screen_pos):
    return cls.instance.screen_to_world(screen_pos)

  @classmethod
  def set_zoom(cls, level: float):
    if cls.instance:
      cls.instance.zoom_level = max(0.1, min(level, 5.0))

  @classmethod
  def set_target(cls, new_target):
    if cls.instance:
      cls.instance.target = new_target

  @classmethod
  def shake(cls, power=10):
    if cls.instance:
      cls.instance.shake_power = power