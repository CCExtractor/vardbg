"""ANSI color codes for terminal output"""

RED = "\u001b[1;31m"
GREEN = "\u001b[1;32m"
BLUE = "\u001b[1;34m"
YELLOW = "\u001b[1;33m"
BOLD = "\u001b[1m"
RESET = "\u001b[0m"


def red(content):
    return RED + str(content) + RESET


def green(content):
    return GREEN + str(content) + RESET


def blue(content):
    return BLUE + str(content) + RESET


def yellow(content):
    return YELLOW + str(content) + RESET


def bold(content):
    return BOLD + str(content) + RESET
