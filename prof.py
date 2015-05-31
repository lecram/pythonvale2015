import os
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

class FuncProf:

  def __init__(self, instrument):
    self.instrument = instrument
    self.stack = []
    self.traces = {}

  def __enter__(self):
    self.old_cb = sys.getprofile()
    sys.setprofile(self.callback)
    return self

  def __exit__(self, *args):
    sys.setprofile(self.old_cb)

  def callback(self, frame, event, arg):
    filename = frame.f_code.co_filename
    if filename == __file__ or filename[0] in "</":
      return
    if event == 'call':
      self.push()
    elif event == 'return':
      funcname = frame2name(frame)
      key = (filename, funcname)
      self.pop(key)

  def push(self):
      before = self.instrument()
      self.stack.append(before)

  def pop(self, key):
      after = self.instrument()
      before = self.stack.pop()
      delta = after - before
      trace = self.traces.get(key, [])
      trace.append(delta)
      self.traces[key] = trace

  def pprint(self):
    print("file:function\tvalue\n")
    traces = {k: (len(v), sum(v)) for k, v in self.traces.items()}
    for key in sorted(traces, key=lambda c: -traces[c][1]):
      filename, funcname = key
      bname = os.path.basename(filename)
      count, value = traces[key]
      if value < 0.01:
        break
      fmt = "{}:{}\t{:.2f}"
      print(fmt.format(bname, funcname, value))

if __name__ == "__main__":
  import time
  #import resource
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
  #def inst():
  #  return resource.getrusage(resource.RUSAGE_SELF).ru_utime
  inst = time.perf_counter
  with FuncProf(inst) as prof:
    exec(code, globs)
  prof.pprint()
