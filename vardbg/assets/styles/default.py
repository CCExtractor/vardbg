from pygments.style import Style
from pygments.token import (
    Comment, Error, Keyword, Literal, Name, Number, Operator, String, Text
)
from vardbg.output.video_writer.getstyle import get_style_by_name

scheme = get_style_by_name('wood')

class DefaultStyle(Style): 
    background_color = scheme['base00']
    highlight_color = scheme['base02']

    styles = {
        Text: scheme['base05'],
        Error: scheme['base08'],  # .err

        Comment: scheme['base03'],  # .c
        Comment.Preproc: scheme['base0f'],  # .cp
        Comment.PreprocFile: scheme['base0b'],  # .cpf

        Keyword: scheme['base0e'],  # .k
        Keyword.Type: scheme['base08'],  # .kt

        Name.Attribute: scheme['base0d'],  # .na
        Name.Builtin: scheme['base0d'],  # .nb
        Name.Builtin.Pseudo: scheme['base08'],  # .bp
        Name.Class: scheme['base0d'],  # .nc
        Name.Constant: scheme['base09'],  # .no
        Name.Decorator: scheme['base09'],  # .nd
        Name.Function: scheme['base0d'],  # .nf
        Name.Namespace: scheme['base0d'],  # .nn
        Name.Tag: scheme['base0e'],  # .nt
        Name.Variable: scheme['base0d'],  # .nv
        Name.Variable.Instance: scheme['base08'],  # .vi

        Number: scheme['base09'],  # .m

        Operator: scheme['base0c'],  # .o
        Operator.Word: scheme['base0e'],  # .ow

        Literal: scheme['base0b'],  # .l

        String: scheme['base0b'],  # .s
        String.Interpol: scheme['base0f'],  # .si
        String.Regex: scheme['base0c'],  # .sr
        String.Symbol: scheme['base09'],  # .ss
    }
