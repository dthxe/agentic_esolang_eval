# -*- coding: utf-8 -*-
"""
Modified version of MiniPyHumanEval.py that evaluates Minipy code from a folder
instead of generating it with an LLM.
"""

# Save the Minipy boilerplate as minipy.py
minipy_code = """
import sys as y
av = y.argv
if len(av) > 1:
    v1 = av[1]
    try:
        v2 = eval(v1)
    except SyntaxError: pass
import os
import re
import functools as ft
import string as st
import copy as cp
import random as rd
import math as m
ri = rd.randint
rt = lambda seq: seq[ri(0, len(seq)-1)]
N = None
_i = __import__
_b = __builtins__
_B = dir(_b)
ab = abs
al = all
an = any
bn = bin
c = chr
cx = complex
d = dict
dr = dir
em = enumerate
e = eval
x = exec
b = lambda x: lambda y: eval(x)
fm = lambda x,y: map(b(x),y)
ff = lambda x,y: filter(b(x),y)
fr = ft.reduce
fl = float
gtat = getattr
hsat = hasattr
dlat = delattr
stat = setattr
hx = hex
i = input
n = lambda *args: eval(input(*args))
sr = ""
t = int
l = len
ls = list
ot = oct
o = open
f = lambda s: o(s).read()
p = print
r = range
rp = repr
rvr = reversed
rnd = round
srt = sorted
s = str
sm = sum
v = vars
z = zip
def rf(s): # regex finder
    index = s.index("!")
    regex = re.compile(s[:index])
    search = s[index + 1 :]
    if search[0] == "!":
        return regex.findall(search[1:])
    else:
        return regex.findall(eval(search))
q = chr(34)
k = "\\n"

def e(s):
    raise RuntimeError(s)
"""
with open("minipy.py", "w") as f:
    f.write(minipy_code)

# Save the interpreter as interpreter.py
interpreter_code = "from minipy import *; x(f(v1))"
with open("interpreter.py", "w") as f:
    f.write(interpreter_code)

print("Minipy and interpreter setup complete!")

import os
import subprocess
import tempfile
import re
import ast

# Define the path to the folder containing the Minipy code to evaluate
CODE_FOLDER = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                          "code_to_evaluate", "Minipy")

results = []

# Prompt engineered prompt
def mod_prompt(prompt):
   modified_prompt = (
        f"Write a function in minipy, an esoteric programming language. Again not python but use the shortcuts in the documentation to shorten the code. In addition, make your functions use return and not print"
        f"The function should perform the following: {prompt}"
        f"The documentation for minipy is provided here: '{minipy_code}'. "

    )
   return modified_prompt

def execute_py_code(code: str, input_data: str = "") -> str:
    """
    Executes Python code and returns the output.
    """
    try:
        # Create a temporary file to hold the Python code
        with tempfile.NamedTemporaryFile(mode="w+", suffix=".py", delete=False) as temp_py:
            temp_py_path = temp_py.name
            temp_py.write(code)

        try:
            # Execute the Python code
            result = subprocess.run(
                ['python3', temp_py_path],
                input=input_data,
                capture_output=True,
                text=True,
                timeout=5  # Adjust the timeout as needed
            )

            # Check for errors during execution
            if result.returncode != 0:
                return f"Error: {result.stderr.strip()}"

            # Return the standard output from the script
            return result.stdout.strip()

        finally:
            # Clean up the temporary file
            os.remove(temp_py_path)

    except subprocess.TimeoutExpired:
        return "Error: Execution timed out."
    except Exception as e:
        return f"Error during execution: {str(e)}"

