import pygame
from util.__init__ import Loader, screen

class UISprite(pygame.sprite.Sprite):
  def __init__(self, image: pygame.Surface, **rect_place):
    super().__init__()
    self.image = image
    self.rect = self.image.get_rect()
    # rect 위치 지정: topleft=(x,y), bottomleft=(x,y) 같은 키워드로 넘김
    for k, v in rect_place.items():
      setattr(self.rect, k, v)

class Ui:
  instance = None

  def __init__(self):
    w, h = screen.surface.get_size()

    clothes_img = Loader.load_image("image/tools/clothes_inventory.png", scale=None)
    inven_img = Loader.load_image("image/tools/inventory.png", scale=None)

    # 스프라이트로 감싸서 위치 지정
    self.clothes = UISprite(clothes_img, topleft=(0, h / 2 - 150))
    self.inven = UISprite(inven_img, midbottom=(w / 2, h))

    self.group = pygame.sprite.Group()
    self.group.add(self.clothes, self.inven)

  @classmethod
  def init(cls):
    cls.instance = cls()
    return cls.instance

  def draw(self):
    # 화면에 스프라이트 그리기
    self.group.draw(screen.surface)

  def build_slot_dict(self, rows, cols,
                      slot_w=32, slot_h=32, gap=6,
                      inset_x=10, inset_y=10,
                      align_bottom=True):
    rect = self.inven.rect
    if align_bottom:
      origin_y = rect.bottom - inset_y - slot_h  # 아래에서 위로 쌓기 시작
      step_y = -(slot_h + gap)
    else:
      origin_y = rect.top + inset_y              # 위에서 아래로 쌓기 시작
      step_y =  (slot_h + gap)

    origin_x = rect.left + inset_x
    step_x = slot_w + gap

    slot_dict = {}
    for r in range(rows):
      for c in range(cols):
        x = origin_x + c * step_x
        y = origin_y + r * step_y
        slot_dict[(r, c)] = (x, y)
    return slot_dict

  def debug_draw_slots(self, slot_dict, slot_w=32, slot_h=32, color=(255, 0, 255)):
    # 슬롯 위치 확인용 디버그(투명 사각형 테두리)
    for (_r, _c), (x, y) in slot_dict.items():
      pygame.draw.rect(screen.surface, color, pygame.Rect(x, y, slot_w, slot_h), 1)