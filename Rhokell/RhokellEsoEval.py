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

# Define the path to the folder containing the test cases
TEST_FOLDER = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                          "data", "EsoEval")

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
    Load test cases for a specific task from a JSON file.
    """
    test_file = os.path.join(TEST_FOLDER, f"{task_name}.json")
    
    if not os.path.exists(test_file):
        print(f"Warning: Test file {test_file} not found.")
        return []
    
    try:
        with open(test_file, 'r') as f:
            test_cases = json.load(f)
        return test_cases
    except Exception as e:
        print(f"Error loading test cases: {e}")
        return []

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

def main():
    """
    Main function to evaluate all tasks.
    """
    # List of common esoteric programming tasks
    tasks = [
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
    
    results = []
    
    for task in tasks:
        print(f"\n{'='*50}")
        print(f"Evaluating task: {task}")
        print(f"{'='*50}\n")
        
        result = evaluate_task(task)
        results.append(result)
    
    # Print summary
    print("\n\nFinal Results:")
    print(f"{'='*50}")
    
    total_passed = 0
    for res in results:
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
    print(f"Test cases were read from: {TEST_FOLDER}")

if __name__ == "__main__":
    main()