def test_py_function(py_code: str, func_name: str, args: list, input_data: str = "") -> str:
    """
    Extracts function definitions from Python code, handles lambda and def functions,
    calls the specified function with arguments, executes the combined code, and returns the output.
    """
    try:
        # Check for traditional function definitions
        pattern_def = rf"def\s+{re.escape(func_name)}\s*\((.*?)\):\s*(.*?)\n(?=def\s|\Z)"
        match_def = re.search(pattern_def, py_code, re.DOTALL)

        # Check for lambda functions
        pattern_lambda = rf"{re.escape(func_name)}\s*=\s*lambda\s*(.*?):(.*)"
        match_lambda = re.search(pattern_lambda, py_code, re.DOTALL)

        extracted_functions = ""

        if match_def:
            # If a traditional function is found, extract it
            args_str, body = match_def.groups()
            body_lines = body.strip().split('\n')
            indented_body = '\n'.join([f"    {line}" for line in body_lines])
            extracted_functions += f"def {func_name}({args_str}):\n{indented_body}\n\n"
        elif match_lambda:
            # If a lambda function is found, convert it to a def function
            args_str, body = match_lambda.groups()
            extracted_functions += f"def {func_name}({args_str.strip()}):\n    return {body.strip()}\n\n"
        else:
            return f"Error: Function '{func_name}' not found in the provided code."

        # Prepare the function call
        args_str = ', '.join(map(str, args))
        function_call = f"print({func_name}({args_str}))\n"

        # Combine the extracted function(s) with the function call
        combined_code = extracted_functions + function_call

        # Execute the combined code
        output = execute_py_code(combined_code, input_data)

        return output

    except Exception as e:
        return f"Error during testing: {str(e)}"

# In a non-Jupyter environment, we would download and extract the human-eval dataset like this:
# subprocess.run(["git", "clone", "https://github.com/openai/human-eval.git"], check=True)
# subprocess.run(["gunzip", "human-eval/data/HumanEval.jsonl.gz"], check=True)

# In a non-Jupyter environment, we would install dependencies like this:
# subprocess.run(["pip", "install", "transformers", "torch", "jsonlines"], check=True)
import jsonlines

problems = []

# Load the problems from the JSONL file
with jsonlines.open("data/HumanEval.jsonl") as f:
    for obj in f:
        problems.append(obj)

import os
import subprocess
import tempfile
import re
import ast
from typing import List, Tuple, Any

##############################################################################

MINIPY_INTERPRETER_PATH = os.path.join(os.getcwd(), "interpreter.py")  # Path to the interpreter in the current directory

def execute_minipy_code(code: str, input_data: str = "") -> str:
    """
    Executes Minipy code and returns the output, or an error message.
    Ignores lines that begin with # comments.
    """
    try:
        if not os.path.isfile(MINIPY_INTERPRETER_PATH):
            return f"Error: Minipy interpreter not found at {MINIPY_INTERPRETER_PATH}."
            
        # Filter out lines that begin with # comments
        filtered_code_lines = [line for line in code.split('\n') if not line.strip().startswith('#')]
        filtered_code = '\n'.join(filtered_code_lines)

        # Create a temporary file for the Minipy code
        with tempfile.NamedTemporaryFile(mode="w+", suffix=".minipy", delete=False) as temp_minipy:
            temp_minipy_path = temp_minipy.name
            temp_minipy.write(filtered_code)

        try:
            # Execute the Minipy code using the interpreter
            result = subprocess.run(
                ['python3', MINIPY_INTERPRETER_PATH, temp_minipy_path],
                input=input_data,
                capture_output=True,
                text=True,
                timeout=5  # Adjust as needed
            )

            # Check for errors during execution
            if result.returncode != 0:
                return f"Error: {result.stderr.strip()}"

            # Return the standard output
            return result.stdout.strip()
        finally:
            # Clean up the temp file
            os.remove(temp_minipy_path)

    except subprocess.TimeoutExpired:
        return "Error: Execution timed out."
    except Exception as e:
        return f"Error during execution: {str(e)}"


