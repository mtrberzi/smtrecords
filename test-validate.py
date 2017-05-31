#!/usr/bin/env python3

import tasks

case = "/home/mtrberzi/projects/z3str/tests/concat-eq-concat-case1_sat.smt2"
result = "sat"
solver = ["/home/mtrberzi/projects/z3str/build/z3", "-smt2", "-in"]
model = """sat
(model 
  (define-fun V () String
    "aaaaaaaaaaBaao")
  (define-fun X () String
    "baaaaaaaaaaB")
  (define-fun U () String
    "b")
  (define-fun !!TheoryStrOverlapAssumption!!!0 () Bool
    false)
  (define-fun Y () String
    "aao")
)
"""

validation_result = tasks.validate_result(solver, case, result, model)
print(validation_result)
