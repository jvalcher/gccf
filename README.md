
# gccf

GCC error formatter

<img src='formatted_output.png' height='350px'>


## Overview

This script parses the data output from `gcc`'s `-fdiagnostics-format=json` flag. It works with `make` and possibly other builders as long as the only `[{` JSON object `}]` in its input is `gcc`'s.


## Usage

Make sure that the shebang path at the top of the script points to your Python interpreter's location.

```shell
#!/usr/bin/python3
```

Copy the script to your PATH.

```shell
$ cp gccf.py ~/.local/bin/gccf
$ gccf -Wall -Wextra -o my_app main.c
```

See the `build_test_files_gccf` script for an example of how to import the core function into your own Python script.


## Development

```shell
$ ./build_test_files_gccf
$ ./build_test_files_gcc
```
