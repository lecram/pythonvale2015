import sys
import functools

def colored(color, text):
  return "\033[{}m{}\033[0m".format(color, text)

fs = [functools.partial(colored, color) for color
      in map(str, range(31, 38))]
red, green, yellow, blue, magenta, cyan, white = fs

class Cover:

  def __init__(self):
    self.covered = {}

  def __enter__(self):
    self.old_cb = sys.gettrace()
    sys.settrace(self.callback)
    return self

  def __exit__(self, *args):
    sys.settrace(self.old_cb)

  def callback(self, frame, event, arg):
    if event == 'line':
      fname = frame.f_code.co_filename
      if fname == __file__ or fname[0] in "</":
        return
      lineno = frame.f_lineno
      s = self.covered.get(fname, set())
      s.add(lineno)
      self.covered[fname] = s
    return self.callback

  def pprint(self):
    for fname in sorted(self.covered):
      try:
        f = open(fname)
      except IOError:
        continue
      print("[{}]".format(fname))
      linenos = self.covered[fname]
      for lineno, line in enumerate(open(fname)):
        if (lineno + 1) in linenos:
          print(green(line), end='')
        else:
          print(red(line), end='')

if __name__ == "__main__":
  import os
  args = sys.argv[1:]
  if not args:
    sys.exit("usage: python {} SCRIPT".format(sys.argv[0]))
  progname = args[0]
  dirname = os.path.dirname(progname)
  sys.path.insert(0, dirname)
  with open(progname, 'rb') as fp:
    code = compile(fp.read(), progname, 'exec')
  globs = {
    '__file__': progname,
    '__name__': '__main__',
    '__package__': None,
    '__cached__': None,
  }
  with Cover() as cv:
    exec(code, globs)
  cv.pprint()
