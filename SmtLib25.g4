grammar SmtLib25;

smtfile : script | response;

/** Commands **/

script : command* ;

option :
       ':produce-models' boolean
       | ':auto-config' boolean
       ;

command :
        '(' 'assert' term ')'
	| '(' 'check-sat' ')'
    | '(' 'declare-const' SYMBOL sort ')'
    | '(' 'declare-fun' SYMBOL '(' sort* ')' sort ')'
    | '(' 'define-fun' fun_def ')'
    | '(' 'exit' ')'
    | '(' 'get-model' ')'
    | '(' 'set-logic' SYMBOL ')'
    | '(' 'set-info' attribute ')'
    | '(' 'set-option' option ')'
    ;

fun_def : SYMBOL '(' sorted_var* ')' sort term ;

/** General Tokens **/

INTEGER : '0' | [1-9][0-9]* ;
B_VALUE : 'true' | 'false' ;

numeral : INTEGER;
boolean : B_VALUE;

STRINGCONSTANT : '"' (QUOTEESCAPE|.)*? '"' ;
fragment QUOTEESCAPE : '""' ;

string : STRINGCONSTANT;

SYMBOL : SIMPLE_SYMBOL | COMPLEX_SYMBOL ;
/** A simple symbol is a non-empty sequence of letters, digits, and the characters
    + - / * = % ? ! . $ _ ~ & ^ < > @
    that does not start with a digit. **/
fragment SIMPLE_SYMBOL : ('a'..'z' | 'A'..'Z' | '+' | '-' | '/' | '*' | '=' | '%' | '?' | '!' | '.' | '$' | '_' | '~' | '&' | '^' | '<' | '>' | '@') ('0'..'9' | 'a'..'z' | 'A'..'Z' | '+' | '-' | '/' | '*' | '=' | '%' | '?' | '!' | '.' | '$' | '_' | '~' | '&' | '^' | '<' | '>' | '@')* ;
/** A complex symbol is a
    sequence of whitespace+printable characters that
    starts and ends with | and doesn't otherwise contain | or \. **/
fragment COMPLEX_SYMBOL : '|' ~('|' | '\\')+ '|' ;

KEYWORD : ':' SIMPLE_SYMBOL ;

/** S-Expressions **/

spec_constant : numeral | /* DECIMAL | HEXADECIMAL | BINARY | */ string ;
s_expr : spec_constant | SYMBOL | KEYWORD | '(' s_expr* ')' ;

/** Identifiers **/

identifier : SYMBOL | '(' '_' SYMBOL index+ ')';
index : numeral | SYMBOL ;

/** Sorts **/

sort : identifier | '(' identifier sort+ ')';

/** Attributes **/

attribute_value : spec_constant | SYMBOL | '(' s_expr* ')';
attribute : KEYWORD attribute_value? ;

/** Terms **/

qual_identifier : identifier | '(' 'as' identifier sort ')' ;
var_binding : '(' SYMBOL term ')' ;
sorted_var : '(' SYMBOL sort ')' ;

term : spec_constant
    | qual_identifier
    | '(' qual_identifier term+ ')'
    | '(' 'let' '(' var_binding+ ')' term ')'
    | '(' 'forall' '(' sorted_var+ ')' term ')'
    | '(' 'exists' '(' sorted_var+ ')' term ')'
    | '(' '!' term attribute+ ')'
    ;

/** Responses **/

response : (error_response | check_sat_response | get_model_response)+;

error_response : '(' 'error' string ')' ;
check_sat_response : 'sat\n' | 'unsat\n' | 'timeout\n' | 'unknown\n';
/* The following is specific to Z3 and is not SMT-LIB 2.5 standard. */
get_model_response : '(' 'model' model_response* ')' ;

model_response : '(' 'define-fun' fun_def ')' ;

WS: [ \n\t\r]+ -> skip;
