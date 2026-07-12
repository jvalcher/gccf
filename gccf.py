#!/usr/bin/python3

'''
gccf - GCC error formatter
Author: jvalcher
URL: https://github.com/jvalcher/gccf
License: MIT
'''

import subprocess
import sys
import json
import textwrap
import re
import shutil

### Colors
RESET = "\033[0m"
RED = "\033[38;2;232;135;149m"
GREEN  = "\033[38;2;100;185;100m"
YELLOW = "\033[38;2;185;165;55m"
PURPLE = "\033[38;2;185;145;220m"
CYAN = "\033[0;36m"
B_MAX_BLUE = "\033[1;94m"
B_MAX_CYAN = "\033[1;96m"
B_MAX_RED = "\033[1;91m"
YELLOW_GOLD  = "\033[38;2;210;170;40m"

ERR_COLOR              = RED
WARN_COLOR             = PURPLE
MISC_COLOR             = B_MAX_CYAN
FILE_PATH_COLOR        = GREEN
LINE_NUM_COLOR         = YELLOW_GOLD
MSG_PROMPT_COLOR       = B_MAX_BLUE
MSG_COLOR              = CYAN
MSG_STR_COLOR          = YELLOW
ERR_CODE_PROMPT_COLOR  = ERR_COLOR
WARN_CODE_PROMPT_COLOR = WARN_COLOR
ERR_CARET_COLOR        = ERR_COLOR
WARN_CARET_COLOR       = WARN_COLOR

def create_indent_string (n):
    indent = ''
    for _ in range(n):
        indent = ' ' + indent
    return indent

def print_error(node_type, msg, type_str, file_path, line_number, start_col, end_col):

    term_cols = shutil.get_terminal_size().columns
    code_indent = "     "
    msg_indent = "     "
    prompt = ">>>  "

    type_str = type_str.capitalize()

    TYPE_COLOR = MISC_COLOR
    CODE_PROMPT_COLOR = MISC_COLOR
    CARET_COLOR = MISC_COLOR

    if type_str == "Error":
        TYPE_COLOR = ERR_COLOR
        CODE_PROMPT_COLOR = ERR_CODE_PROMPT_COLOR
        CARET_COLOR = ERR_CARET_COLOR
        err_buff = " " * (len("Warning") - len("Error"))
    elif type_str == "Warning":
        TYPE_COLOR = WARN_COLOR
        CODE_PROMPT_COLOR = WARN_CODE_PROMPT_COLOR
        CARET_COLOR = WARN_CARET_COLOR
        err_buff = ""
    else:
        err_buff = " " * (len("Warning") - len(type_str) + 2)

    if node_type != "location" and not (node_type == "child" and type_str == "Note"):
        return

    error = f"{err_buff}{TYPE_COLOR}{type_str}{RESET}:  {FILE_PATH_COLOR}{file_path}{RESET} : {LINE_NUM_COLOR}{line_number}{RESET}"

    msg = msg[:1].upper() + msg[1:]
    msg = f"{MSG_PROMPT_COLOR}{prompt}{MSG_COLOR}{msg}{RESET}"
    msg = textwrap.fill(
        msg,
        initial_indent=msg_indent,
        subsequent_indent=msg_indent + " " * len(prompt),
        width=term_cols
    )
    msg = re.sub(r"‘([^‘]*)’", rf"‘{MSG_STR_COLOR}\1{RESET}{MSG_COLOR}’", msg)

    code_line = ""
    stripped_spaces = 0

    try:
        with open(file_path) as f:
            for lineno, line in enumerate(f, start=1):
                if lineno == line_number:
                    stripped_spaces = len(line) - len(line.lstrip())
                    code_line = line.lstrip().rstrip("\n")
                    break
                else:
                    code_line = f'Unable to find line {line_number} in "{file_path}"'
    except FileNotFoundError:
        code_line = f'Unable to find "{file_path}"'

    print(error)
    print(msg)

    print(code_indent + f"{CODE_PROMPT_COLOR}{prompt}{RESET}" + code_line)

    start = max(1, start_col - stripped_spaces)
    end = max(start, end_col - stripped_spaces)

    caret = (
        code_indent +
        " " * len(prompt) +
        " " * (start - 1) +
        CARET_COLOR +
        "^" * max(1, end - start) +
        RESET
    )

    print(caret)
    print()

def format_gcc_output(command):

    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    status = result.returncode

    if result.stdout:
        print(result.stdout, end="")

    printed = False

    try:
        sarif = json.loads(result.stderr)
    except json.JSONDecodeError:
        if result.stderr:
            print(result.stderr, end="")
        sys.exit(status)

    for run in sarif["runs"]:
        for result in run["results"]:

            if not printed:
                print()
                printed = True

            level = result.get("level", "note")
            message = result["message"]["text"]

            file_path = ""
            line_number = 0
            start_col = 1
            end_col = 1

            locations = result.get("locations", [])
            if locations:
                physical = locations[0].get("physicalLocation")
                if physical:
                    artifact = physical.get("artifactLocation", {})
                    region = physical.get("region", {})

                    file_path = artifact.get("uri", "")
                    line_number = region.get("startLine", 0)
                    start_col = region.get("startColumn", 1)
                    end_col = region.get("endColumn", start_col + 1)

            if file_path:
                print_error(
                    "location",
                    message,
                    level,
                    file_path,
                    line_number,
                    start_col,
                    end_col
                )
            else:
                print(f"{level.capitalize()}: {message}")

    sys.exit(status)

if __name__ == "__main__":
    args = sys.argv[1:]
    args_str = " ".join(args)
    cmd = f'gcc -fdiagnostics-format=sarif-stderr {args_str}'
    format_gcc_output(cmd);

