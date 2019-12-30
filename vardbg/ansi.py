"""ANSI color codes for terminal output"""

RED = "\u001b[1;31m"
GREEN = "\u001b[1;32m"
BLUE = "\u001b[1;34m"
BOLD = "\u001b[1m"
RESET = "\u001b[0m"


def red(text):
    return RED + text + RESET


def green(text):
    return GREEN + text + RESET


def blue(text):
    return BLUE + text + RESET


def bold(text):
    return BOLD + text + RESET
