import math
from array import array
import collections

def _fill(color, n):
  for i in range(n):
    yield from color

class Canvas:

  def __init__(self, width, height, bgcolor=(255, 255, 255)):
    self.width   = width
    self.height  = height
    self.bgcolor = bgcolor
    n = width * height
    self.data = array('B', _fill(bgcolor, n))

  def __getitem__(self, key):
    x, y = key
    i = 3 * (y * self.width + x)
    r, g, b = self.data[i:i+3]
    return r, g, b

  def __setitem__(self, key, value):
    x, y = key
    i = 3 * (y * self.width + x)
    *fg, a = value
    color = self.blend(self.data[i:i+3], fg, a)
    self.data[i:i+3] = array('B', color)

  def blend(self, bg, fg, alpha):
    r0, g0, b0 = bg
    r1, g1, b1 = fg
    beta = 1 - alpha
    r = int(r0 * beta + r1 * alpha + 0.5)
    g = int(g0 * beta + g1 * alpha + 0.5)
    b = int(b0 * beta + b1 * alpha + 0.5)
    return r, g, b

  def save(self, fp):
    fp.write(b"P6\n")
    fp.write("{0.width} {0.height}\n".format(self).encode("ascii"))
    fp.write(b"255\n")
    self.data.tofile(fp)

def dptpt(p, q):
  px, py = p
  qx, qy = q
  d = math.hypot(qx - px, qy - py)
  return d

def dptedge(p, e):
  px, py = p
  (ax, ay), (bx, by) = e
  # Project P onto the line R passing through E to find a point Q.
  dx = bx - ax
  dy = by - ay
  s = (dx * (py - ay) + dy * (ax - px)) / (dx * dx + dy * dy)
  qx = px + dy * s
  qy = py - dx * s
  #  If the projection Q is within E end points, return the length of PQ,
  # otherwise, return the length of the smaller segment of PA and PB.
  minx, maxx = (ax, bx) if ax < bx else (bx, ax)
  miny, maxy = (ay, by) if ay < by else (by, ay)
  if minx <= qx <= maxx and miny <= qy <= maxy:
    return dptpt(p, (qx, qy))
  else:
    return min(dptpt(p, e[0]), dptpt(p, e[1]))

def aa(d, r):
  r0 = r - 0.25
  r1 = r + 0.25
  if d <= r0:
    return 1
  elif d <= r1:
    return (r1 - d) * 2
  else:
    return 0

def line_f(x0, y0, x1, y1, w):
  hw = w / 2
  def func(x, y):
    d = dptedge((x, y), ((x0, y0), (x1, y1)))
    f = 0
    s = aa(d, hw)
    return f, s
  return func

def circle_f(cx, cy, r, w):
  hw = w / 2
  def func(x, y):
    d = dptpt((cx, cy), (x, y))
    f = aa(d, r)
    s = aa(abs(d-r), hw)
    return f, s
  return func

def uny_f(op, func1):
  def func(x, y):
    f, s = func1(x, y)
    f = op(f)
    s = op(s)
    return f, s
  return func

def bin_f(op, func1, func2):
  def func(x, y):
    f1, s1 = func1(x, y)
    f2, s2 = func2(x, y)
    f = op(f1, f2)
    s = op(s1, s2)
    return f, s
  return func

inv_f = lambda f1: uny_f(lambda v: 1 - v, f1)
min_f = lambda f1, f2: bin_f(min, f1, f2)
max_f = lambda f1, f2: bin_f(max, f1, f2)

class State:
  __slots__ = "width alpha fill stroke".split()

  def __init__(self):
    self.width = 1
    self.alpha = 1
    self.fill = (128, 128, 128)
    self.stroke = (0, 0, 0)

  def copy(self):
    stt = State()
    stt.width = self.width
    stt.alpha = self.alpha
    stt.fill = self.fill
    stt.stroke = self.stroke
    return stt

def enqueue(state: State, stack: list, queue: list, token: str) -> None:
  if token.replace(".", "").isdecimal():
    stack.append(float(token))
  elif token == "setwidth":
    state.width = stack.pop()
  elif token == "setalpha":
    state.alpha = stack.pop()
  elif token == "setfill":
    state.fill = tuple(stack[-3:])
    stack[-3:] = []
  elif token == "setstroke":
    state.stroke = tuple(stack[-3:])
    stack[-3:] = []
  elif token == "line":
    x0, y0, x1, y1 = stack[-4:]
    stack[-4:] = [line_f(x0, y0, x1, y1, state.width)]
  elif token == "circle":
    cx, cy, r = stack[-3:]
    stack[-3:] = [circle_f(cx, cy, r, state.width)]
  elif token == "inv":
    stack[-1] = inv_f(stack[-1])
  elif token == "min":
    stack[-2:] = [min_f(*stack[-2:])]
  elif token == "max":
    stack[-2:] = [max_f(*stack[-2:])]
  elif token == "fill":
    action = (stack.pop(), [0], state.copy())
    queue.append(action)
  elif token == "strk":
    action = (stack.pop(), [1], state.copy())
    queue.append(action)
  elif token == "fillstrk":
    action = (stack.pop(), [0, 1], state.copy())
    queue.append(action)
  elif token == "strkfill":
    action = (stack.pop(), [1, 0], state.copy())
    queue.append(action)
  else:
    raise ValueError("unknown token: {}".format(token))

def dequeue(canvas, queue):
  for func, seq, state in queue:
    for y in range(canvas.height):
      for x in range(canvas.width):
        vs = func(x, y)
        cs = state.fill, state.stroke
        for i in seq:
          canvas[x, y] = cs[i] + (state.alpha * vs[i],)

def main(fp_in, fp_out):
  state = State()
  stack = []
  queue = []
  for line in fp_in:
    for token in filter(None, line.split()):
      if token.startswith("#"):
        break
      enqueue(state, stack, queue, token)
  width, height = map(int, stack[-2:])
  canvas = Canvas(width, height)
  dequeue(canvas, queue)
  canvas.save(fp_out)

if __name__ == "__main__":
  #import sys
  #import fileinput
  #main(fileinput.input(), sys.stdout.buffer)
  import io
  inp = io.StringIO("""
  255 0 0 setfill
  30 20 12 circle fill
  60 40
  """)
  out = io.BytesIO()
  main(inp, out)
