import collections.abc


def _irepr_seq_iterable(painter, lst, highlight_idx=None, end_symbols=("[", "]"), *args, **kwargs):
    # Initialize state
    painter.write(end_symbols[0])
    elem_pos = None

    for idx, elem in enumerate(lst):
        # Add comma separator if this isn't the first element
        if idx > 0:
            painter.write(", ")

        # If this is our candidate element,
        if idx == highlight_idx:
            # Record the position and pass highlight flags
            elem_pos = painter.write(repr(elem), *args, **kwargs)
        else:
            painter.write(repr(elem))

    # Finalize string
    last_pos = painter.write(end_symbols[1])

    # Mark end as highlighted target if not found
    if elem_pos is None:
        elem_pos = last_pos

    # Return indices
    return elem_pos


def _irepr_dict(painter, dct, highlight_key=None, *args, **kwargs):
    # Initialize state
    painter.write("{")
    elem_pos = None

    for idx, (key, elem) in enumerate(dct.items()):
        # Add comma separator if this isn't the first element
        if idx > 0:
            painter.write(", ")

        # Add key first (no need to record this)
        painter.write(repr(key) + ": ")

        # If this is our candidate element,
        if key == highlight_key:
            # Record the position and pass highlight flags
            elem_pos = painter.write(repr(elem), *args, **kwargs)
        else:
            painter.write(repr(elem))

    # Finalize string
    last_pos = painter.write("}")

    # Mark end as highlighted target if not found
    if elem_pos is None:
        elem_pos = last_pos

    # Return indices
    return elem_pos


def irepr(painter, obj, *args, **kwargs):
    # Compare and invoke container-specific implementations if applicable to the given object
    # We use ABC collections classes to catch all similar classes, e.g. sortedcontainers objects
    if isinstance(obj, collections.abc.Sequence):
        return _irepr_seq_iterable(painter, obj, *args, **kwargs)
    elif isinstance(obj, collections.abc.Mapping):
        return _irepr_dict(painter, obj, *args, **kwargs)
    elif isinstance(obj, collections.abc.Set):
        # Same thing as sequences, just different symbols
        return _irepr_seq_iterable(painter, obj, *args, end_symbols=("{", "}"), **kwargs)
    else:
        # Fall back to a generic implementation with standard repr()
        return painter.write(repr(obj))
