# npc.py
import pygame
from util.__init__ import Loader, screen, text, Button
from camera import Camera

TALK_RANGE = 64  # distance to start talk

class Merchant(pygame.sprite.Sprite):
  def __init__(self, pos, blocking=True, image_path="image/npc/villager.png"):
    super().__init__()
    self.image = Loader.load_image(image_path, scale=(32, 32))
    self.rect = self.image.get_rect(topleft=pos)
    self.name = "merchant"
    self.blocking = blocking
    self.hitbox = self.rect.copy()
    self.is_talking = False
    self.lines = [{
      1 : "I have good things",
      2 : "Want to check it out?"
    },
    {
      1 : "Ok"
    }]
    self._line_idx = 0

  def toggle_talk(self):
    self.is_talking = not self.is_talking
    self._line_idx = 0

  def next_line(self, player):
    def open_shop(player):
      pygame.mouse.set_visible(True)
      w, h = screen.surface.get_size()
      panelR = pygame.Rect(int(w * 0.1), int(h * 0.1), int(w * 0.8), int(h * 0.8))

      btn_buy = Button(
        rect=(panelR.left + 40, panelR.top + 120, 260, 48),
        text="Buy CraftTable (100G)", bsign=True
      )
      btn_close = Button(
        rect=(panelR.right - 120, panelR.top + 20, 100, 36),
        color=(200, 80, 80), hover_color=(220, 100, 100),
        text="Close", bsign="CLOSE"
      )

      feedback_msg = ""
      clock = pygame.time.Clock()

      while True:
        events = pygame.event.get()
        for e in events:
          if e.type == pygame.QUIT:
            return True
          if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
            return True

        sig_buy = btn_buy.handle_events(events)
        sig_close = btn_close.handle_events(events)

        if sig_close == "CLOSE":
          pygame.mouse.set_visible(False)
          return True

        # 상점 버튼
        if sig_buy is True:
          price = 100
          if getattr(player, "has_auto", False):
            feedback_msg = "Already owned."
          elif getattr(player, "gold", 0) < price:
            feedback_msg = "Not enough gold."
          else:
            player.gold -= price
            player.has_auto = True
            return False

        # ---------- draw ----------
        overlay = pygame.Surface((w, h), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        screen.surface.blit(overlay, (0, 0))

        pygame.draw.rect(screen.surface, (245, 245, 250), panelR, border_radius=12)
        pygame.draw.rect(screen.surface, (30, 30, 50), panelR, width=3, border_radius=12)

        text.render((panelR.centerx, panelR.top + 50), "Tool Shop",
                    True, (20, 20, 30), centerpos="midtop", size=42)
        sub = f"Gold: {getattr(player, 'gold', 0)}G"
        text.render((panelR.left + 40, panelR.top + 80), sub,
                    True, (40, 40, 60), centerpos="topleft", size=28)

        if feedback_msg:
          text.render((panelR.left + 40, panelR.bottom - 80), feedback_msg,
                      True, (200, 60, 60), centerpos="topleft", size=24)

        text.render((panelR.left + 40, panelR.top + 170), "Automation Module",
                    True, (30, 30, 40), centerpos="topleft", size=28)
        text.render((panelR.left + 40, panelR.top + 205), "- Auto mining/processing",
                    True, (70, 70, 90), centerpos="topleft", size=22)
        text.render((panelR.left + 40, panelR.top + 232), "- Maintenance: 0G",
                    True, (70, 70, 90), centerpos="topleft", size=22)

        btn_buy.draw()
        btn_close.draw()

        pygame.display.flip()
        clock.tick(60)

    # ---------- dialogue flow ----------
    if self._line_idx < len(self.lines) - 1:
      self._line_idx += 1
    else:
      # open shop at the last line (trigger by SPACE in manager)
      still_not_open = False
      while not still_not_open:
        still_not_open = open_shop(player=player)
      self.toggle_talk()

  # ---------- UI helpers ----------
  def in_range(self, player):
    px, py = player.rect.center
    nx, ny = self.rect.center
    dx = nx - px; dy = ny - py
    return (dx*dx + dy*dy) ** 0.5 <= TALK_RANGE

  def draw_nameplate(self):
    def calculate_position():
      tl = Camera.instance.apply(self.rect)
      x = int(tl.x + self.rect.width // 2)
      y = int(tl.y - 6)
      return x, y

    if not screen.surface: return
    name = self.name
    x, y = calculate_position()
    bg = pygame.Surface((max(60, len(name)*10), 18), pygame.SRCALPHA)
    bg.fill((0, 0, 0, 140))
    screen.surface.blit(bg, bg.get_rect(center=(x, y)))
    text.render((x, y), name, True, (255, 255, 255), size=25)

  def draw_dialog(self):
    if not self.is_talking:
      return
    w, h = screen.surface.get_size()
    box_h = 90
    panel = pygame.Surface((w - 40, box_h), pygame.SRCALPHA)
    panel.fill((0, 0, 0, 170))
    rect = panel.get_rect(midbottom=(w//2, h - 12))
    screen.surface.blit(panel, rect)

    if 0 <= self._line_idx < len(self.lines):
      for i in range(len(self.lines[self._line_idx])):
        lines = self.lines[self._line_idx][i + 1]
        text.render((rect.centerx, rect.top + 24 * (i + 1)), lines, True, (255, 255, 255), size=22)
    else:
      lines = ""

    text.render((rect.right - 110, rect.bottom - 18),
                "E: No  SPACE: Yes", True, (200, 200, 200),
                size=16, centerpos="center")

class NpcManager:
  def __init__(self):
    self.group = pygame.sprite.Group()
    self.block_group = pygame.sprite.Group()

  def add(self, npc: Merchant):
    self.group.add(npc)
    if npc.blocking:
      self.block_group.add(npc)

  def sprites(self):
    return list(self.group.sprites())

  def update(self, player):
    for npc in self.group:
      npc.update(player)

  def draw_ui(self, player):
    for npc in self.group:
      if npc.in_range(player) and not npc.is_talking:
        npc.draw_nameplate()
    for npc in self.group:
      if npc.is_talking:
        npc.draw_dialog()
        break

  def handle_event(self, events, player):
    for event in events:
      if event.type != pygame.KEYDOWN:
        continue

      talking = next((n for n in self.group if n.is_talking), None)
      if talking:
        if event.key == pygame.K_SPACE:
          talking.next_line(player)
        elif event.key == pygame.K_e:
          talking.toggle_talk()
        return

      if event.key == pygame.K_e:
        for npc in self.group:
          if npc.in_range(player):
            npc.toggle_talk()
            break
