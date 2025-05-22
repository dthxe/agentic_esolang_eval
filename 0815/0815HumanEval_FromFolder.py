# -*- coding: utf-8 -*-
"""
Modified version of 0815HumanEval.py that evaluates 0815 code from a folder
instead of generating it with an LLM.
"""

import os
import subprocess
import re
import ast
import jsonlines
from typing import Any, List, Tuple

# Define the path to the folder containing the 0815 code to evaluate
CODE_FOLDER = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                          "code_to_evaluate", "0815", "HumanEval")

# In a non-Jupyter environment, we would download the interpreter like this:
# interpreter_url = "https://gist.githubusercontent.com/perey/015aeea5c3af016531e9/raw/71b4cbfd16577e349d58a11eefd1cde12d40a2ae/esolang0815_interpreter.py"
# subprocess.run(["wget", "-O", "esolang0815_interpreter.py", interpreter_url], check=True)

# Path to your local 0815 interpreter
ESO_INTERPRETER_PATH = os.path.join(os.getcwd(), "esolang0815_interpreter.py")

documentation = """
¤0815

0815 - Language details

0815 is based around a queue and 3 registers. It understands hexadecimals only, so every numeric input and output are in hexadecimals. It also ignores everything that is not one of its instructions, for that matter: everything that is not an instruction is a comment.
Registers

0815 has 3 signed integers 64 bit wide registers: X, Y, and Z. All three are initialized with 0. X is a write only register and Z is a read only register. Y is a helper register and cannot be accessed by the programmer.
Parameters

Some of 0815 instructions need parameters. All parameters must be surrounded by colons, e.g. :3c:
Labels are also considered parameters; therefore they also need the surrounding colons.
If a parameter is needed but any is found the instruction will simply be ignored, no error message will be displayed.
Jumps

In 0815 you find 2 kinds of jumps: if Zero( # ) or if not Zero( ^ ). Jumps' labels can contain any character, except the language reserved symbols, e.g. :_loop: or :34:
If the label that the jump is pointed to is not found, the program terminates.
New lines

Either ASCII 10 or 13 will be interpreted as a new line.
Instructions

+-----------+---------+---------------------------------------------------------------------------+
|           |         |<:2: will move '2' to register X                                           |
|   move    |    <    |(parameter is mandatory)                                                   |
|           |         |                                                                           |
+-----------+---------+---------------------------------------------------------------------------+
|           |         |swaps register X and Y                                                     |
|   swap    |    x    |                                                                           |
|           |         |                                                                           |
+-----------+---------+---------------------------------------------------------------------------+
|           |         |}:_loop: this creates a label called '_loop'                               |
|   label   |    }    |(parameter is mandatory)                                                   |
|           |         |                                                                           |
+-----------+---------+---------------------------------------------------------------------------+
|   input   |         |inputs a signed 64 bit integer and stores it into X                        |
|   number  |    |    |(hexadecimal base)                                                         |
|           |         |                                                                           |
+-----------+---------+---------------------------------------------------------------------------+
|   input   |         |inputs an ASCII char and stores it into X                                  |
|   ASCII   |    !    |                                                                           |
|           |         |                                                                           |
+-----------+---------+---------------------------------------------------------------------------+
|   print   |         |prints a signed 64 bit integer stored in Z                                 |
|   number  |    %    |(hexadecimal base)                                                         |
|           |         |                                                                           |
+-----------+---------+---------------------------------------------------------------------------+
|   print   |         |prints an ASCII char stored in Z                                           |
|   ASCII   |    $    |                                                                           |
|           |         |                                                                           |
+-----------+---------+---------------------------------------------------------------------------+
|   roll    |         |rolls all registers to the left: X <- Y <- Z                               |
| registers |    ~    |after roll: X = Y, Y = Z and Z = X                                         |
|   left    |         |                                                                           |
+-----------+---------+---------------------------------------------------------------------------+
|   roll    |         |rolls all registers to the right: X -> Y -> Z                              |
| registers |    =    |after roll: X = Z, Y = X and Z = Y                                         |
|  right    |         |                                                                           |
+-----------+---------+---------------------------------------------------------------------------+
|   jump    |         |^:_loop: jumps to label _loop if Z is not 0                                |
|   if not  |    ^    |(parameter is mandatory)                                                   |
|   zero    |         |                                                                           |
+-----------+---------+---------------------------------------------------------------------------+
|   jump    |         |#:_loop: jumps to label _loop if Z is 0                                    |
|   if      |    #    |(parameter is mandatory)                                                   |
|   zero    |         |                                                                           |
+-----------+---------+---------------------------------------------------------------------------+
Queue instructions

+-----------+---------+---------------------------------------------------------------------------+
|           |         |clears the queue                                                           |
|  clear    |    ?    |                                                                           |
|           |         |                                                                           |
+-----------+---------+---------------------------------------------------------------------------+
|           |         |enqueue the number stored in Z                                             |
|  enqueue  |    >    |                                                                           |
|           |         |                                                                           |
+-----------+---------+---------------------------------------------------------------------------+
|           |         |dequeue a number and stores it into X                                      |
|  dequeue  |    {    |                                                                           |
|           |         |                                                                           |
+-----------+---------+---------------------------------------------------------------------------+
|   roll    |         |rolls the queue to the left: the first value becomes the last, the second  |
|   queue   |    @    |will be first and so on. If no parameter is found, it will roll the queue  |
|   left    |         |once, otherwise rolls it parameter times. e.g. @:a: rolls the queue ten    |
|           |         |times to the left.                                                         |
+-----------+---------+---------------------------------------------------------------------------+
|  roll     |         |the same as '@' just that the roll will go to the right:                   |
|  queue    |    &    |the last will be the first, the first will be the second and so on.        |
|  right    |         |                                                                           |
+-----------+---------+---------------------------------------------------------------------------+
Arithmetic instructions

+-----------+---------+---------------------------------------------------------------------------+
|           |         |Z = X + Y                                                                  |
|   add     |    +    |                                                                           |
|           |         |                                                                           |
+-----------+---------+---------------------------------------------------------------------------+
|           |         |Z = X - Y                                                                  |
|   sub     |    -    |                                                                           |
|           |         |                                                                           |
+-----------+---------+---------------------------------------------------------------------------+
|           |         |Z = X * Y                                                                  |
| multipl.  |    *    |                                                                           |
|           |         |                                                                           |
+-----------+---------+---------------------------------------------------------------------------+
|           |         |Z = X / Y                                                                  |
| division  |    /    |Y = rest                                                                   |
|           |         |                                                                           |
+-----------+---------+---------------------------------------------------------------------------+
Interpreter

I re-wrote my Brainfuck interpreter to run 0815 programs. This version just runs (interprets) 0815 programs.
Probably, I'll write another version that can interpret both languages, but for now, this will do.
There is another issue that I should mention: In this version, the Queue will only show its first 2070 items.
0815 Interpreter

0815 Programming examples

Hello World!
Cat
Odd or Even
Binary representation of an integer
Factorial sequence (0 - 14h)
Arithmetic mean(averages)
Fibonacci sequence (0 - a94fad42221f2702h)
99 bottles of beer (63h bottles of beer)
Prime numbers
Hailstone sequence
Simple randomizer
Sum of squares
Truth machine - numeric
Truth machine - ASCII

Home | Esolang

"""

