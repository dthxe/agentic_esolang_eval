# Agentic Esolang Evaluation

This repository contains scripts for evaluating code in esoteric programming languages (esolangs) against benchmarks.

## Overview

This project provides a framework for evaluating the performance of esoteric programming languages on standard programming benchmarks. Instead of generating code with language models, this repository focuses on evaluating pre-written code files, making it suitable for comparing different code generation approaches or manual implementations.

The repository includes:
- Evaluation scripts for multiple esoteric languages (0815, Minipy, Pyth, Rhokell)
- Code samples generated with and without context by agentic AI systems
- Standardized evaluation methodology using the HumanEval benchmark

## Code Generation Methodology

The code samples in this repository were generated using Windsurf, an agentic AI system, in March/April 2025. The prompting was done through an agent directly, instead of being fed through a traditional LLM API, allowing for more interactive and context-aware code generation. Two sets of code were generated:

1. **Context Code**: Generated with full contextual information about the esoteric language
2. **No Context Code**: Generated with minimal information about the language

This allows for comparative analysis of how contextual information affects code generation quality in esoteric languages.

## Requirements and Dependencies

### Software Requirements
- Python 3.6+
- Dependencies listed in `requirements.txt` (install with `pip install -r requirements.txt`)

### Language Interpreters
Each esoteric language requires its own interpreter:

