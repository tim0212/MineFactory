import os
import pygame
pygame.init()
from pygame.sprite import Sprite, Group
from pytmx.util_pygame import load_pygame

ASSETS_PATH = os.path.join(os.path.dirname(__file__), "assets")
MAPS_PATH = os.path.join(ASSETS_PATH, "maps")

class Tile(Sprite):
  def __init__(self, image, pos, group):
    super().__init__(group)
    self.image = image
    self.rect = self.image.get_rect(topleft=pos)

class OreTile(Sprite):
  # HP/드랍 테이블
  HP_TABLE = {"stone": 2, "coal": 5, "row_iron" : 9}
  DROP_TABLE = {
    "stone": ("stone2", 1),
    "coal": ("coal", 1),
    "row_iron": ("row_iron", 1),
    "row_gold": ("gold_ore", 1),
}
  # 여러 그룹에 동시에 등록되도록 *groups 사용
  def __init__(self, image, pos, groups, ore_type="stone"):
    super().__init__(*groups)
    self.image = image
    self.rect = self.image.get_rect(topleft=pos)
    self.ore_type = ore_type
    self.max_hp = self.HP_TABLE.get(ore_type, 5)
    self.hp = self.max_hp
    self.mine_sound = pygame.mixer.Sound("util\\assets\\audio\ore_mine.wav")

  def mine(self, dmg=2):
    self.hp -= dmg
    if self.mine_sound:
        self.mine_sound.play()
    return self.hp <= 0

  def drop(self):
    return self.DROP_TABLE.get(self.ore_type, ("stone", 1))

class TMXMap:
  instance = None

  def __init__(self, filename, tile_size=(32, 32)):
    tmx_path = os.path.join(MAPS_PATH, filename)
    if not os.path.exists(tmx_path):
      raise FileNotFoundError(f"TMX not found: {tmx_path}")

    self.tmx = load_pygame(tmx_path)

    tw = getattr(self.tmx, "tilewidth", tile_size[0])
    th = getattr(self.tmx, "tileheight", tile_size[1])
    self.tile_w, self.tile_h = tile_size if tile_size else (tw, th)

    self.ground = Group()
    self.decor = Group()
    self.collision = Group()
    self.ores = Group()        # 광석 전용
    self.render_all = Group()  # 화면 그리기용(충돌 제외)

    self.spawn_pos = (0, 0)
    self._build()

  @classmethod
  def init(cls, filename, tile_size=(32, 32)):
    cls.instance = cls(filename, tile_size)
    return cls.instance

  @classmethod
  def get(cls):
    if cls.instance is None:
      raise RuntimeError("TMXMap not initialized. Call TMXMap.init(...) first.")
    return cls.instance

  def _build(self):
    # 로드 진단
    total = have = 0
    for layer in self.tmx.visible_layers:
      if hasattr(layer, "tiles"):
        for _x, _y, image in layer.tiles():
          total += 1
          if image is not None:
            have += 1

    ore_cnt = 0

    # 레이어 순서대로 한 번만 처리
    for layer in self.tmx.visible_layers:
      name = (getattr(layer, "name", "") or "").lower()

      # elif hasattr(layer, "layer_name"): ex)
      #  for layer_name in layer:
      #    if getattr(layer_name, "name", "") == "player_spawn":
      #      self.spawn_pos = (int(obj.x), int(obj.y))
      #      continue
      #    gid = getattr(layer_name, "gid", 0)
      #    if gid:
      #      image = self.tmx.get_tile_image_by_gid(gid)
      #      if image:
      #        h = image.get_height()
      #        Tile(image, (int(obj.x), int(obj.y) - h), self.render_all)

      # 1) 타일 레이어
      if hasattr(layer, "tiles"):
        for x, y, image in layer.tiles():
          if image is None:
            continue
          px, py = x * self.tile_w, y * self.tile_h

          if "ore" in name:
            gid = layer.data[y][x]  # GID 읽기
            props = self.tmx.get_tile_properties_by_gid(gid) if gid else None
            ore_type = (props.get("type") if props else None) or "stone"

            OreTile(image, (px, py), (self.ores, self.render_all, self.collision), ore_type)
            ore_cnt += 1
            continue

          if "collision" in name:
            Tile(image, (px, py), self.collision)
          elif "decor" in name:
            Tile(image, (px, py), self.decor)
            Tile(image, (px, py), self.render_all)
          else:
            Tile(image, (px, py), self.ground)
            Tile(image, (px, py), self.render_all)

      elif hasattr(layer, "image") and layer.image:
        ix = int(getattr(layer, "x", 0))
        iy = int(getattr(layer, "y", 0))
        Tile(layer.image, (ix, iy), self.render_all)

      elif hasattr(layer, "objects"):
        for obj in layer:
          if getattr(obj, "name", "") == "player_spawn":
            self.spawn_pos = (int(obj.x), int(obj.y))
            continue
          gid = getattr(obj, "gid", 0)
          if gid:
            image = self.tmx.get_tile_image_by_gid(gid)
            if image:
              h = image.get_height()
              Tile(image, (int(obj.x), int(obj.y) - h), self.render_all)

    print(f"\033[034m[TMX]\033[0m ores count = {ore_cnt}")
    print(f"\033[034m[TMX]\033[0m tiles total={total}, loaded={have}")
    if have == 0:
      print("\033[034m[TMX]\033[0m ⚠ 타일 이미지가 하나도 로드되지 않았습니다. (타일셋 경로 확인)")

  @property
  def pixel_size(self):
    w = getattr(self.tmx, "width", 0) * self.tile_w
    h = getattr(self.tmx, "height", 0) * self.tile_h
    return (w, h)