# Program definitions
hello_world_program = """
<:48:x<:65:=<:6C:$=$=$$~<:03:+$~<:ffffffffffffffbd:+$<:ffffffffffffffb1:
+$<:57:~$~<:18:x+$~<:03:+$~<:06:x-$x<:0e:x-$=x<:43:x-$
"""

cat_program = """
}:_t:!~$^:_t:
"""

odd_even_program = """
}:s:|=<:2:x~#:e:=/~%~<:20:~$=<:73:x<:69:~$~$~<:20:~$=^:o:<:65:
x<:76:=$=$~$<:6E:~$<:a:~$^:s:}:o:<:6F:x<:64:x~$~$$<:a:~$^:s:
"""

binary_program = """
|~}:z:=x<:2:x/=>&~^:z:
<:ffffffffffffffff:~>}:s:{x
<:ffffffffffffffff:
-#:out:=%~^:s:
"""

factorial_program = """
<:1:~%<:d:~$~>~}:s:><:1:x{+>~{*%
<:21C3677C82B40000:=-#:end:~<:d:~$=^:s:
"""

arithmetic_program = """
<:01:~><:02:~><:03:~><:04:~><:05:~><:06:~><:07:~><:08:~><:09:~>
<:0a:~><:0b:~><:0c:~><:0d:~><:0e:~><:0f:~><:10:~><:11:~><:12:~>
<:13:~><:14:~><:15:~><:16:~><:17:~><:18:~><:19:~><:ffffffffffffffff:~>
{x{+>}:8f:{&={+>{~>&=x<:ffffffffffffffff:/#:8f:{{=<:19:x/%
"""

fibonacci_program = """
# %<:0D:>~$<:01:~%>=<:a94fad42221f2702:>~>}:_s:{x{={~$x+%{=>~>x~-x<:0D:~>~>~^:_s:?
"""

