
# gccf

GCC error formatter

<img src='formatted_output.png' height='350px'>


## Overview

This script parses the data output from `gcc`'s `-fdiagnostics-format=json` flag. It works with `make` and possibly other builders as long as the only `[{` JSON object `}]` in its input is `gcc`'s.


## Usage

Make sure that the shell shebang path at the top of the script points to your Python interpreter's location.

```bash
$ cp gccf.py ~/.local/bin/gccf
$ gccf -Wall -Wextra -o my_app main.c
```

See the `run_tests` shell script for an example of how to import the core function.


## Development

```bash
$ ./run_tests
$ ./get_unformatted_errors
```
