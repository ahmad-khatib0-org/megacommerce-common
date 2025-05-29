from time import time


class TimeUtils():
  @classmethod
  def time_in_milies(cls) -> float:
    return time() * 1000
