import abc
import collections.abc
from typing import TYPE_CHECKING

import dictdiffer

from . import data, render

if TYPE_CHECKING:
    from .debugger import Debugger


class DiffProcessor(abc.ABC):
    def __init__(self: "Debugger"):
        # Full variable + values map
        self.vars = {}

        # File contents cache
        self.file_cache = {}

        # Propagate initialization to other mixins
        super().__init__()

    def _get_history(self, wrapper):
        return data.VarHistory(wrapper, self.vars)

    def process_add(self: "Debugger", chg_name, chg, frame_info, new_locals):
        # If we have a changed variable, elements were added to a list/set/dict
        if chg_name:
            # Get a reference to the container to check its type
            container = new_locals[chg_name]
            # Construct variable wrapper
            wrapper = data.Variable(chg_name, frame_info)

            if not self.vars[wrapper].ignored:
                # chg is a list of tuples with keys (index, key, etc.) and values
                for key, val in chg:
                    if isinstance(container, collections.abc.Set):
                        # Move value out of set if there's only 1
                        if len(val) == 1:
                            val = val.pop()

                        # Show it as an extension for sets
                        self.out.write_add(
                            chg_name,
                            val,
                            self._get_history(wrapper),
                            action="extended",
                            plural=isinstance(val, collections.abc.Set),
                        )
                    else:
                        # Render it as var[key] for lists, dicts, etc.
                        self.out.write_add(
                            render.key_var(chg_name, key), val, self._get_history(wrapper), action="added", plural=False
                        )

                # Record new value
                self.vars[wrapper].append(data.VarValue(container, frame_info))

        # Otherwise, it's a new variable
        else:
            # chg is a list of tuples with variable names and values
            for name, val in chg:
                wrapper = data.Variable(name, frame_info)
                ignored = frame_info.comment == "ignore"
                if ignored:
                    self.vars[wrapper] = data.VarValues(ignored=True)
                else:
                    self.out.write_add(name, val, self._get_history(wrapper), action="added", plural=False)
                    self.vars[wrapper] = data.VarValues(data.VarValue(val, frame_info))

    def process_change(self: "Debugger", chg_name, chg, frame_info, new_locals):
        before, after = chg

        # If the changed variable is given as a list, a list/set/dict element was changed
        if isinstance(chg_name, list):
            # chg_name is a tuple with the variable name and key
            var_name, key = chg_name
            # Render it as var_name[key]
            chg_name = f"{var_name}[{repr(key)}]"

            # Full changed value
            full_after = new_locals[var_name]
        else:
            var_name = chg_name
            full_after = after

        wrapper = data.Variable(var_name, frame_info)
        if not self.vars[wrapper].ignored:
            self.out.write_change(chg_name, before, after, self._get_history(wrapper), action="changed")
            self.vars[wrapper].append(data.VarValue(full_after, frame_info))

    def process_remove(self: "Debugger", chg_name, chg, frame_info, new_locals):
        # If we have a changed variable, elements were removed from a list/set/dict
        if chg_name:
            # Construct variable wrapper
            wrapper = data.Variable(chg_name, frame_info)

            if not self.vars[wrapper].ignored:
                for key, val in chg:
                    self.out.write_remove(
                        render.key_var(chg_name, key), val, self._get_history(wrapper), action="removed"
                    )

                # Get new container contents and log value
                container = new_locals[chg_name]
                self.vars[wrapper].append(data.VarValue(container, frame_info))

        # Otherwise, a variable was deleted
        else:
            # chg is a list of tuples with variable names and values
            for name, val in chg:
                # Construct variable wrapper
                wrapper = data.Variable(name, frame_info)

                if not self.vars[wrapper].ignored:
                    self.out.write_remove(name, val, self._get_history(wrapper), action="deleted")
                    self.vars[wrapper].deleted_line = frame_info.file_line

    def process_locals_diff(self: "Debugger", diff, frame_info, new_locals):
        for action, chg_var, chg in diff:
            if action == dictdiffer.ADD:
                self.process_add(chg_var, chg, frame_info, new_locals)
            elif action == dictdiffer.CHANGE:
                self.process_change(chg_var, chg, frame_info, new_locals)
            elif action == dictdiffer.REMOVE:
                self.process_remove(chg_var, chg, frame_info, new_locals)

    def finalize_history(self: "Debugger"):
        # Delete ignored variables (implementation detail) from history map
        to_delete = [var for var, values in self.vars.items() if values.ignored]
        for var in to_delete:
            del self.vars[var]
