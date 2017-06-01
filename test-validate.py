#!/usr/bin/env python3

import tasks

case = "/work/benchmarks/PISA/pisa-002.smt2"
result = "sat"
#solver = ["/home/mtrberzi/projects/z3str/build/z3", "-smt2", "-in"]
solver = ["/work/validation_solvers/cvc4-20170105", "--lang", "smt2", "--no-interactive", "--no-interactive-prompt", "--strings-exp"]
model = """sat
 (model                                        
   (define-fun $$_val_ts0!4_14_0_1!22 () String
     "9")                                      
   (define-fun ts1!3 () String                 
     "**UNUSED**")                             
   (define-fun ts0!2 () String                 
     "**UNUSED**")                             
   (define-fun $$_xor!10 () Int                
     19)                                       
   (define-fun ts1!7 () String                 
     "aaaaaD")                                 
   (define-fun $$_str2!11 () String            
     "**UNUSED**")                             
   (define-fun $$_xor!12 () Int                
     30)                                       
   (define-fun ts0!6 () String                 
     "aaaaaaaaaaaaajsc")                       
   (define-fun $$_str1!9 () String             
     "**UNUSED**")                             
   (define-fun $$_len_ts1!7_1_1!14 () String   
     "more")                                   
   (define-fun ts1!5 () String                 
     "ript scr=aaaaaD")                        
   (define-fun s () String                     
     "aaaaaaaaaaaaajscript scr=aaaaaD")        
   (define-fun ts0!4 () String                 
     "aaaaaaaaaaaaaj")                         
   (define-fun $$_len_ts1!7_2_3!16 () String   
     "more")                                   
   (define-fun ts1!1 () String                 
     "**UNUSED**")                             
   (define-fun $$_len_ts0!4_2_2!15 () String   
     "more")                                   
   (define-fun $$_len_ts1!7_3_4!17 () String   
     "6")                                      
   (define-fun $$_str0!8 () String             
     "sc")                                     
   (define-fun $$_len_ts0!4_1_0!13 () String   
     "more")                                   
   (define-fun $$_val_ts1!7_6_0_0!20 () String 
     "29")                                     
   (define-fun $$_len_ts0!4_5_7!21 () String   
     "14")                                     
   (define-fun ts0!0 () String                 
     "**UNUSED**")                             
   (define-fun $$_len_ts0!4_4_6!19 () String   
     "more")                                   
   (define-fun ret () String                   
     "aaaaaaaaaaaaajscript scr=aaaaaD")        
   (define-fun $$_len_ts0!4_3_5!18 () String   
     "more")                                   
 )      
"""

validation_result = tasks.validate_result(solver, case, result, model)
print(validation_result)