prime_program = """
<:2:~}:strt:>~}:net:<:1:x-~<:1:x-#:ok:x{=>=>=/=#:nP:{x
^:net:}:ok:{~%<:d:~$<:1:+^:strt:}:nP:{{x<:1:+^:strt:
"""

hailstone_program = """
|~}:s:%~<:1:-#:end:
<:d:~$~>{>x<:2:x/=
#:evn:{x<:3:*~<:1:+
^:s:}:evn:~{^:s:
"""

sum_of_squares_program = """
{x{*%<:d:~$<:1:~>><:2:~>><:3:~>><:4:~>><:5:~>><:6:~>><:7:
~>><:8:~>><:9:~>><:a:~>><:b:~>><:c:~>><:ffffffffffffffff:
~>{x{*>}:8f:{x{*&{=+>{~>&=x<:ffffffffffffffff:/#:8f:{{~%
"""

# Placeholder for 99bb.0815 program
program99 = """<:30:~><:39:~><:39:~><:20:~><:62:~><:6F:~><:74:~><:74:~><:6C:~><:65:~><:73:~><:20:~>
<:6F:~><:66:~><:20:~><:62:~><:65:~><:65:~><:72:~><:20:~><:6F:~><:6E:~><:20:~><:74:~><:68:~>
<:65:~><:20:~><:77:~><:61:~><:6C:~><:6C:~>"""

# Combine all programs into documentation
documentation += f"""
--- Hello World Program ---
{hello_world_program}

--- Cat Program ---
{cat_program}

--- Odd Even Program ---
{odd_even_program}

--- Binary Program ---
{binary_program}

--- Factorial Program ---
{factorial_program}

--- Arithmetic Program ---
{arithmetic_program}

--- Fibonacci Program ---
{fibonacci_program}

--- Prime Program ---
{prime_program}

--- Hailstone Program ---
{hailstone_program}

--- Sum of Squares Program ---
{sum_of_squares_program}

--- 99bb Program ---
{program99}
"""

# Initialize results list
results = []

# Load the problems from the JSONL file
problems = []
humaneval_path = "human-eval/data/HumanEval.jsonl"
if os.path.exists(humaneval_path):
    with jsonlines.open(humaneval_path) as f:
        for obj in f:
            problems.append(obj)
else:
    print(f"Warning: {humaneval_path} not found. Using a placeholder problem for testing.")
    # Add a placeholder problem for testing if the file doesn't exist
    problems = [{
        "task_id": "HumanEval_0",
        "prompt": "Return the sum of two numbers",
        "test": "assert candidate(2, 3) == 5\nassert candidate(5, 7) == 12"
    }]

# Function definitions for evaluation

def execute_0815_function(code: str, input_data: Any = "") -> str:
    """
    Executes 0815 code with the given input and returns the output or a concise error message.
    """
    try:
        if not os.path.isfile(ESO_INTERPRETER_PATH):
            return f"Error: 0815 interpreter not found at {ESO_INTERPRETER_PATH}."

        temp_eso_path = "temp.0815"
        with open(temp_eso_path, "w") as f:
            f.write(code)

        input_str = str(input_data)

        result = subprocess.run(
            ["python3", ESO_INTERPRETER_PATH, temp_eso_path],
            input=input_str,
            capture_output=True,
            text=True,
            timeout=5
        )

        if result.returncode != 0:
            error_message = result.stderr.strip().split('\n')[-1]
            return f"Error: {error_message}"

        return result.stdout.strip()

    except subprocess.TimeoutExpired:
        return "Error: Execution timed out."
    except Exception as e:
        return f"Error during execution: {str(e)}"

def extract_0815_code(generated_content: str) -> str:
    """
    Extracts the first 0815 code block from the generated content.
    Handles code blocks enclosed with ``` or ''' and marked as plaintext or 0815.
    If the closing delimiter is missing, captures until the end of the string.

    Args:
        generated_content (str): The content containing code blocks.

    Returns:
        str: The extracted 0815 code if found, else an empty string.
    """
    # Define a regex pattern that matches both ``` and ''' as delimiters
    # and captures code blocks marked as plaintext or 0815
    pattern = r"""
        (?P<delimiter>```|''')
        (?P<lang>plaintext|0815)?\s*\n?
        (?P<code>[\s\S]*?)(?:(?P=delimiter)|$)
    """

    regex = re.compile(pattern, re.VERBOSE | re.IGNORECASE)

    matches = regex.finditer(generated_content)

    for match in matches:
        lang = match.group('lang')
        code = match.group('code')
        if lang and lang.lower() in ['plaintext', '0815']:
            return code.strip()

    return ""


