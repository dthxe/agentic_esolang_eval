# Agentic Esolang Evaluation

This repository contains scripts for evaluating code in esoteric programming languages (esolangs) against benchmarks. The scripts are modified versions of the [esolangs](https://github.com/saraswathyamjith/esolangs) repository that evaluate code from files instead of generating code with an LLM.

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

## Data

The scripts require the HumanEval dataset from OpenAI. You can download it from:
https://github.com/openai/human-eval

Place the `HumanEval.jsonl` file in the `data/` directory.
