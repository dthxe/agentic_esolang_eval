# -*- coding: utf-8 -*-
"""
Script for evaluating MiniPy code on general esoteric language tasks.
"""

import os
import subprocess
import tempfile
import re
import json
import ast
from typing import Any, Dict, List, Tuple

# Save the Minipy boilerplate as minipy.py if it doesn't exist
if not os.path.exists("minipy.py"):
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

# Save the interpreter as interpreter.py if it doesn't exist
if not os.path.exists("interpreter.py"):
    interpreter_code = "from minipy import *; x(f(v1))"
    with open("interpreter.py", "w") as f:
        f.write(interpreter_code)

# Path to the MiniPy interpreter
MINIPY_INTERPRETER_PATH = os.path.join(os.getcwd(), "interpreter.py")  # Path to the interpreter in the current directory

# Define the path to the folder containing the MiniPy code to evaluate
CODE_FOLDER = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                          "code_to_evaluate", "Minipy", "EsoEval")

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
        with tempfile.NamedTemporaryFile(mode="w+", suffix=".mp", delete=False) as temp_file:
            temp_minipy_path = temp_file.name
            temp_file.write(filtered_code)

        # Execute the Minipy code
        result = subprocess.run(
            ["python3", MINIPY_INTERPRETER_PATH, temp_minipy_path],
            input=input_data,
            capture_output=True,
            text=True,
            timeout=10  # Longer timeout for complex tasks
        )

        # Clean up the temporary file
        os.remove(temp_minipy_path)

        if result.returncode != 0:
            error_message = result.stderr.strip().split('\n')[-1] if result.stderr else "Unknown error"
            return f"Error: {error_message}"

        return result.stdout.strip()

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
        # Create a wrapper that calls the function with the arguments
        if isinstance(args, tuple) and len(args) > 0:
            # Multiple arguments
            args_str = ", ".join([repr(arg) for arg in args])
            wrapper_code = f"{minipy_code}\n\np({func_name}({args_str}))"
        else:
            # Single argument
            wrapper_code = f"{minipy_code}\n\np({func_name}({repr(args)}))"
        
        # Execute the wrapper code
        return execute_minipy_code(wrapper_code, input_data)
        
    except Exception as e:
        return f"Error: {str(e)}"

def extract_function_name_and_convert(minipy_code: str) -> str:
    """
    Extracts the name of the first function defined via 'def name(...)' from Minipy code.
    """
    match = re.search(r'def\s+([a-zA-Z0-9_]+)\s*\(', minipy_code)
    if match:
        return match.group(1)
    return None

def load_test_cases(task_name: str) -> List[Dict[str, Any]]:
    """
    Load test cases for a specific task.
    """
    # Define test cases for each task directly in the code
    test_cases_dict = {
        "hello_world": [
            {"input": "", "output": "Hello, world!"}
        ],
        "cat": [
            {"input": "hello", "output": "hello"},
            {"input": "Minipy", "output": "Minipy"},
            {"input": "123", "output": "123"}
        ],
        "reverse_cat": [
            {"input": "hello", "output": "olleh"},
            {"input": "Minipy", "output": "ypiniM"},
            {"input": "123", "output": "321"}
        ],
        "truth_machine": [
            {"input": "0", "output": "0"},
            {"input": "1", "output": "1111111"} # Should output infinite 1s, but we'll check for at least several 1s
        ],
        "fibonacci": [
            {"input": "5", "output": "0 1 1 2 3"},
            {"input": "8", "output": "0 1 1 2 3 5 8 13"}
        ],
        "factorial": [
            {"input": "5", "output": "120"},
            {"input": "0", "output": "1"},
            {"input": "10", "output": "3628800"}
        ],
        "quine": [
            # For a quine, the output should be the same as the input code
            # This is a special case that will be handled separately
            {"input": "", "output": ""}
        ],
        "rot13": [
            {"input": "hello", "output": "uryyb"},
            {"input": "HELLO", "output": "URYYB"},
            {"input": "Hello, World!", "output": "Uryyb, Jbeyq!"}
        ],
        "99_bottles": [
            # For 99 bottles, we'll just check for the first few lines
            {"input": "", "output": "99 bottles of beer on the wall"}
        ]
    }
    
    # Return the test cases for the specified task, or an empty list if not found
    return test_cases_dict.get(task_name, [])

