# -*- coding: utf-8 -*-
"""
Script for evaluating Rhokell code from a folder against HumanEval problems.
"""

import os
import subprocess
import re
import ast
import jsonlines
import tempfile
from typing import Any, List, Tuple

# Define the path to the folder containing the Rhokell code to evaluate
CODE_FOLDER = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                          "code_to_evaluate", "Rhokell", "HumanEval")

# Path to your local Rhokell interpreter
RHOKELL_INTERPRETER_PATH = os.path.join(os.getcwd(), "rhokell", "target", "release", "rhokell")

def execute_rhokell_function(code: str, input_data: Any = "") -> str:
    """
    Executes Rhokell code with the given input and returns the output or a concise error message.
    Ignores lines that begin with # comments.
    """
    try:
        if not os.path.isfile(RHOKELL_INTERPRETER_PATH):
            return f"Error: Rhokell interpreter not found at {RHOKELL_INTERPRETER_PATH}."
            
        # Filter out lines that begin with # comments
        filtered_code_lines = [line for line in code.split('\n') if not line.strip().startswith('#')]
        filtered_code = '\n'.join(filtered_code_lines)
        
        # Create a temporary file for the Rhokell code in the current directory
        temp_rhokell_path = "temp_eval.rhk"
        with open(temp_rhokell_path, "w") as f:
            f.write(filtered_code)

        # Convert input_data to string
        input_str = str(input_data)

        # Run in RD (ResultDisplay) mode to get the output
        result = subprocess.run(
            [RHOKELL_INTERPRETER_PATH, "-d", temp_rhokell_path],
            input=input_str,
            capture_output=True,
            text=True,
            timeout=10  # Longer timeout for Rhokell
        )

        # Clean up the temporary file
        os.remove(temp_rhokell_path)

        if result.returncode != 0:
            error_message = result.stderr.strip().split('\n')[-1] if result.stderr else "Unknown error"
            return f"Error: {error_message}"

        return result.stdout.strip()

    except subprocess.TimeoutExpired:
        return "Error: Execution timed out."
    except Exception as e:
        return f"Error during execution: {str(e)}"

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
            # Tolerance is currently not used; can be implemented if needed
            test_cases.append((input_args, expected_output))
        except Exception as e:
            print(f"Error parsing approximate equality test case: {e}")

    return test_cases

def extract_function_name(rhokell_code: str) -> str:
    """
    Extract the function name from Rhokell code.
    In Rhokell, functions are defined as (function_name (param1) (param2) ...) = ...
    """
    pattern = r'\(([a-zA-Z0-9_]+)\s*\('
    match = re.search(pattern, rhokell_code)
    if match:
        return match.group(1)
    return None

##############################################################################
# Load the problems from the JSONL file
problems = []
humaneval_path = "data/HumanEval.jsonl"
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

##############################################################################
# Evaluation Loop

results = []

for idx, problem in enumerate(problems[:10]):  # Limit to first 10 problems for testing
    print(f"Evaluating Problem {idx+1}/{len(problems[:10])}: {problem['task_id']}")

    try:
        # Construct the file path for this problem
        file_path = os.path.join(CODE_FOLDER, f"{problem['task_id']}.rhk")

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
            rhokell_code = f.read().strip()

        print(f"Reading Rhokell code from file: {file_path}")
        print(f"Code: {rhokell_code}\n")

        if not rhokell_code:
            raise ValueError("Empty code file.")
            
        # Extract function name
        func_name = extract_function_name(rhokell_code)
        if not func_name:
            raise ValueError("Could not extract function name from Rhokell code.")
        
        print(f"Extracted function name: {func_name}")
            
        # Parse test cases
        parsed_test_cases = parse_test_cases(problem['test'])
        print(f"Parsed Test Cases: {parsed_test_cases}\n")

        # Initialize pass status
        all_pass = True
        failed_tests = []

        # Execute and evaluate each test case
        for test_idx, (inputs, expected) in enumerate(parsed_test_cases, start=1):
            # Prepare a test wrapper that calls the function with the inputs
            # In Rhokell, we need to create a main function that calls our target function
            if isinstance(inputs, tuple):
                # Multiple arguments
                args_str = ' '.join([f"({repr(arg)})" for arg in inputs])
                test_code = f"{rhokell_code}\n\n(main) = ({func_name} {args_str});"
            else:
                # Single argument
                test_code = f"{rhokell_code}\n\n(main) = ({func_name} ({repr(inputs)}));"
            
            # Execute the Rhokell code
            output = execute_rhokell_function(test_code, "")

            # Limit the output printed to prevent long error messages
            if output.startswith("Error:"):
                display_output = output  # Short error message
            else:
                display_output = output[:20] + "..." if len(output) > 20 else output  # Truncate long outputs

            print(f"Test {test_idx}: Input: {inputs}, Expected: {expected}, Output: {display_output}")

            # Compare the output with the expected result
            # In Rhokell, the output might need some parsing/conversion
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
                "status": "Passed",
                "attempts": 1
            })
        else:
            failure_message = f"Failed {len(failed_tests)} test cases out of {len(parsed_test_cases)}"
            print(f"Problem {problem['task_id']} {failure_message}")
            
            # Print details of failed tests
            for failed_test in failed_tests:
                print(f"  Test {failed_test['test_idx']} failed:")
                print(f"    Input: {failed_test['input']}")
                print(f"    Expected: {failed_test['expected']}")
                print(f"    Got: {failed_test['output']}")
            
            results.append({
                "problem": problem["task_id"],
                "status": "Failed",
                "attempts": 1,
                "reason": failure_message
            })

    except Exception as e:
        print(f"Error during evaluation: {e}")
        error_message = f"Encountered an error: {e}"
        print(error_message)
        
        results.append({
            "problem": problem["task_id"],
            "status": "Failed",
            "attempts": 1,
            "reason": error_message
        })

print("\nFinal Results:")
totalpassed = 0
for res in results:
    print(f"Problem: {res['problem']}, Status: {res['status']}, Attempts: {res.get('attempts', 'N/A')}")
    if res['status'] == "Passed":
         totalpassed += 1

print("percentage passed: " + str(100*totalpassed/ len(results)) + "%")

print(f"\nCode files were read from: {CODE_FOLDER}")
