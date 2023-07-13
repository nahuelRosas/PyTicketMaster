import sys


def get_input(prompt):
    if sys.stdin.isatty():
        return input(prompt)
    else:
        return sys.stdin.readline().rstrip("\n")
