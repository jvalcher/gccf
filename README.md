
# gccf

`GCC` error formatter

<img src='formatted_output.png' height='350px'>


## Overview

This script parses the output from `GCC`'s `-fdiagnostics-format=sarif-stderr` flag and outputs easy-to-read error messages.


## Usage

As of this time, the `GCC` flag `-fmax-errors=n` does not work properly when using `-fdiagnostics-format` ([bug report](https://gcc.gnu.org/bugzilla/show_bug.cgi?id=126224)) so for now set the `result_count_max` variable at the top of the script if needed.<br>
<br>
For use as a Linux shell command, make sure that the shebang path at the top of the script points to your Python interpreter's location.

```sh
#!/usr/bin/python3
```

Then just copy the script to your `PATH`.

```sh
$ cp gccf.py ~/.local/bin/gccf

$ gccf -Wall -Wextra -o my_app main.c
```

See the `build_test_files_gccf` script for an example of how to import the core function into your own Python script.


## Development

```sh
$ ./build_test_files_gccf
$ ./build_test_files_gcc
```
