from pathlib import Path

import toml
from pygments.formatter import Formatter
from pygments.styles.monokai import MonokaiStyle
from pygments.token import Token

BASE_PATH = Path(__file__).parent / ".." / ".." / ".."
DEFAULT_CFG_PATH = BASE_PATH / "config.toml"


def load_data(path):
    # Attempt to load file
    try:
        data = path.read_text()
    except FileNotFoundError:
        # Fall back to default config if not found
        data = DEFAULT_CFG_PATH.read_text()

    return data


def sub_path(path):
    # Replace first $VARDBG with base path
    if path.startswith("$VARDBG"):
        path = path.replace("$VARDBG", str(BASE_PATH), 1)

    return path


def calc_frac(value, frac):
    num, denom = frac
    return round(value * num / denom)


def parse_hex_color(string):
    if string.startswith("#"):
        string = string[1:]

    r = int(string[0:2], 16)
    g = int(string[2:4], 16)
    b = int(string[4:6], 16)

    return r, g, b, 255


def load_style(style):
    styles = {}
    formatter = Formatter(style=style)

    for token, params in formatter.style:
        color = parse_hex_color(params["color"]) if params["color"] else None
        # Italic and underline styles aren't supported, so just use bold for them
        bold = params["bold"] or params["italic"] or params["underline"]

        # Save style
        styles[token] = {"color": color, "bold": bold}

    return styles


class Config:
    def __init__(self, config_path):
        # Load config
        self.data = load_data(Path(config_path))
        self.config = toml.loads(self.data)

        # Extract values
        general = self.config["general"]
        self.w = general["width"]
        self.h = general["height"]
        self.fps = general["fps"]

        self.intro_text = general["intro_text"]
        self.intro_time = general["intro_time"]
        self.watermark = general["watermark"]

        sizes = self.config["sizes"]
        self.var_x = calc_frac(self.w, sizes["code_width"])
        self.out_y = calc_frac(self.h, sizes["code_height"])
        self.ovar_y = calc_frac(self.h, sizes["last_variable_height"])

        self.head_padding = sizes["heading_padding"]
        self.sect_padding = sizes["section_padding"]

        self.line_height = sizes["line_height"]

        fonts = self.config["fonts"]
        self.font_body = (sub_path(fonts["body"]), fonts["body_size"])
        self.font_body_bold = (sub_path(fonts["body_bold"]), fonts["body_size"])
        self.font_caption = (sub_path(fonts["caption"]), fonts["caption_size"])
        self.font_heading = (sub_path(fonts["heading"]), fonts["heading_size"])
        self.font_intro = (sub_path(fonts["intro"]), fonts["intro_size"])

        style = MonokaiStyle
        self.styles = load_style(style)

        self.bg = parse_hex_color(style.background_color)
        self.highlight = parse_hex_color(style.highlight_color)
        self.fg_divider = self.styles[Token.Generic.Subheading]["color"]
        self.fg_heading = self.styles[Token.Name]["color"]
        self.fg_body = self.styles[Token.Text]["color"]
        self.fg_watermark = self.styles[Token.Comment]["color"]

        self.red = self.styles[Token.Operator]["color"]
        self.green = self.styles[Token.Name.Function]["color"]
        self.blue = self.styles[Token.Keyword]["color"]
