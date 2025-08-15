import os
from pygame.sprite import Sprite, Group
from pytmx.util_pygame import load_pygame
from itemstorge.itemsprites import OreTile, Tile
from settings import MAPS_PATH

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
    self.render_all = Group()  # 화면 그리기용

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

    for layer in self.tmx.visible_layers:
      name = (getattr(layer, "name", "") or "").lower()
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
      print("\033[034m[TMX]\033[0m  타일 이미지가 하나도 로드되지 않았습니다. (타일셋 경로 확인)")

  @property
  def pixel_size(self):
    w = getattr(self.tmx, "width", 0) * self.tile_w
    h = getattr(self.tmx, "height", 0) * self.tile_h
    return (w, h)
