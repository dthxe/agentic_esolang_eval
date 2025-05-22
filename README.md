# Agentic Esolang Evaluation

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

This repository contains scripts for evaluating code in esoteric programming languages (esolangs) against benchmarks. The scripts are modified versions of the [esolangs](https://github.com/saraswathyamjith/esolangs) repository that evaluate code from files instead of generating code with an LLM.

## Overview

This project provides a framework for evaluating the performance of esoteric programming languages on standard programming benchmarks. Instead of generating code with language models, this repository focuses on evaluating pre-written code files, making it suitable for comparing different code generation approaches or manual implementations.

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

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Overview

This project provides a framework for evaluating the performance of esoteric programming languages on standard programming benchmarks. Instead of generating code with language models, this repository focuses on evaluating pre-written code files, making it suitable for comparing different code generation approaches or manual implementations.

## Supported Languages

- **0815**: A queue-based esoteric language with 3 registers
- **Minipy**: A minimalist version of Python with shortened syntax
- **Pyth**: A concise, Pythonic code-golfing language

## Directory Structure

- `0815/`: Contains evaluation scripts for 0815
- `Minipy/`: Contains evaluation scripts for Minipy
- `Pyth/`: Contains evaluation scripts for Pyth
- `code_to_evaluate/`: Directory where code files should be placed
  - `0815/HumanEval/`: Place 0815 code files here
  - `Minipy/HumanEval/`: Place Minipy code files here
  - `Pyth/HumanEval/`: Place Pyth code files here

## How to Use

1. Place your code files in the appropriate subdirectory of `code_to_evaluate/`
2. Name your files according to the problem ID (e.g., `HumanEval/0.pyth`, `HumanEval/1.pyth`, etc.)
3. Run the evaluation script for the language you want to evaluate:

```bash
# For Pyth
python Pyth/PythHumanEval_FromFolder.py

# For 0815
python 0815/0815HumanEval_FromFolder.py

# For Minipy
python Minipy/MiniPyHumanEval_FromFolder.py
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

## Reproducibility

To ensure reproducibility of results, follow these steps:

1. Install all dependencies as specified in the Requirements section
2. Download the HumanEval dataset and place it in the `data/` directory
3. Install the language interpreters as described
4. Place your code files in the appropriate directories following the naming conventions
5. Run the evaluation scripts as described in the "How to Use" section

All evaluation results are deterministic given the same code files and interpreters.
