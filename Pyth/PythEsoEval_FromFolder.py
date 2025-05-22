# -*- coding: utf-8 -*-
"""
Modified version of PythEsoEval.py that evaluates Pyth code from a folder
instead of generating it with an LLM.
"""

import os
import re
import ast
import subprocess
from typing import List

# Define the path to the folder containing the Pyth code to evaluate
CODE_FOLDER = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                          "code_to_evaluate", "Pyth")

# Uncomment the line below and replace 'your-api-key' with your actual API key
os.environ["OPENAI_API_KEY"] = 'your-api-key'


def parse_test_cases(test_str: str):
    """
    Parses the test string to extract input arguments and expected outputs.

    """
    test_cases = []
    pattern = r'assert\s+candidate\((.*?)\)\s*==\s*(.+)'

    matches = re.findall(pattern, test_str, re.DOTALL)

    for idx, (args_str, expected_str) in enumerate(matches, 1):
        try:
            # Clean up the expected_str by removing newlines and extra spaces
            expected_str = re.sub(r"\s+", " ", expected_str.strip())
            # Safely evaluate the expected output
            expected_output = ast.literal_eval(expected_str)

            # Wrap the args_str in parentheses to form a tuple for evaluation
            args_tuple = ast.literal_eval(f'({args_str})')

            # If only one argument
            if isinstance(args_tuple, tuple) and len(args_tuple) == 1:
                input_args = args_tuple[0]
            else:
                input_args = args_tuple
            test_cases.append((input_args, expected_output))
        except Exception as e:
            print(f"Error parsing test case {idx}: {e}")
            continue
    return test_cases

def extract_pyth_code(generated_content: str) -> list:

    pattern = r"```pyth\s+([\s\S]*?)```"
    pyth_codes = re.findall(pattern, generated_content, re.MULTILINE)
    print(pyth_codes)
    return pyth_codes[0] if type(pyth_codes) == list else pyth_codes

def evaluate_code(code: str, test_str: str) -> bool:

    test_cases = parse_test_cases(test_str)
    if not test_cases:
        print("No valid test cases found.")
        return False

    print(test_cases)
    for idx, (input_args, expected_output) in enumerate(test_cases, 1):

        # Execute the Pyth code with the input_data
        output = execute_pyth_code(extract_pyth_code(code), f"{input_args}")

        # Convert the output to a float for comparison
        import ast

        try:
            output_value = ast.literal_eval(output)
        except Exception as e:
            print(f"Test Case {idx}: Invalid output format. Output: '{output}'")
            return False

        # Compare the output with the expected output
        if output_value != expected_output:
            print(f"Test Case {idx}: Failed")
            print(f"Input: {input_args}")
            print(f"Expected Output: {expected_output}, Got: {output_value}\n")
            return False
        else:
            print(f"Test Case {idx}: Passed")


    return True

def execute_pyth_code(code: str, input_data: str = "") -> str:
    """
    Executes Pyth code and returns the output.
    """
    try:
        # Define paths
        temp_pyth_path = "temp.pyth"  # Adjust path as needed
        pyth_interpreter = "/content/pyth/pyth.py"  # Ensure this path is correct

        # Ensure the Pyth interpreter exists
        if not os.path.isfile(pyth_interpreter):
            return f"Error: Pyth interpreter not found at {pyth_interpreter}."

        # Write the Pyth code to a temporary file
        with open(temp_pyth_path, "w") as f:
            f.write(code)

        # Execute the Pyth code using the Pyth interpreter
        result = subprocess.run(
            ['python3', pyth_interpreter, temp_pyth_path],
            input=input_data,
            capture_output=True,
            text=True,
            timeout=5
        )

        # Check for errors
        if result.returncode != 0:
            return f"Error: {result.stderr.strip()}"

        # Return the standard output
        return result.stdout.strip()

    except subprocess.TimeoutExpired:
        return "Error: Execution timed out."
    except Exception as e:
        return f"Error during execution: {str(e)}"

# Define the extract_pyth_code function
def extract_pyth_code(generated_content: str) -> str:
    pattern = r"```pyth\s+([\s\S]*?)```"
    pyth_codes = re.findall(pattern, generated_content, re.MULTILINE)
    print("Extracted Pyth Codes:", pyth_codes)
    return pyth_codes[0].strip() if pyth_codes else ""

# Initialize results
results = []

def mod_prompt(prompt):
   modified_prompt = (
        f"Write a function in Pyth, an esoteric programming language. "
        f"The function should perform the following: {prompt}"
        f"The documentation for Pyth is provided here: '{text_content}'. "

    )
   return modified_prompt

