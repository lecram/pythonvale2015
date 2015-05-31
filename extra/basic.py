# BASIC MODE
from goto import goto

def main():
  i = 1
  print(i)
  i += 1
  if i <= 5:
    goto(6)
  return

main()
