"""ANSI colors for terminal output"""

import click


def red(content):
    return click.style(str(content), fg="red", bold=True)


def green(content):
    return click.style(str(content), fg="green", bold=True)


def blue(content):
    return click.style(str(content), fg="blue", bold=True)


def yellow(content):
    return click.style(str(content), fg="yellow", bold=True)


def bold(content):
    return click.style(str(content), bold=True)
