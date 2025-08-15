from pygame.sprite import Sprite
import os, pygame
from util.__init__ import Loader

ITEM_DICT = {
  "pickaxe" : Loader.load_image("image\\tools\\pickaxe.png", scale=(32, 32)),
  "coal" : Loader.load_image("image\\ore\\Coal2.png", scale=(32, 32)),
  "row_iron" : Loader.load_image("image\\ore\\row_iron.png", scale=(32, 32)),
  "stone2" : Loader.load_image("image\\ore\\stone2.png", scale=(32, 32))
  }


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
    "row_gold": ("row_gold", 1),
}
  VALUABLE_TABLE = {"stone2" : 2, "coal" : 4, "row_iron" : 10, "row_gold" : 15}

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

class CraftTable(Sprite):
  def __init__(self):
    self.img = Loader.load_image("image\\tools\crafttable.png")

class item:
  def __init__(self):
    self.item_table = {"row_iron" : ""}