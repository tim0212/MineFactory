import pygame
from camera import Camera
from util.__init__ import Loader, screen, text as texts
from util.map_loader import TMXMap
from itemstorge.itemsprites import ITEM_DICT

MAX_STACK = 64
ROWS, COLS = 10, 5
DEBUG_MINING = True  # False로 바꾸면 로그 끔

SLOT_W, SLOT_H = 32, 32
SLOT_GAP = 7
ROWS, COLS = 5, 10

INV_MARGIN_BOTTOM = 12
INV_ORIGIN_X = screen.surface.get_width() // 2 - ((COLS * SLOT_W + (COLS - 1) * SLOT_GAP) // 2 + 6)
INV_ORIGIN_Y = screen.surface.get_height() - INV_MARGIN_BOTTOM - SLOT_H + 8

SLOT_DICT = {}
for r in range(ROWS):
  for c in range(COLS):
    x = INV_ORIGIN_X + c * (SLOT_W + SLOT_GAP)
    y = INV_ORIGIN_Y - r * (SLOT_H + SLOT_GAP)  # 아래에서 위로 쌓이게 10x5인벤
    SLOT_DICT[(r, c)] = (x, y)

on = True
save = 0
swich = True

x = screen.surface.get_width() - 10
class Inventory:
  instance = False

  def __init__(self):
    self.slots = [["" for _ in range(COLS)] for _ in range(ROWS)]
    self.font = pygame.font.SysFont(None, 18)
    self.slots[0][0] = {"id": "pickaxe", "qty": 1}
    self.selected_hotbar = 0
    self.slot_positions = {}
    self.hotbar_only = True

  @classmethod
  def init(cls):
    cls.instance = cls()

  @classmethod
  def get(cls):
    if cls.instance is None:
      return cls.init()
    return cls.instance

  def add_stack(self, item_id, qty=1):
      remain = qty
      # 기존 스택 채우기
      for r in range(ROWS):
          for c in range(COLS):
              cell = self.slots[r][c]
              pos = (r, c)
              if isinstance(cell, dict) and cell["id"] == item_id and cell["qty"] < MAX_STACK:
                  can = min(MAX_STACK - cell["qty"], remain)
                  cell["qty"] += can
                  remain -= can
                  if remain == 0:
                      return qty, pos
      for r in range(ROWS):
          for c in range(COLS):
              if self.slots[r][c] in (None, ""):
                  put = min(MAX_STACK, remain)
                  self.slots[r][c] = {"id": item_id, "qty": put}
                  remain -= put
                  if remain == 0:
                      return qty
      return qty - remain

  # 외부에서 상태 토글
  def set_open(self, open_: bool):
    self.hotbar_only = not open_

  # 한번 더 눌으면 칸 지우기
  def select_hotbar(self, idx: int):
    global on, save, swich
    if save == idx:
      on = not on
    if save != idx: on = True

    save = idx

    if on:
      print("on")
      self.selected_hotbar = max(0, min(9, idx))
    else:
      self.selected_hotbar = None
      print("None")

  def current_item_id(self):
    global cell
    cell = None

    if self.selected_hotbar is not None:
        cell = self.slots[0][self.selected_hotbar]
        if isinstance(cell, dict):
            return cell["id"]
    return ""

  def item_info_show(self):
    mx, my = pygame.mouse.get_pos()
    for (r, c), (sx, sy) in self.slot_positions.items():
        slot_rect = pygame.Rect(sx, sy, SLOT_W, SLOT_H)
        if slot_rect.collidepoint(mx, my):
            cell = self.slots[r][c]
            if isinstance(cell, dict):
                item_name = cell["id"]
                name_x = sx + SLOT_W // 2
                name_y = sy - 20  # 슬롯 위 20px
                texts.render(
                    (name_x, name_y),
                    item_name,
                    True,
                    (0, 0, 0),
                    centerpos="center",
                    size=20
                )
            break

  def draw_hotbar(self, surface):
    font = pygame.font.SysFont(None, 16)
    for c in range(COLS):
      cell = self.slots[0][c]
      pos = (0, c)
      if pos not in self.slot_positions: continue
      x, y = self.slot_positions[pos]

      if c == self.selected_hotbar:
        pygame.draw.rect(surface, (255, 255, 255), pygame.Rect(x-2, y-2, 36, 36), 2)

      if isinstance(cell, dict):
        global item_id
        item_id, qty = cell["id"], cell["qty"]
        if item_id in ITEM_DICT:
          img = ITEM_DICT[item_id]
          surface.blit(img, (x, y))
          stxt = font.render(str(qty), True, (255, 255, 255))
          surface.blit(stxt, stxt.get_rect(bottomright=(x + img.get_width() - 2, y + img.get_height() - 2)))

  def draw_all(self, surface):
    font = pygame.font.SysFont(None, 16)
    for r in range(ROWS):
      for c in range(COLS):
        cell = self.slots[r][c]
        pos = (r, c)
        if pos not in self.slot_positions: continue
        x, y = self.slot_positions[pos]

        if r == 0 and c == self.selected_hotbar:
          pygame.draw.rect(surface, (255, 255, 255), pygame.Rect(x-2, y-2, 36, 36), 2)

        if isinstance(cell, dict):
          item_id, qty = cell["id"], cell["qty"]
          if item_id in ITEM_DICT:
            img = ITEM_DICT[item_id]
            surface.blit(img, (x, y))
            stxt = font.render(str(qty), True, (255, 255, 255))
            surface.blit(stxt, stxt.get_rect(bottomright=(x + img.get_width() - 2, y + img.get_height() - 2)))

  def draw(self, surface):
    if self.hotbar_only:
      self.draw_hotbar(surface)
    else:
      self.draw_all(surface)


  def inven_input(item_id, qty, pos):
    r, c = pos
    cell = Inventory.instance.slots[r][c]
    if cell in ("", None):
      Inventory.instance.slots[r][c] = {"id": item_id, "qty": qty}
    elif isinstance(cell, dict) and cell["id"] == item_id:
      cell["qty"] = min(cell["qty"] + qty, MAX_STACK)
    else:
      Inventory.instance.slots[r][c] = {"id": item_id, "qty": qty}

    if item_id in ITEM_DICT:
      img = ITEM_DICT[item_id]
      x, y = SLOT_DICT[(r, c)]
      screen.surface.blit(img, (x, y))
      font = pygame.font.SysFont(None, 16)
      stxt = font.render(str(Inventory.instance.slots[r][c]["qty"]), True, (255, 255, 255))
      screen.surface.blit(stxt, stxt.get_rect(bottomright=(x + img.get_width() - 2, y + img.get_height() - 2)))

  def set_slot_positions(self, slot_dict):
    self.slot_positions = dict(slot_dict) if slot_dict else {}

  def draw_item_tooltip(self):
    mx, my = pygame.mouse.get_pos()
    for (r, c), (sx, sy) in self.slot_positions.items():
      if self.hotbar_only and r != 0:
        continue
      slot_rect = pygame.Rect(sx, sy, SLOT_W, SLOT_H)
      if not slot_rect.collidepoint(mx, my):
        continue

      cell = self.slots[r][c]
      if not isinstance(cell, dict):
        continue
      name = cell["id"]

      # 텍스트 크기
      name_rect = texts.render((0, 0), name, True, (255, 255, 255), return_rect_only=True, size=18)

      pad_x, pad_y = 8, 6
      box_w = max(64, name_rect.width + pad_x * 2)
      box_h = name_rect.height + pad_y * 2

      bx = sx + SLOT_W // 2 - box_w // 2
      by = sy - box_h - 6

      sw, sh = screen.surface.get_size()
      bx = max(6, min(bx, sw - box_w - 6))
      by = max(6, by)

      panel = pygame.Surface((box_w, box_h), pygame.SRCALPHA)
      panel.fill((0, 0, 0, 170))
      screen.surface.blit(panel, (bx, by))

      pygame.draw.rect(screen.surface, (255, 255, 255), pygame.Rect(bx, by, box_w, box_h), 1)

      text_x = bx + box_w // 2
      text_y = by + box_h // 2
      texts.render((text_x, text_y), name, True, (255, 255, 255), size=18)
      break



