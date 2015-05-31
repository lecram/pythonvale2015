import sys

def frame2name(frame):
  code = frame.f_code
  name = code.co_name
  if code.co_argcount:
    arg0 = code.co_varnames[0]
    self = frame.f_locals[arg0]
    method = getattr(self, name, None)
    if hasattr(method, "__func__"):
      if method.__func__.__code__ is code:
        clname = type(self).__name__
        name = "{}.{}".format(clname, name)
  return name

class CallGrapher:

  def __init__(self):
    self.calls = set()

  def __enter__(self):
    self.old_cb = sys.getprofile()
    sys.setprofile(self.callback)
    return self

  def __exit__(self, *args):
    sys.setprofile(self.old_cb)

  def callback(self, frame, event, arg):
    if event != 'call':
      return
    fname = frame.f_code.co_filename
    if fname == __file__ or fname[0] in "</":
      return
    caller = frame2name(frame.f_back)
    callee = frame2name(frame)
    self.calls.add((caller, callee))

  def dot(self):
    lines = "digraph {\n"
    fmt = '  "{}" -> "{}";'
    lines += "\n".join(fmt.format(a, b) for a, b in self.calls)
    lines += "\n}"
    return lines

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
  with CallGrapher() as cg:
    exec(code, globs)
  print(cg.dot())
