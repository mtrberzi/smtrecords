#!/usr/bin/env python3

import tasks

case = "/home/mtrberzi/projects/z3str/tests/pisa/pisa-010.smt2"
result = "sat"
solver = ["/home/mtrberzi/projects/z3str/build/z3", "-smt2", "-in"]
#solver = ["/work/validation_solvers/cvc4-1.5", "--lang", "smt2.5", "--no-interactive", "--no-interactive-prompt", "--strings-exp"]
model = """
sat
(model                                               
  (define-fun s () String                            
    "<script type = ""text/javascript"">")           
  (define-fun ret0 () String                         
    "&lt;script type = ""text/javascript""&gt;")     
  (define-fun ret1 () String                         
    "&lt;script type = ""text/javascript""&gt;<br/>")
)                                                        
"""

validation_result = tasks.validate_result(solver, case, result, model)
print(validation_result)