speed = 5
class Player(pygame.sprite.Sprite):
  instance = None

  def __init__(self):
    super().__init__()
    self.gold = 0
    self.image = Loader.load_image("image/player.png", scale=(32, 32))
    self.rect = self.image.get_rect(topleft=(0, 0))
    self.group = pygame.sprite.Group(); self.group.add(self)
    Inventory.init()
    self.inventory = Inventory.get()
    self.mine_cool = 0
    self.cursor_ok = Loader.load_image("image/ui/cursor_pick_ok.png")
    self.cursor_no = Loader.load_image("image/ui/cursor_pick_no.png")

    self.inventory.set_slot_positions(SLOT_DICT)


  @classmethod
  def init(cls):
    if cls.instance is None:
      cls.instance = cls()
    return cls.instance

  @classmethod
  def get(cls):
    if cls.instance is None:
      return cls.init()
    return cls.instance

  def keyevents(self):
    keys = pygame.key.get_pressed()
    dx = dy = 0
    if keys[pygame.K_d]: dx += speed
    if keys[pygame.K_a]: dx -= speed
    if keys[pygame.K_w]: dy -= speed
    if keys[pygame.K_s]: dy += speed
    self.move_with_collision(dx, dy, TMXMap.get().collision)

    if self.mine_cool > 0:
      self.mine_cool -= 1

  def move_with_collision(self, dx, dy, collision_group):
    hitbox = self.rect.inflate(-4, -2)

    hitbox.x += dx
    if any(hitbox.colliderect(obj.rect) for obj in collision_group):
        hitbox.x -= dx
    hitbox.y += dy
    if any(hitbox.colliderect(obj.rect) for obj in collision_group):
        hitbox.y -= dy

    self.rect.center = hitbox.center

  # === 마우스 클릭으로 채광 ===
  def mine_at_mouse(self, screen_pos):
    if self.inventory.current_item_id() != "pickaxe" or self.mine_cool > 0:
      return
    world_pos = Camera.screen_to_world_pos(screen_pos)
    self.try_mine_at(world_pos)
    self.mine_cool = 15

  def try_mine_at(self, world_pos, range_px=50):
    tmx = TMXMap.get()
    ores = tmx.ores
    if not ores:
      if DEBUG_MINING: print("\033[35m[MINE]\033[0m ores empty")
      return

    # 1) 포인터 아래에 있는 ore 우선
    target = None
    for ore in ores:
      if ore.rect.collidepoint(world_pos):
        target = ore
        break

    # 2) 없으면 포인터와 가장 가까운 ore(16px 이내만)
    if target is None:
      best = float("inf")
      for ore in ores:
        ox, oy = ore.rect.center
        dx = world_pos[0] - ox; dy = world_pos[1] - oy
        d2 = dx*dx + dy*dy
        if d2 < best:
          best = d2; target = ore
      if target:
        import math
        if math.sqrt(best) > 16:
          target = None

    if target:
      import math
      px, py = self.rect.center
      dx = target.rect.centerx - px; dy = target.rect.centery - py
      dist = math.sqrt(dx*dx + dy*dy)
      if dist <= range_px:
        destroyed = target.mine(dmg=1)
        if destroyed:
          item_id, qty = target.drop()
          self.inventory.add_stack(item_id, qty)
          target.kill()
          if DEBUG_MINING:
            print(f"\033[32m[MINE]\033[0m destroyed → +{qty} {item_id}")
      else:
        if DEBUG_MINING:
          print("\033[31m[MINE] out of range (50px)\033")
    else:
      if DEBUG_MINING:
        print("\033[33m[MINE]\033[0m no ore at cursor")

  # === 커서 표시 ===
  def draw_cursor(self, surface):
    if self.inventory.current_item_id() != "pickaxe":
      return
    mx, my = pygame.mouse.get_pos()
    can_mine = self.check_can_mine((mx, my))
    img = self.cursor_ok if (can_mine and self.cursor_ok) else self.cursor_no
    if img:
      rect = img.get_rect(center=(mx, my))
      surface.blit(img, rect)
    else:
      if can_mine:
        pygame.draw.circle(surface, (0, 255, 0), (mx, my), 6, 2)
      else:
        pygame.draw.line(surface, (255, 0, 0), (mx-6, my-6), (mx+6, my+6), 2)
        pygame.draw.line(surface, (255, 0, 0), (mx-6, my+6), (mx+6, my-6), 2)

  def check_can_mine(self, screen_pos):
    if self.inventory.current_item_id() != "pickaxe":
      return
    world_pos = Camera.screen_to_world_pos(screen_pos)
    tmx = TMXMap.get()
    for ore in tmx.ores:
      if ore.rect.collidepoint(world_pos):
        import math
        px, py = self.rect.center
        dx = ore.rect.centerx - px; dy = ore.rect.centery - py
        return math.hypot(dx, dy) <= 50
    return False