problems = [
    {
        'task_id': "1",
        'prompt': mod_prompt('print hello world'),
        "tests": ["", 'Hello world']
    },
    {
        'task_id': "2",
        'prompt': mod_prompt('given a number n input, return the nth factorial number'),
        "tests": ["5", "120"]
    },
    {
        'task_id': "3",
        'prompt': mod_prompt('given a number n, return "Even" if n is even, else "Odd"'),
        "tests": ["4", '"Even"']
    },
    {
        'task_id': "4",
        'prompt': mod_prompt('given two numbers a and b, return their sum'),
        "tests": ["2 \n 3", "5"]
    },
    {
        'task_id': "5",
        'prompt': mod_prompt('given a number n, return True if it is prime, else False'),
        "tests": ["11", "True"]
    },
    {
        'task_id': "6",
        'prompt': mod_prompt('given a string s, return the reversed string'),
        "tests": ["hello", '"olleh"']
    },
     {
        'task_id': "7",
        'prompt': mod_prompt('print "Hello, Pyth!"'),
        "tests": ["", '"Hello, Pyth!"']
    },
    {
        'task_id': "8",
        'prompt': mod_prompt('given two numbers a and b, return their product'),
        "tests": ["2 \n 3", "6"]
    },
    {
        'task_id': "9",
        'prompt': mod_prompt('given a number n, return True if it is positive, else False'),
        "tests": ["10", "True"]
    },
    {
        'task_id': "10",
        'prompt': mod_prompt('given two strings s1 and s2, return their concatenation'),
        "tests": ['"foo", "bar"', '"foobar"']
    },
    {
        'task_id': "11",
        'prompt': mod_prompt('given a number n, return its square'),
        "tests": ["4", "16"]
    },
    {
        'task_id': "12",
        'prompt': mod_prompt('given a string s, return the number of characters in the string'),
        "tests": ['"hello"', "5"]
    },
    {
        'task_id': "13",
        'prompt': mod_prompt('given two numbers a and b, return the smaller number'),
        "tests": ["3 \n 7", "3"]
    },
    {
        'task_id': "14",
        'prompt': mod_prompt('given a string s, return True if all characters in the string are vowels, else False'),
        "tests": ['"aeiou"', "True"]
    },
    {
        'task_id': "15",
        'prompt': mod_prompt('given two numbers a and b, return the absolute difference between them'),
        "tests": ["7 \n 3", "4"]
    },
    {
        'task_id': "16",
        'prompt': mod_prompt('given a string s and a number n, return the string repeated n times'),
        "tests": ['"abc", 3', '"abcabcabc"']
    }
]

import os
import subprocess
import re

passed = 0
results = []
for idx, problem in enumerate(problems):  # Adjust the range as needed
    print(f"Evaluating Problem {idx+1}/{len(problems)}: {problem['task_id']}")

    try:
        # Construct the file path for this problem
        file_path = os.path.join(CODE_FOLDER, f"{problem['task_id']}.pyth")
        
        # Check if the file exists
        if not os.path.exists(file_path):
            print(f"No code file found for problem {problem['task_id']}")
            results.append({
                'problem': problem['task_id'],
                'pass': False,
                'code': '',
                'output': 'No code file found'
            })
            continue
            
        # Read the code from the file
        with open(file_path, 'r') as f:
            pyth_code = f.read().strip()
            
        print(f"Reading Pyth code from file: {file_path}")
        print(f"Code: {pyth_code}")

        # Execute the Pyth code
        output = execute_pyth_code(pyth_code, problem['tests'][0])
        print(f"Pyth Output: {output}\n")
        print("Pass", problem['tests'][1].upper() in output.upper(), "type", type(output))
        # Record the result
        results.append({'problem': problem['task_id'],'pass': problem['tests'][1] in output, 'code': pyth_code, 'output': output})

    except Exception as e:
        print(f"Error during file processing: {e}")
        results.append({
            'problem': problem['task_id'],
            'pass': False,
            'code': '',
            'output': f"Error: {str(e)}"
        })

# Summarize the results



print("\nSummary of Results:")
totalpassed = 0
for result in results:
    if result['pass'] == True:
         totalpassed += 1
    # print(f"Problem {result['problem']}:")
    # print(f"Pyth Code:\n{result['code']}")
    # print(f"Output:\n{result.get('output', 'No output')}\n")

print("percentage passed: " + str(100*totalpassed/ len(results)) + "%")

print(f"\nCode files were read from: {CODE_FOLDER}")
