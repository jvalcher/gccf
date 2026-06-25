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

def print_error (node_type, msg, type_str, file_path, line_number, caret_cols):
    '''
    Print error, warning message
    '''

    term_size = shutil.get_terminal_size()
    term_cols = term_size.columns
    code_indent = '     '
    msg_indent  = '     '
    type_str = ''.join([c.upper() if i == 0 else c for i,c in enumerate(type_str)])
    err_buff = ''
    msg_num = -1
    TYPE_COLOR = MISC_COLOR

    if node_type == "location" or (node_type == "child" and type_str == "note"):

        # <error type>: <file path>: <line number>
        if type_str == 'Error':
            TYPE_COLOR = ERR_COLOR
            err_buff = create_indent_string (len('Warning') - len('Error'))
            err_buff = create_indent_string (len(err_buff))
        elif type_str == 'Warning':
            TYPE_COLOR = WARN_COLOR
            err_buff = create_indent_string (0)
        else:
            err_buff = create_indent_string (len('Warning') - len(type_str))
            err_buff = create_indent_string (len(err_buff) + 2)
        error = f"{err_buff}{TYPE_COLOR}{type_str}{RESET}:  {FILE_PATH_COLOR}{file_path}{RESET} : {LINE_NUM_COLOR}{line_number}{RESET}"

        # message
        prompt = ">>>  "
        msg_str = ''.join([c.upper() if i == 0 else c for i,c in enumerate(msg)])
        msg_str = f"{MSG_PROMPT_COLOR}{prompt}{MSG_COLOR}{msg_str}{RESET}"
        msg_str = textwrap.fill (msg_str, initial_indent=msg_indent, subsequent_indent= msg_indent + f"{'': <{len(prompt)}}", width=term_cols)
        msg_str = re.sub (r"‘([^‘]*)’", rf"‘{MSG_STR_COLOR}\1{RESET}{MSG_COLOR}’", msg_str)

        # line of code
        code_line = ''
        stripped_spaces = 0
        line_found = False
        CODE_PROMPT_COLOR = MISC_COLOR
        if type_str == 'Warning':
            CODE_PROMPT_COLOR = WARN_CODE_PROMPT_COLOR
        elif type_str == 'Error':
            CODE_PROMPT_COLOR = ERR_CODE_PROMPT_COLOR
        try:
            with open(file_path, 'r') as file:
                for current_line_number, line in enumerate(file, start=1):
                    if current_line_number == line_number:
                        orig_code_line = line
                        code_line = orig_code_line.lstrip()
                        stripped_spaces = len(orig_code_line) - len(code_line)
                        line_found = True
                        break
        except FileNotFoundError:
            code_line = f"Unable to find \"{file_path}\""
        if line_found is False:
            code_line = f"Unable to find line number {line_number} in \"{file_path}\""
        code_line = code_indent + f"{CODE_PROMPT_COLOR}{prompt}{RESET}" + code_line.rstrip('\n')

        # caret
        CARET_COLOR = MISC_COLOR
        if type_str == 'Warning':
            CARET_COLOR = WARN_CARET_COLOR
        elif type_str == 'Error':
            CARET_COLOR = ERR_CARET_COLOR
        caret_indent = create_indent_string (caret_cols - stripped_spaces - 2)
        if len(caret_indent) == 0:
            code_indent = code_indent[1:]
        caret = code_indent + caret_indent + f'{"": <{len(prompt)}}' + f'{CARET_COLOR}⤴{RESET}'

        print (error)
        print (msg_str)
        print (code_line)
        print (caret)
        print ("")

def format_gcc_output(command):
    '''
    Format GCC compiler errors from '-fdiagnostics-format=json' flag.
    Also prints non-JSON diagnostics (e.g. ld, collect2).
    '''

    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    output = result.stdout + result.stderr
    status = result.returncode

    print()

    for line in output.splitlines():

        line = line.strip()

        if not line or line == "[]":
            continue

        # JSON diagnostics from GCC
        if line.startswith("[{"):

            for msg in json.loads(line):

                type_str = msg["kind"]
                file_path = ""
                line_number = 0
                caret_cols = []

                for loc in msg["locations"]:
                    caret = loc.get("caret")
                    if caret is None:
                        continue

                    file_path = caret.get("file")
                    line_number = caret.get("line")
                    caret_cols.append(caret.get("column"))

                if caret_cols:
                    print_error(
                        "location",
                        msg["message"],
                        type_str,
                        file_path,
                        line_number,
                        min(caret_cols)
                    )

        # Linker/assembler/etc. diagnostics
        else:
            print(line)

    sys.exit(status)

if __name__ == "__main__":
    args = sys.argv[1:]
    args_str = " ".join(args)
    cmd = f'gcc -fdiagnostics-format=json {args_str}'
    format_gcc_output(cmd);

