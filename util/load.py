import pygame, os

class Loader:
  cache = {}

  @staticmethod
  def load_images(base_path : str, filenames : str, scale=None):
    images = []

    for name in filenames:
      full_path = os.path.join(base_path, name)
      cache_key = (full_path, scale)

      if cache_key in Loader.cache:
        image = Loader.cache[cache_key]
      else:
        if os.path.exists(full_path):
          image = pygame.image.load(full_path).convert_alpha()
          if scale is not None:
            image = pygame.transform.scale(image, scale)
          Loader.cache[cache_key] = image
        else:
          print(f"import error: No file in {full_path}")
          if scale is not None:
            image = pygame.Surface(scale)
          else:
             image = pygame.Surface((32, 32))
          image.fill((255, 0, 255))  # 에러 표시용

      images.append(image)

    return images

  @staticmethod
  def load_image(path, scale=None):
    return Loader.load_images("", [path], scale)[0]

  @staticmethod
  def load_music(path, rightNow=False, loop=False):
      if not os.path.exists(path):
          print(f"import error: No music file in {path}")
          return

      try:
          pygame.mixer.music.load(path)
          if rightNow:
              loops = -1 if loop else 0
              pygame.mixer.music.play(loops=loops)
      except Exception as e:
          print(f"music load/play error: {e}")

