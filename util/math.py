import math as Math

#===========================================math.py===========================================
class math:
  inf = Math.inf

  @staticmethod
  def limit(val, min_val: int, max_val: int):
    done = False
    if val == max_val:
      print("max")
      done = True
    return [max(min_val, min(val, max_val)), done]

  @staticmethod
  def distance(pos1, pos2):
    x1, y1 = pos1
    x2, y2 = pos2
    return Math.sqrt((x1 - x2)**2 + (y1 - y2)**2)

  @staticmethod
  def length(pos1, pos2):
    return (pos2[0] - pos1[0], pos2[1] - pos1[1])
