from pathlib import Path

import toml

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

        colors = self.config["colors"]
        self.bg = tuple(colors["background"])
        self.fg_heading = tuple(colors["heading"])
        self.fg_body = tuple(colors["body"])
        self.fg_watermark = tuple(colors["watermark"])
        self.highlight = tuple(colors["highlight"])

        self.red = tuple(colors["red"])
        self.green = tuple(colors["green"])
        self.blue = tuple(colors["blue"])