def parse_test_cases(test_str: str) -> List[Tuple[Any, Any]]:
    """
    Parses a string containing Python assert statements to extract test cases.
    Returns a list of tuples: (input_args, expected_output).
    """
    test_cases = []

    # Patterns for different assert types
    pattern_eq = re.compile(
        r'assert\s+candidate\((.*?)\)\s*==\s*('
        r'\[.*?\]|True|False|None|".*?"|\'.*?\'|[-+]?\d*\.\d+|\d+'
        r')',
        re.DOTALL
    )
    pattern_approx_eq = re.compile(
        r'assert\s+abs\s*\(\s*candidate\((.*?)\)\s*-\s*(.*?)\s*\)\s*<\s*('
        r'[-+]?\d*\.\d+|\d+'
        r')',
        re.DOTALL
    )

    # Extract direct equality test cases
    for args_str, expected_str in pattern_eq.findall(test_str):
        try:
            input_args = ast.literal_eval(args_str.strip())
            expected_output = ast.literal_eval(expected_str.strip())
            test_cases.append((input_args, expected_output))
        except Exception as e:
            print(f"Error parsing direct equality test case: {e}")

    # Extract approximate equality test cases
    for args_str, expected_str, tolerance_str in pattern_approx_eq.findall(test_str):
        try:
            input_args = ast.literal_eval(args_str.strip())
            expected_output = ast.literal_eval(expected_str.strip())
            test_cases.append((input_args, expected_output))
        except Exception as e:
            print(f"Error parsing approximate equality test case: {e}")

    return test_cases

##############################################################################
# Evaluation Loop

results = []

for idx, problem in enumerate(problems[:10]):
    print(f"Evaluating Problem {idx+1}/{len(problems[:10])}: {problem['task_id']}")

    try:
        # Construct the file path for this problem
        file_path = os.path.join(CODE_FOLDER, f"{problem['task_id']}.0815")

        # Check if the file exists
        if not os.path.exists(file_path):
            print(f"No code file found for problem {problem['task_id']}")
            results.append({
                "problem": problem["task_id"],
                "status": "Failed",
                "attempts": 0,
                "reason": "No code file found"
            })
            continue

        # Read the code from the file
        with open(file_path, 'r') as f:
            eso_code = f.read().strip()

        print(f"Reading 0815 code from file: {file_path}")
        print(f"Code: {eso_code}\n")

        if not eso_code:
            raise ValueError("Empty code file.")
            
        # Parse test cases
        parsed_test_cases = parse_test_cases(problem['test'])
        print(f"Parsed Test Cases: {parsed_test_cases}\n")

        # Initialize pass status
        all_pass = True
        failed_tests = []

        # Execute and evaluate each test case
        for test_idx, (inputs, expected) in enumerate(parsed_test_cases, start=1):
            output = execute_0815_function(eso_code, inputs)

            # Limit the output printed to prevent long error messages
            if output.startswith("Error:"):
                display_output = output  # Short error message
            else:
                display_output = output[:20] + "..." if len(output) > 20 else output  # Truncate long outputs

            print(f"Test {test_idx}: Input: {inputs}, Expected: {expected}, Output: {display_output}")

            pass_test = (str(expected) in output)
            if not pass_test:
                all_pass = False
                failed_tests.append({
                    "test_idx": test_idx,
                    "input": inputs,
                    "expected": expected,
                    "output": output
                })
            print(f"Pass: {pass_test}\n")

        if all_pass:
            print(f"Problem {problem['task_id']} passed all test cases.")
            results.append({
                "problem": problem["task_id"],
                "status": "Passed"
            })
        else:
            print(f"Problem {problem['task_id']} failed some test cases.")
            failed_test_descriptions = [
                f"Test {ft['test_idx']}: Expected {ft['expected']}, Got {ft['output']}"
                for ft in failed_tests
            ]
            results.append({
                "problem": problem["task_id"],
                "status": "Failed",
                "reason": f"Failed tests: {'; '.join(failed_test_descriptions)}"
            })

    except Exception as e:
        print(f"Error during evaluation: {e}")
        results.append({
            "problem": problem["task_id"],
            "status": "Failed",
            "reason": f"Error: {str(e)}"
        })

print("\nFinal Results:")
total_passed = 0
for res in results:
    status_info = f"Problem: {res['problem']}, Status: {res['status']}"
    if res['status'] == "Failed" and 'reason' in res:
        status_info += f", Reason: {res['reason']}"
    print(status_info)
    
    if res['status'] == "Passed":
        total_passed += 1

if results:
    print(f"Percentage passed: {100 * total_passed / len(results):.2f}%")
else:
    print("No problems were evaluated.")

print("\nNote: Make sure code files are placed in the following directory:")
print(CODE_FOLDER)