- **0815**: 
  - Interpreter: `esolang0815_interpreter.py` 
  - Source: [GitHub Gist](https://gist.githubusercontent.com/perey/015aeea5c3af016531e9/raw/71b4cbfd16577e349d58a11eefd1cde12d40a2ae/esolang0815_interpreter.py)
  - Installation: Download the interpreter to the root directory of this repository

- **Pyth**: 
  - Interpreter: `pyth.py` 
  - Source: [GitHub Repository](https://github.com/isaacg1/pyth)
  - Installation: Clone the Pyth repository to the root directory of this repository
  ```bash
  git clone https://github.com/isaacg1/pyth.git
  ```

- **Minipy**: 
  - Interpreter: Included in the repository
  - No additional installation required

- **Rhokell**: 
  - Interpreter: `rhokell` 
  - Source: [GitHub Repository](https://github.com/pro465/rhokell)
  - Description: A functional programming language based on rho calculus and Haskell, featuring pattern matching, algebraic data types, and higher-order functions
  - Installation: Clone and build the Rhokell repository
  ```bash
  git clone https://github.com/pro465/rhokell.git
  cd rhokell
  cargo build --release
  ```
  - Usage: After building, you can run Rhokell code with `./target/release/rhokell path/to/file.rhk`

## Overview

This project provides a framework for evaluating the performance of esoteric programming languages on standard programming benchmarks. Instead of generating code with language models, this repository focuses on evaluating pre-written code files, making it suitable for comparing different code generation approaches or manual implementations.

## Supported Languages

- **0815**: A queue-based esoteric language with 3 registers
- **Minipy**: A minimalist version of Python with shortened syntax
- **Pyth**: A concise, Pythonic code-golfing language
- **Rhokell**: A functional programming language based on rho calculus and Haskell

## Directory Structure

- `0815/`: Contains evaluation scripts for 0815
- `Minipy/`: Contains evaluation scripts for Minipy
- `Pyth/`: Contains evaluation scripts for Pyth
- `Rhokell/`: Contains evaluation scripts for Rhokell
- `context_code/`: Code generated with full context about the language
  - Organized by language and model
- `no_context_code/`: Code generated with minimal context about the language
  - Organized by language and model
- `code_to_evaluate/`: Directory where code files should be placed for evaluation
  - `0815/HumanEval/`: Place 0815 code files here
  - `Minipy/HumanEval/`: Place Minipy code files here
  - `Pyth/HumanEval/`: Place Pyth code files here
  - `Rhokell/HumanEval/`: Place Rhokell code files here
  - `Rhokell/EsoEval/`: Place Rhokell code for esoteric language tasks here

## How to Use

1. Place your code files in the appropriate subdirectory of `code_to_evaluate/`
2. Name your files according to the problem ID (e.g., `HumanEval/0.pyth`, `HumanEval/1.pyth`, etc.)
3. Run the evaluation script for the language you want to evaluate:

### HumanEval Benchmarks
These scripts evaluate code against the HumanEval benchmark:

```bash
# For Pyth
python Pyth/PythHumanEval_FromFolder.py

# For 0815
python 0815/0815HumanEval_FromFolder.py

# For Minipy
python Minipy/MiniPyHumanEval_FromFolder.py

# For Rhokell HumanEval
python Rhokell/RhokellHumanEval_FromFolder.py
```

### EsoEval Benchmarks
These scripts evaluate code against a custom set of 30 programming tasks embedded directly in the scripts:

```bash
# For Pyth EsoEval
python Pyth/PythEsoEval_FromFolder.py

# For 0815 EsoEval
python 0815/0815EsoEval_FromFolder.py

# For Minipy EsoEval
python Minipy/MiniPyEsoEval.py

# For Rhokell EsoEval
python Rhokell/RhokellEsoEval.py
```

## Dataset

### HumanEval Dataset

- **Source**: The scripts require the HumanEval dataset from OpenAI
- **Repository**: [https://github.com/openai/human-eval](https://github.com/openai/human-eval)
- **License**: MIT License
- **Citation**: Chen, M., Tworek, J., Jun, H., Yuan, Q., Pinto, H. P. D. O., Kaplan, J., ... & Zaremba, W. (2021). Evaluating large language models trained on code. arXiv preprint arXiv:2107.03374.

### Dataset Installation

1. Clone the HumanEval repository:
   ```bash
   git clone https://github.com/openai/human-eval.git
   ```

2. Extract the dataset:
   ```bash
   gunzip human-eval/data/HumanEval.jsonl.gz
   ```

3. Copy or link the dataset to the `data/` directory:
   ```bash
   cp human-eval/data/HumanEval.jsonl data/
   ```

## EsoEval Dataset: Simple Problems for Pyth, 0815, and Janus Benchmarks

Below is the problem set used for evaluating esolangs that are more divergent from standard languages. The problem set was tested via OPENAI's gpt-4o-mini which achieved a 93.33% accuracy in Python. Since it achieved such high accuracy, these problems are able to be labeled as a standard, simple benchmark. 

1. Print "hello world".
2. Given a number `n` as input, return the `n`th factorial number.
3. Given a number `n`, return `"Even"` if `n` is even, else `"Odd"`.
4. Given two numbers `a` and `b`, return their sum.
5. Given a number `n`, return `True` if it is prime, else `False`.
6. Given a string `s`, return the reversed string.
7. Print "Hello, Pyth!".
8. Given two numbers `a` and `b`, return their product.
9. Given a number `n`, return `True` if it is positive, else `False`.
10. Given two strings `s1` and `s2`, return their concatenation.
11. Given a number `n`, return its square.
12. Given a string `s`, return the number of characters in the string.
13. Given two numbers `a` and `b`, return the smaller number.
14. Given a string `s`, return `True` if all characters in the string are vowels, else `False`.
15. Given two numbers `a` and `b`, return the absolute difference between them.
16. Given a string `s` and a number `n`, return the string repeated `n` times.
17. Given a number `n`, return the Fibonacci sequence up to the nth term.
18. Given a list of numbers, return the maximum number.
19. Given a string `s` , return True if it is a palindrome, else False.
20. Given two numbers `a` and `b`, return their greatest common divisor.
21. Given a list of numbers, return the list sorted in ascending order.
22. Given a number `n`, return True if it is a perfect square, else False.
23. Given a string  `s` , return the number of vowels in the string.
24. Given a list of numbers, return the sum of all numbers in the list.
25. Given a number `n`,, return its binary representation as a string.
26. Given two strings `s1` and `s2`, return True if s1 is an anagram of s2, else False.
27. Given a number `n`, return the sum of digits in n.
28. Given a list of numbers, return True if all numbers are even, else False.
29. Given a string `s`, return the string in title case.
30. Given two numbers  `a` and `b`, return True if a is divisible by b, else False.

## Reproducibility

To ensure reproducibility of results, follow these steps:

1. Install all dependencies as specified in the Requirements section
2. Download the HumanEval dataset and place it in the `data/` directory
3. Install the language interpreters as described
4. Place your code files in the appropriate directories following the naming conventions
5. Run the evaluation scripts as described in the "How to Use" section

## Documentation & Examples Sources
0815 examples & documentation:
Jorente, P. (n.d.). 0815. In Poncho esolang. Retrieved May 21, 2025, from http://paulo-jorente.de/poncho/esolang/0815/
All 0815 examples and documentation were drawn from the official 0815 website. 

Pyth examples & documentation:
Isaacg1. (2015). Pyth 1.0 documentation. Retrieved May 21, 2025, from https://pyth.readthedocs.io/en/latest/
All Pyth examples and documentation were drawn from the official Pyth website. 

Rhokell examples & documentation:
pro465. (n.d.). rhokell [Computer software]. GitHub. Retrieved May 21, 2025, from https://github.com/pro465/rhokell
All Pyth examples and documentation were drawn from the official Rhokell git.

Minipy documentation:
Esolangs Wiki. (n.d.). Minipy. Retrieved May 21, 2025, from https://esolangs.org/wiki/Minipy
All minipy examples were generated by researchers. 

