# Code Style Guidelines

This project is governed by the following code style guidelines. Contributions
which do not follow these guidelines will not be accepted.

It is expected that you possess basic knowledge of **Python 3.6** or newer
*before* writing code for this project.

**Please read the ENTIRE page before writing code for this project!**

## Imports

Imports are grouped into 3 sections in the following order:

1. Python standard library
   - Standard imports
   - `from` imports
2. Third-party libraries
   - Standard imports
   - `from` imports
3. Other modules within the project
   - Standard imports
   - `from` imports

Each section is separated with a blank line in between. Within each section, the
subsections are separated without a new line between them. Each subsection is
alphabetically sorted independently of the others. Symbols listed in a `from`
import are also alphabetically sorted. `from` imports are generally discouraged
unless they improve readability significantly.

Example:

```python
import asyncio
import io
import sys
from pathlib import PurePosixPath
from typing import Callable, Dict, Iterable, Tuple

import aiohttp

from .. import command, module
from ..util import async_helpers
from .event_dispatcher import EventDispatcher
```

This import style is enforced using the [isort](https://github.com/timothycrosley/isort)
tool.

## Line Length

No lines of Python code should exceed 120 characters in length. This is 50% longer
than the line length recommended by PEP-8 (80 characters), but this was deemed a
worthwhile tradeoff for the reduced line wrapping at awkward points.

In Markdown files, the line length limit is *80-ish* for readability. This means
that you should generally attempt to stick to 80 characters, but it's fine to go
a few characters over if it improves raw readability significantly.

## General Code Style

Our general code style is the [Black](https://black.readthedocs.io/en/stable/the_black_code_style.html) code style. This is *mostly* compliant with PEP-8,
but violates it in a few areas in favor of enhanced readability. We abide by this
style strictly, except in terms of line length as described below.

This code style is enforced using the [Black](https://black.readthedocs.io/en/stable/)
tool.

## Symbol Naming

Follow the Python naming conventions:

- `PascalCase` for classes
- `snake_case` for functions, variables, attributes, and just about everything else

`camelCase` and any other naming conventions should not be used in Python code.

## Pythonicism

Code should generally be written in the Pythonic way, when applicable. For example,
use iterators to iterate through lists:

```python
values = [1, 2, 3, 4, 5]

# NOT Pythonic
for i in range(len(values)):
    val = values[i]
    print(val)

# Pythonic
for val in values:
    print(val)
```

## Whitespace

Split discrete logical sections of single *block* (indentation level) of code by
a single blank line. Do so sparingly, however, as to avoid *excessive* whitespace
which is counterproductive and makes the code harder to read.

Example:

```python
def get_processed_image():
    # Get the image
    url = get_url()
    token = get_token()
    image_data = get_image(url, token)

    # Process the image
    image = Image(img_data)
    image.invert()
    image.tint(Color.RED)
    image.flip()

    return image.to_bytes()
```

## Comments

Hard-to-understand or otherwise unclear pieces of code should be commented, as
seen in the example above. Use comments sparingly, however, because the best
code is self-documenting. Too many comments are counterproductive and can make
the code harder to read.

When in doubt, comment — too many comments are still better than none.

## Common Sense

Use your common sense while writing code. For example, do not combine multiple
statements on one line for the sake of writing fewer lines:

```python
# Bad
if val is None: return

# Good
if val is None:
    return
```

## Micro-Optimizations

> Premature optimization is the root of all evil.
>
> — Donald Knuth

Favor readability over micro-optimizations unless you have profiled the code and
identified it as a bottleneck.

## String Formatting

Prefer Python 3.6's f-strings over other forms of string formatting. Avoid using
legacy `%`-formatting unless it is being used for a debug log message, where it
becomes useful to avoid unnecessary formatting because `logging` will lazily evaluate
them. Likewise, you should avoid using `str.format()` unless absolutely necessary.

## Pre-Commit Hooks

Import style and general code style will automatically be enforced
when code is committed if you install the pre-commit hooks present in the project.
We use the [pre-commit](https://pre-commit.com/#install) framework to facilitate
their installation in a portable and flexible manner. Use of these hooks is
**highly recommended** to ensure that your code meets most of our style
guidelines before making it online. It saves time for everyone in the long run.