def test_minipy_function(minipy_code: str, func_name: str, args: Any, input_data: str = "") -> str:
    """
    Executes the specified function in the provided Minipy code with the given arguments.
    'args' can be a single value or a tuple/list of values.
    """
    try:
        # Determine if we have multiple arguments (tuple) or a single argument
        if isinstance(args, tuple):
            # Multiple arguments
            formatted_args = []
            for arg in args:
                if isinstance(arg, str):
                    # Enclose string arguments in quotes
                    formatted_args.append(f'"{arg}"')
                else:
                    # Use repr for other types to ensure correct formatting
                    formatted_args.append(repr(arg))
            args_str = ', '.join(formatted_args)
        else:
            # Single argument
            if isinstance(args, str):
                args_str = f'"{args}"'
            else:
                args_str = repr(args)

        # Create the function call string
        function_call = f"print({func_name}({args_str}))"

        # Combine with the user’s Minipy code
        combined_code = f"{minipy_code.strip()}\n\n{function_call}"

        # Execute the combined code
        output = execute_minipy_code(combined_code, input_data)
        return output
    except Exception as e:
        return f"Error during testing: {str(e)}"



def parse_test_cases(test_str: str) -> List[Tuple[Any, Any]]:
    """
    Parses a string containing Python asserts of the form:
        assert candidate(...) == <expected>
    or
        assert abs(candidate(...) - <expected>) < <tolerance>
    Returns a list of (input_args, expected_value).
    """
    test_cases = []

    # Pattern for parsing from assert candidate(...) check function in
    # human eval test cases
    pattern_eq = re.compile(
        r'assert\s+candidate\((.*?)\)\s*==\s*('
        r'\[.*?\]'         # lists
        r'|True|False'     # bool
        r'|None'           # None
        r'|".*?"'          # double-quoted
        r'|\'.*?\''        # single-quoted
        r'|[-+]?\d*\.\d+|\d+'  # int/float
        r')',
        re.DOTALL
    )

    # Pattern for approximate equality from
    # assert abs(candidate(...) - something) < tolerance check function in
    # human eval test cases
    pattern_approx_eq = re.compile(
        r'assert\s+abs\s*\(\s*candidate\((.*?)\)\s*-\s*(.*?)\s*\)\s*<\s*('
        r'[-+]?\d*\.\d+|\d+'  # Tolerance
        r')',
        re.DOTALL
    )

    matches_eq = pattern_eq.findall(test_str)
    for idx, (args_str, expected_str) in enumerate(matches_eq, 1):
        try:
            # Clean up
            args_str_clean = args_str.strip()
            expected_str_clean = expected_str.strip()

            # ast.literal_eval can parse it as a proper string.
            input_args = ast.literal_eval(args_str_clean)

            # Safely evaluate expected
            expected_output = ast.literal_eval(expected_str_clean)

            test_cases.append((input_args, expected_output))
        except Exception as e:
            print(f"Error parsing direct equality test case {idx}: {e}")
            continue

    matches_approx_eq = pattern_approx_eq.findall(test_str)
    for idx, (args_str, expected_str, tolerance_str) in enumerate(matches_approx_eq, 1):
        try:
            args_str_clean = args_str.strip()
            expected_str_clean = expected_str.strip()
            tolerance = float(tolerance_str.strip())

            input_args = ast.literal_eval(args_str_clean)
            expected_output = ast.literal_eval(expected_str_clean)
            test_cases.append((input_args, expected_output))
        except Exception as e:
            print(f"Error parsing approximate equality test case {idx}: {e}")
            continue

    return test_cases


def extract_function_name_and_convert(minipy_code: str) -> str:
    """
    Extracts the name of the first function defined via 'def name(...)' from Minipy code.
    """
    pattern = r"def\s+(\w+)\s*\("
    match = re.search(pattern, minipy_code)
    if match:
        return match.group(1)
    return ""


