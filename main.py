import pygame
pygame.init()

from util.__init__ import screen, text as texts
screen.init(caption="MineFactory")
texts.init(font = "basic"); text = texts.instance

from util.map_loader import TMXMap
TMXMap.init("level01.tmx", tile_size=(32, 32))
tmx_map = TMXMap.get()

from player import Player, SLOT_DICT
Player.init()
player = Player.get()
player.inventory.set_slot_positions(SLOT_DICT)
player.rect.topleft = tmx_map.spawn_pos

from playerUi import Ui
Ui.init()
ui = Ui.instance

from npc import Merchant, NpcManager

npcman = NpcManager()
merchant = Merchant((500, 200))
npcman.add(merchant)

for s in npcman.sprites():
  tmx_map.render_all.add(s)
  tmx_map.collision.add(s)   # NPC와도 부딪히게(원하면 빼도 됨)


from camera import Camera
Camera.init(target=player, objects=tmx_map.render_all)
camera = Camera.instance

tmx_map.render_all.add(player)

player.gold += 1000

class Ingame:
  def __init__(self):
    self.F3 = False
    self.inventory_open = False
    pygame.mouse.set_visible(False)

  def run(self):
    while True:
      events = pygame.event.get()

      for event in events:
        if event.type == pygame.QUIT:
          screen.exit()
        if event.type == pygame.KEYDOWN:
          if event.key == pygame.K_ESCAPE:
            screen.exit()
          if event.key == pygame.K_F3:
            self.F3 = not self.F3

          if event.key == pygame.K_i:
            self.inventory_open = not self.inventory_open
            player.inventory.set_open(self.inventory_open)

          if event.type == pygame.KEYDOWN:
            for i, key in enumerate([
              pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5,
              pygame.K_6, pygame.K_7, pygame.K_8, pygame.K_9, pygame.K_0
              ]):
              if event.key == key:
                player.inventory.select_hotbar(i)

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
          player.mine_at_mouse(event.pos)

      if not merchant.is_talking:
        player.keyevents()

      screen.set_screen()

      camera.draw()
      ui.draw()
      player.inventory.draw(screen.surface)
      player.inventory.draw_item_tooltip()

      npcman.update(player)
      npcman.draw_ui(player)

      npcman.handle_event(events, player)

      player.draw_cursor(screen.surface)

      if self.F3:
        text.render((0, 0),
          f"x : {round(player.rect.x / 32, 0)}, y : {round(player.rect.y / 32, 0)}",
          False, (255, 255, 255), centerpos="topleft", size=25)
        text.render((screen.x, screen.y),
          "classic v0.5 (npc)", True,
          (255, 50, 100), centerpos="bottomright", size=25)

      screen.update()

game = Ingame()
game.run()