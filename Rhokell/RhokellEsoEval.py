# -*- coding: utf-8 -*-
"""
Script for evaluating Rhokell code on general esoteric language tasks.
"""

import os
import subprocess
import tempfile
import re
import json
from typing import Any, Dict, List

# Path to your local Rhokell interpreter
RHOKELL_INTERPRETER_PATH = os.path.join(os.getcwd(), "rhokell", "target", "release", "rhokell")

# Define the path to the folder containing the Rhokell code to evaluate
CODE_FOLDER = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                          "code_to_evaluate", "Rhokell", "EsoEval")

def execute_rhokell_function(code: str, input_data: str = "") -> str:
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

        # Run in RD (ResultDisplay) mode to get the output
        result = subprocess.run(
            [RHOKELL_INTERPRETER_PATH, "-d", temp_rhokell_path],
            input=input_data,
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
            {"input": "Rhokell", "output": "Rhokell"},
            {"input": "123", "output": "123"}
        ],
        "reverse_cat": [
            {"input": "hello", "output": "olleh"},
            {"input": "Rhokell", "output": "llekohr"},
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
    Evaluate Rhokell code for a specific task against test cases.
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
    file_path = os.path.join(CODE_FOLDER, f"{task_name}.rhk")
    
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
            rhokell_code = f.read().strip()
        
        print(f"Reading Rhokell code from file: {file_path}")
        print(f"Code: {rhokell_code}\n")
        
        if not rhokell_code:
            return {
                "task": task_name,
                "status": "Failed",
                "reason": "Empty code file"
            }
        
        # Initialize pass status
        all_pass = True
        failed_tests = []
        
        # Execute and evaluate each test case
        for test_idx, test_case in enumerate(test_cases, start=1):
            input_data = test_case.get("input", "")
            expected_output = test_case.get("output", "")
            
            # Execute the Rhokell code
            output = execute_rhokell_function(rhokell_code, input_data)
            
            # Limit the output printed to prevent long error messages
            if output.startswith("Error:"):
                display_output = output  # Short error message
            else:
                display_output = output[:20] + "..." if len(output) > 20 else output  # Truncate long outputs
            
            print(f"Test {test_idx}: Input: {input_data}, Expected: {expected_output}, Output: {display_output}")
            
            # Check if the output matches the expected output
            # For Rhokell, we might need to normalize the output
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
        
        if all_pass:
            print(f"Task {task_name} passed all test cases.")
            return {
                "task": task_name,
                "status": "Passed",
                "tests_passed": len(test_cases),
                "tests_total": len(test_cases)
            }
        else:
            failure_message = f"Failed {len(failed_tests)} test cases out of {len(test_cases)}"
            print(f"Task {task_name} {failure_message}")
            
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
                "reason": failure_message
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
        'prompt': 'print "Hello, Rhokell!"',
        'tests': ["", "Hello, Rhokell!"]
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
    # Define the problems to evaluate

    
    # List of traditional esoteric programming tasks
    traditional_tasks = [
        "hello_world",
        "cat",
        "reverse_cat",
        "truth_machine",
        "fibonacci",
        "factorial",
        "quine",
        "rot13",
        "99_bottles"
    ]
    
    # Define the tasks to evaluate - can be either from problems list or traditional tasks
    # For now, we'll use the problems list
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
    
    for res in results:
        if 'prompt' in res:
            status_info = f"Problem {res['task']}: {res.get('prompt', '')}, Status: {res['status']}"
        else:
            status_info = f"Task: {res['task']}, Status: {res['status']}"
            
        if res['status'] == "Passed":
            total_passed += 1
            status_info += f", Tests Passed: {res.get('tests_passed', 'N/A')}/{res.get('tests_total', 'N/A')}"
        else:
            status_info += f", Reason: {res.get('reason', 'Unknown')}"
        print(status_info)
    
    if results:
        print(f"\nPercentage passed: {100 * total_passed / len(results):.2f}%")
    else:
        print("No tasks were evaluated.")
    
    print(f"\nCode files were read from: {CODE_FOLDER}")
    print("Test cases are defined directly in the script.")

if __name__ == "__main__":
    main()
