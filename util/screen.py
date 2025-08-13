import pygame, time as pytime, sys, math as pymath
from util.math import math

class screen:
  clock = None
  start_time = None
  x = 1250
  y = int(x * 9 / 16)
  fps = 60
  surface = None

  def __eq__(self, value):
    pass

  @staticmethod
  def init(width=1250, height=None, caption="Turn Game", fps_=60):
    screen.start_time = pytime.time()
    if height is None:
      height = int(width * (9 / 16))

    screen.surface = pygame.display.set_mode((width, height))
    pygame.display.set_caption(caption)
    screen.clock = pygame.time.Clock()
    screen.fps = fps_

  @staticmethod
  def set_screen():
    screen.fill((0, 0, 0))

  @staticmethod
  def update():
    pygame.display.update()
    screen.clock.tick(screen.fps)

  @staticmethod
  def exit():
    print("save code will input here")
    end_time = pytime.time()
    running_time = (end_time - screen.start_time)
    print("게임이 돌아간 시간 : {}초 ========================".format(pymath.ceil(running_time)))
    pygame.quit()
    sys.exit()

  @staticmethod
  def fill(fill: tuple = None, top_color: tuple = (255, 255, 255), bottom_color: tuple = (0, 0, 0)):
    try:
      if fill is not None:
        screen.surface.fill(fill)
      else:
        raise ValueError
    except:
      height = screen.surface.get_height()
      width = screen.surface.get_width()
      for y in range(height):
        ratio = y / height
        r = int(top_color[0] * (1 - ratio) + bottom_color[0] * ratio)
        g = int(top_color[1] * (1 - ratio) + bottom_color[1] * ratio)
        b = int(top_color[2] * (1 - ratio) + bottom_color[2] * ratio)
        pygame.draw.line(screen.surface, (r, g, b), (0, y), (width, y))