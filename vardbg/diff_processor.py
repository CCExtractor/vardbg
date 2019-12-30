import abc
from typing import TYPE_CHECKING

import dictdiffer

from . import data, render

if TYPE_CHECKING:
    from .debugger import Debugger


class DiffProcessor(abc.ABC):
    def __init__(self: "Debugger"):
        # Full variable + values map
        self.vars = {}

        # Propagate initialization to other mixins
        super().__init__()

    def process_add(self: "Debugger", chg_name, chg, frame_info):
        # If we have a changed variable, elements were added to a list/set/dict
        if chg_name:
            # Get a reference to the container to check its type
            container = self.new_locals[chg_name]

            # chg is a list of tuples with keys (index, key, etc.) and values
            for key, val in chg:
                if isinstance(container, set):
                    # Move value out of set if there's only 1
                    if len(val) == 1:
                        val = val.pop()

                    # Show it as an extension for sets
                    self.print_add(chg_name, val, action="extended", plural=isinstance(val, set))
                else:
                    # Render it as var[key] for lists, dicts, etc.
                    self.print_add(render.key_var(chg_name, key), val)

            # Record new value
            self.vars[data.Variable(chg_name, frame_info)].append(data.VarValue(container, frame_info))

        # Otherwise, it's a new variable
        else:
            # chg is a list of tuples with variable names and values
            for name, val in chg:
                self.print_add(name, val)
                self.vars[data.Variable(name, frame_info)] = [data.VarValue(val, frame_info)]

    def process_change(self: "Debugger", chg_name, chg, frame_info):
        # If the changed variable is given as a list, a list/set/dict element was changed
        if isinstance(chg_name, list):
            # chg_name is a tuple with the variable name and key
            var_name, key = chg_name
            # Render it as var_name[key]
            chg_name = f"{var_name}[{repr(key)}]"
        else:
            var_name = chg_name

        # chg_name is the variable that was changed
        # chg is a tuple with the before and after values
        before, after = chg
        self.print_change(chg_name, before, after)
        self.vars[data.Variable(var_name, frame_info)].append(data.VarValue(after, frame_info))

    def process_remove(self: "Debugger", chg_name, chg, frame_info):
        # If we have a changed variable, elements were removed from a list/set/dict
        if chg_name:
            for key, val in chg:
                self.print_remove(render.key_var(chg_name, key), val)

            # Get new container contents and log value
            container = self.new_locals[chg_name]
            self.vars[data.Variable(chg_name, frame_info)].append(data.VarValue(container, frame_info))

        # Otherwise, a variable was deleted
        else:
            # chg is a list of tuples with variable names and values
            for name, val in chg:
                self.print_remove(name, val, action="deleted")

                # Find existing equivalent variable object
                new_var = data.Variable(name, frame_info)
                var = list(filter(lambda v: v == new_var, self.vars.keys()))[0]
                var.deleted_line = frame_info.file_line

    def process_locals_diff(self: "Debugger", diff, frame_info):
        for action, chg_var, chg in diff:
            if action == dictdiffer.ADD:
                self.process_add(chg_var, chg, frame_info)
            elif action == dictdiffer.CHANGE:
                self.process_change(chg_var, chg, frame_info)
            elif action == dictdiffer.REMOVE:
                self.process_remove(chg_var, chg, frame_info)