def extract_minipy_code(generated_content: str) -> str:
    """
    Extracts the Minipy code block from triple-backtick fences. If no closing
    fence is found, will return everything after ```minipy.
    """
    # Regex for normal labeled 'minipy'
    code_pattern = r"```minipy\s*\n([\s\S]*?)```"
    match = re.search(code_pattern, generated_content)
    if match:
        return match.group(1).strip()

    # regex if no forgot the closing backticks
    incomplete_pattern = r"```minipy\s*\n([\s\S]*)"
    incomplete_match = re.search(incomplete_pattern, generated_content)
    if incomplete_match:
        return incomplete_match.group(1).strip()

    # regex for any triple-backtick code block
    fallback_pattern = r"```\s*\n([\s\S]*?)```"
    fallback_match = re.search(fallback_pattern, generated_content)
    if fallback_match:
        return fallback_match.group(1).strip()

    # No block found
    return "Error: No valid Minipy code block found."

results = []
for idx, problem in enumerate(problems[:30]):  # subset of 30 problems
    print(f"Evaluating Problem {idx+1}/{len(problems)}: {problem['task_id']}")
    try:
        # Construct the file path for this problem
        file_path = os.path.join(CODE_FOLDER, f"{problem['task_id']}.minipy")
        
        # Check if the file exists
        if not os.path.exists(file_path):
            print(f"No code file found for problem {problem['task_id']}")
            results.append({
                'problem': problem['task_id'],
                'test_case': 'N/A',
                'input': 'N/A',
                'expected': 'N/A',
                'output': 'No code file found',
                'pass': False,
                'pythonpass': False
            })
            continue
            
        # Read the code from the file
        with open(file_path, 'r') as f:
            minipy_code = f.read().strip()
            
        print(f"Reading Minipy code from file: {file_path}")
        print(f"Code: {minipy_code}\n")

        # Extract function name
        func_name = extract_function_name_and_convert(minipy_code)
        if func_name:
            print(f"Detected function definition: {func_name}")
        else:
            func_name = "f"  # Default function name
            print("Defaulting to function name 'f'.")

        # Execute each test case
        all_passed = True
        print(parse_test_cases(problem['test']))
        parsed_test_cases = parse_test_cases(problem['test'])
        all_pass = True
        # runs through the test cases
        for test_idx, (inputs, expected) in enumerate(parsed_test_cases, start=1):
          print(f"Running Test Case {test_idx}: {func_name}({repr(inputs)}) == {repr(expected)}")
          output = test_minipy_function(minipy_code, func_name, inputs)
          print(f"Minipy Output: {output}")

          # Compare strings directly
          pass_test = (str(expected) == output)
          if not pass_test:
            all_pass = False
          print(f"Pass: {pass_test}\n")

        # sees if it's runnable via standard python interpreter and not minipy
        python_pass = False
        try:
          test_py_function(minipy_code, func_name, inputs)
        except Exception as e:
          python_pass = True
        results.append({
                'problem': problem['task_id'],
                'test_case': test_idx,
                'input': inputs,
                'expected': expected,
                'output': output,
                'pass': all_pass,
                'pythonpass': python_pass
            })

    except Exception as e:
        print(f"Error during evaluation: {e}")
        results.append({
            'problem': problem['task_id'],
            'test_case': 'N/A',
            'input': 'N/A',
            'expected': 'N/A',
            'output': f"Error: {e}",
            'pass': False
        })



# results of both passing with minipy interpreter and passing with minipy interpreter & not python.

passed = 0
nonexecut = 0
for result in results:
    print(f"Problem {result['problem']}:")
    print(f"Pass: {result['pass']}")
    print(f"Non executable via python interpretor: {result['pythonpass']}")
    if result['pass']:
      passed += 1
    if result['pass'] and result['pythonpass']:
      nonexecut += 1

print(f"Passed: {passed}/{len(results)}")
print(f"Passed + not executable by pthon: {nonexecut}/{len(results)}")

print(f"\nCode files were read from: {CODE_FOLDER}")
