#!/usr/bin/env python3

import tasks

case = "/home/mtrberzi/projects/z3str/tests/z3str/contains-024.smt2"
result = "sat"
#solver = ["/home/mtrberzi/projects/z3str/build/z3", "-smt2", "-in"]
solver = ["/work/validation_solvers/cvc4-20170105", "--lang", "smt2", "--no-interactive", "--no-interactive-prompt", "--strings-exp"]
model = """sat
(model 
  (define-fun y1 () String
    "bc")
  (define-fun b2 () Bool
    false)
  (define-fun x2 () String
    "caaaz")
  (define-fun x1 () String
    "caaaz")
  (define-fun b1 () Bool
    true)
  (define-fun y2 () String
    "abcd")
  (define-fun !!TheoryStrOverlapAssumption!!!0 () Bool
    false)
)
"""

validation_result = tasks.validate_result(solver, case, result, model)
print(validation_result)
