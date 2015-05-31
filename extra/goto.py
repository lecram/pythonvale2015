import sys

def goto(x):
  return x

class GoTo:

  def __init__(self):
    self.target = None
    sys.settrace(self.globaltrace)

  def globaltrace(self, frame, event, arg):
    if event == 'call':
      return self.localtrace

  def localtrace(self, frame, event, arg):
    if event == 'return':
      if frame.f_code.co_name == 'goto':
        self.target = arg
    elif event == 'line':
      if self.target is not None:
        frame.f_lineno = self.target
        self.target = None
    return self.localtrace

GoTo()