def evaluate_task(task_name: str) -> Dict[str, Any]:
    """
    Evaluate Minipy code for a specific task against test cases.
    """
    # Load test cases
    test_cases = load_test_cases(task_name)
    if not test_cases:
        return {
            "task": task_name,
            "status": "Failed",
            "reason": "No test cases found"
        }
    
    # Construct the file path for this task
    file_path = os.path.join(CODE_FOLDER, f"{task_name}.mp")
    
    # Check if the file exists
    if not os.path.exists(file_path):
        print(f"No code file found for task {task_name}")
        return {
            "task": task_name,
            "status": "Failed",
            "reason": "No code file found"
        }
    
    # Read the code from the file
    try:
        with open(file_path, 'r') as f:
            minipy_code = f.read().strip()
        
        print(f"Reading Minipy code from file: {file_path}")
        print(f"Code: {minipy_code}\n")
        
        if not minipy_code:
            return {
                "task": task_name,
                "status": "Failed",
                "reason": "Empty code file"
            }
        
        # Extract function name
        func_name = extract_function_name_and_convert(minipy_code)
        if func_name:
            print(f"Detected function definition: {func_name}")
        else:
            func_name = "f"  # Default function name in Minipy
            print("Defaulting to function name 'f'.")
        
        # Initialize pass status
        all_pass = True
        failed_tests = []
        python_pass_tests = []
        
        # Execute and evaluate each test case
        for test_idx, test_case in enumerate(test_cases, start=1):
            input_data = test_case.get("input", "")
            expected_output = test_case.get("output", "")
            
            # For hello_world and similar tasks that don't require input,
            # we need to call the function without arguments
            if not input_data:
                # Create a wrapper that calls the function without arguments
                wrapper_code = f"{minipy_code}\n\np({func_name}())"
                output = execute_minipy_code(wrapper_code, "")
            else:
                # For tasks that require input, pass it to the function
                output = test_minipy_function(minipy_code, func_name, input_data)
            
            # Limit the output printed to prevent long error messages
            if output.startswith("Error:"):
                display_output = output  # Short error message
            else:
                display_output = output[:50] + "..." if len(output) > 50 else output  # Truncate long outputs
            
            print(f"Test {test_idx}: Input: {input_data}, Expected: {expected_output}, Output: {display_output}")
            
            # Check if the output contains the expected output
            # In Minipy, the output might include additional formatting
            pass_test = (expected_output in output)
            if not pass_test:
                all_pass = False
                failed_tests.append({
                    "test_idx": test_idx,
                    "input": input_data,
                    "expected": expected_output,
                    "output": output
                })
            print(f"Pass: {pass_test}\n")
            
            # Check if the code is valid Python (it shouldn't be for true esoteric code)
            try:
                # Try to execute the code as Python
                with tempfile.NamedTemporaryFile(mode="w+", suffix=".py", delete=False) as temp_file:
                    temp_py_path = temp_file.name
                    temp_file.write(minipy_code)
                
                result = subprocess.run(
                    ["python3", temp_py_path],
                    input=input_data if isinstance(input_data, str) else "",
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                
                os.remove(temp_py_path)
                
                if result.returncode == 0:
                    python_pass_tests.append(test_idx)
            except:
                # If it fails, that's good - it means it's truly esoteric
                pass
        
        # Check if the code is valid Python (it shouldn't be for true esoteric code)
        python_executable = len(python_pass_tests) > 0
        
        if all_pass:
            print(f"Task {task_name} passed all test cases.")
            print(f"Python executable: {python_executable}")
            return {
                "task": task_name,
                "status": "Passed",
                "tests_passed": len(test_cases),
                "tests_total": len(test_cases),
                "python_executable": python_executable
            }
        else:
            failure_message = f"Failed {len(failed_tests)} test cases out of {len(test_cases)}"
            print(f"Task {task_name} {failure_message}")
            print(f"Python executable: {python_executable}")
            
            # Print details of failed tests
            for failed_test in failed_tests:
                print(f"  Test {failed_test['test_idx']} failed:")
                print(f"    Input: {failed_test['input']}")
                print(f"    Expected: {failed_test['expected']}")
                print(f"    Got: {failed_test['output']}")
            
            return {
                "task": task_name,
                "status": "Failed",
                "tests_passed": len(test_cases) - len(failed_tests),
                "tests_total": len(test_cases),
                "reason": failure_message,
                "python_executable": python_executable
            }
    
    except Exception as e:
        print(f"Error during evaluation: {e}")
        return {
            "task": task_name,
            "status": "Failed",
            "reason": f"Error: {str(e)}"
        }

problems = [
    {
        'task_id': "1",
        'prompt': 'print hello world',
        'tests': ["", "Hello, World!"]
    },
    {
        'task_id': "2",
        'prompt': 'given a number n input, return the nth factorial number',
        'tests': ["5", "120"]
    },
    {
        'task_id': "3",
        'prompt': 'given a number n, return "Even" if n is even, else "Odd"',
        'tests': ["4", "Even"]
    },
    {
        'task_id': "4",
        'prompt': 'given two numbers a and b, return their sum',
        'tests': ["2\n3", "5"]
    },
    {
        'task_id': "5",
        'prompt': 'given a number n, return True if it is prime, else False',
        'tests': ["11", "True"]
    },
    {
        'task_id': "6",
        'prompt': 'given a string s, return the reversed string',
        'tests': ["hello", "olleh"]
    },
    {
        'task_id': "7",
        'prompt': 'print "Hello, Minipy!"',
        'tests': ["", "Hello, Minipy!"]
    },
    {
        'task_id': "8",
        'prompt': 'given two numbers a and b, return their product',
        'tests': ["2\n3", "6"]
    },
    {
        'task_id': "9",
        'prompt': 'given a number n, return True if it is positive, else False',
        'tests': ["10", "True"]
    },
    {
        'task_id': "10",
        'prompt': 'given two strings s1 and s2, return their concatenation',
        'tests': ["foo\nbar", "foobar"]
    },
    {
        'task_id': "11",
        'prompt': 'given a number n, return its square',
        'tests': ["4", "16"]
    },
    {
        'task_id': "12",
        'prompt': 'given a string s, return the number of characters in the string',
        'tests': ["hello", "5"]
    },
    {
        'task_id': "13",
        'prompt': 'given two numbers a and b, return the smaller number',
        'tests': ["3\n7", "3"]
    },
    {
        'task_id': "14",
        'prompt': 'given a string s, return True if all characters in the string are vowels, else False',
        'tests': ["aeiou", "True"]
    },
    {
        'task_id': "15",
        'prompt': 'given two numbers a and b, return the absolute difference between them',
        'tests': ["7\n3", "4"]
    },
    {
        'task_id': "16",
        'prompt': 'given a string s and a number n, return the string repeated n times',
        'tests': ["abc\n3", "abcabcabc"]
    },
    {
        'task_id': "17",
        'prompt': 'given a number n, return the Fibonacci sequence up to the nth term',
        'tests': ["5", "0 1 1 2 3"]
    },
    {
        'task_id': "18",
        'prompt': 'given a list of numbers, return the maximum number',
        'tests': ["3 1 4 1 5 9", "9"]
    },
    {
        'task_id': "19",
        'prompt': 'given a string s, return True if it is a palindrome, else False',
        'tests': ["racecar", "True"]
    },
    {
        'task_id': "20",
        'prompt': 'given two numbers a and b, return their greatest common divisor',
        'tests': ["8\n12", "4"]
    },
    {
        'task_id': "21",
        'prompt': 'given a list of numbers, return the list sorted in ascending order',
        'tests': ["4 2 5 1", "1 2 4 5"]
    },
    {
        'task_id': "22",
        'prompt': 'given a number n, return True if it is a perfect square, else False',
        'tests': ["16", "True"]
    },
    {
        'task_id': "23",
        'prompt': 'given a string s, return the number of vowels in the string',
        'tests': ["hello", "2"]
    },
    {
        'task_id': "24",
        'prompt': 'given a list of numbers, return the sum of all numbers in the list',
        'tests': ["1 2 3 4", "10"]
    },
    {
        'task_id': "25",
        'prompt': 'given a number n, return its binary representation as a string',
        'tests': ["10", "1010"]
    },
    {
        'task_id': "26",
        'prompt': 'given two strings s1 and s2, return True if s1 is an anagram of s2, else False',
        'tests': ["listen\nsilent", "True"]
    },
    {
        'task_id': "27",
        'prompt': 'given a number n, return the sum of digits in n',
        'tests': ["1234", "10"]
    },
    {
        'task_id': "28",
        'prompt': 'given a list of numbers, return True if all numbers are even, else False',
        'tests': ["2 4 6 8", "True"]
    },
    {
        'task_id': "29",
        'prompt': 'given a string s, return the string in title case',
        'tests': ["hello world", "Hello World"]
    },
    {
        'task_id': "30",
        'prompt': 'given two numbers a and b, return True if a is divisible by b, else False',
        'tests': ["10\n2", "True"]
    }
]


def main():
    """
    Main function to evaluate all tasks.
    """
    results = []
    
    # Evaluate the problems
    for problem in problems:  # Limit to first 10 for testing
        task_id = problem['task_id']
        prompt = problem['prompt']
        input_data = problem['tests'][0]
        expected_output = problem['tests'][1]
        
        print(f"\n{'='*50}")
        print(f"Evaluating problem {task_id}: {prompt}")
        print(f"Input: {input_data}, Expected Output: {expected_output}")
        print(f"{'='*50}\n")
        
        # Construct test case in the format expected by evaluate_task
        test_case = [{
            "input": input_data,
            "output": expected_output
        }]
        
        # Create a temporary function to override load_test_cases for this specific problem
        original_load_test_cases = load_test_cases
        
        def temp_load_test_cases(task_name):
            return test_case
        
        # Replace the function temporarily
        globals()['load_test_cases'] = temp_load_test_cases
        
        # Evaluate the task using the task_id as the filename
        result = evaluate_task(task_id)
        result['prompt'] = prompt  # Add the prompt to the result
        results.append(result)
        
        # Restore the original function
        globals()['load_test_cases'] = original_load_test_cases

    
    # Print summary
    print("\n\nFinal Results:")
    print(f"{'='*50}")
    
    total_passed = 0
    total_true_esoteric = 0  # Count of passed tests that are not valid Python
    
    for res in results:
        if 'prompt' in res:
            status_info = f"Problem {res['task']}: {res.get('prompt', '')}, Status: {res['status']}"
        else:
            status_info = f"Task: {res['task']}, Status: {res['status']}"
            
        if res['status'] == "Passed":
            total_passed += 1
            status_info += f", Tests Passed: {res.get('tests_passed', 'N/A')}/{res.get('tests_total', 'N/A')}"
            
            # Check if the code is not executable by standard Python
            if res.get('python_executable', True) == False:
                total_true_esoteric += 1
                status_info += ", True Esoteric: Yes"
            else:
                status_info += ", True Esoteric: No"
        else:
            status_info += f", Reason: {res.get('reason', 'Unknown')}"
        print(status_info)
    
    if results:
        print(f"\nPercentage passed: {100 * total_passed / len(results):.2f}%")
        print(f"Percentage of true esoteric solutions (passed but not valid Python): {100 * total_true_esoteric / len(results):.2f}%")
    else:
        print("No tasks were evaluated.")
    
    print(f"\nCode files were read from: {CODE_FOLDER}")
    print("Test cases are defined directly in the script.")

if __name__ == "__main__":
    main()
