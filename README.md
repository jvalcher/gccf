
# GCC error formatter

<img src='formatted_output.png' height='350px'>

## Overview

- Uses the `-fdiagnostics-format=json` flag
- Works with Make et al. as long as the only `[{` JSON objects `}]` in the output are GCC's

## Usage

### As import

```python
from gccf import format_gcc_output
command = 'g++ -Wall -Wextra -fdiagnostics-format=json test2.cpp'
format_gcc_output (command)
```

### As bash script
Edit the `gcc_cmd` string at the top of `gccf.py` as needed and run.

```bash
$ ./gccf.py     # uses /usr/bin/python
```

## Color configuration

Personalize the colors at the top of `gccf.py`.<br>

## Development

```bash
$ ./run_tests
$ ./get_unformatted_errors
```
