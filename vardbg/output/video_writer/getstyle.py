"""
    vardbg.styles
    ~~~~~~~~~~~~~~~

"""

from pygments.util import ClassNotFound


STYLE_ENTRY_POINT = 'vardbg.assets.styles'


def iter_entry_points(group_name):
    try:
        import pkg_resources
    except (ImportError, IOError):
        return []

    return pkg_resources.iter_entry_points(group_name)

def find_plugin_styles():
    for entrypoint in iter_entry_points(STYLE_ENTRY_POINT):
        yield entrypoint.name, entrypoint.load()

#: Maps style names to 'submodule::dictname'.
STYLE_MAP = {
    'wood': 'wood::scheme'
}


def get_style_by_name(name):
    if name in STYLE_MAP:
        mod, cls = STYLE_MAP[name].split('::')
        builtin = "yes"
    else:
        for found_name, style in find_plugin_styles():
            if name == found_name:
                return style
        # perhaps it got dropped into our styles package
        builtin = ""
        mod = name
        cls = name.title() + "Style"
        print(mod)

    try:
        mod = __import__('vardbg.assets.styles.' + mod, None, None, [cls])
    except ImportError:
        raise ClassNotFound("Could not find style module %r" % mod +
                         (builtin and ", though it should be builtin") + ".")
    try:
        return getattr(mod, cls)
    except AttributeError:
        raise ClassNotFound("Could not find style class %r in style module." % cls)


