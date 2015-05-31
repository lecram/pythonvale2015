import sys
import linecache

class Debug:

  def __init__(self):
    self.state = "cont"
    self.breaks = set()
    self.args = ["c"]

  def __enter__(self):
    self.old_cb = sys.gettrace()
    self.prompt()
    sys.settrace(self.callback)
    return self

  def __exit__(self, *args):
    sys.settrace(self.old_cb)

  def prompt(self, globs=None, locs=None):
    args = self.args
    while True:
      args = input("> ").split() or args
      cmd = args.pop(0)
      if "break".startswith(cmd):
        self.breaks.add(int(args[0]))
      elif "unbreak".startswith(cmd):
        self.breaks.remove(int(args[0]))
      elif "continue".startswith(cmd):
        self.state = "cont"
        break
      elif "step".startswith(cmd):
        self.state = "step"
        break
      elif "print".startswith(cmd):
        source = " ".join(args)
        print(eval(source, globs, locs))
      elif "quit".startswith(cmd):
        exit()
      else:
        print("tente outra vez")
    self.args = args

  def callback(self, frame, event, arg):
    if event == 'line':
      fname = frame.f_code.co_filename
      if fname == __file__ or fname[0] in "</":
        return
      lineno = frame.f_lineno
      globs = frame.f_globals
      locs = frame.f_locals
      if self.state == "cont":
        if lineno in self.breaks:
          line = linecache.getline(fname, lineno)
          print(lineno, line.rstrip())
          self.prompt(globs, locs)
      elif self.state == "step":
        line = linecache.getline(fname, lineno)
        print(lineno, line.rstrip())
        self.prompt(globs, locs)
    return self.callback

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
  with Debug():
    exec(code, globs)
