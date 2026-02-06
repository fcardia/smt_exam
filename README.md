# SMT Exam

Exam for the "Symbolic AI and SMT solving" seminar by dr. Enrico Lipparini

## Installation
If you don't have `z3-solver` installed, run the following command to configure the environment.

```bash
python3 -m venv smt
source smt/bin/activate
pip install -r requirements.txt
```

## Get started

To test the code, enter the numbers in a space-separated list and the target, as in the following command
```bash
python3 project.py --numbers 1 3 5 8 10 50 --target 462 
```

You should see
```bash
Initial number: 50
Step 1: operation - with number 3 -> result 47
Step 2: operation * with number 10 -> result 470
Step 3: operation - with number 8 -> result 462
Final number: 462
Distance from goal: 0
```
