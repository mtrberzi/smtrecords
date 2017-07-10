Installation
============

You will need to install the following Python3 modules:

- antlr4-python3-runtime
- typing
- python-dateutil
- sqlalchemy

You can do this easily by typing (possibly as root):

    pip3 install antlr4-python3-runtime typing python-dateutil sqlalchemy

Usage
=====

The tool will write to the directory `/work` and its subdirectories, where it keeps a copy of the solvers, cases, etc. You can change the file "config.py" to set a different path or change other options.

Here is an example of how to use the tool (out of the base directory).

Create a database by running:

    ./mkdb.py

Register a new version of a solver (only needs to be done once per version):

    ./new-solver.py z3 build-20170607 /path/to/z3/binary

Register a new benchmark (only needs to be done once per benchmark):

    ./new-benchmark.py Kaluza /path/to/kaluza/cases

Register a solver to be used for validating results (only once per validation solver):

    ./new-validation-solver.py cvc4-20170103 /path/to/cvc4/binary [command line arguments]

A note on the validation solvers: Z3str2 isn't currently supported due to issues with interactive mode and differences in the syntax used in the new SMT-LIB standard. I plan to add special support for it at a later time. Validation works well with solvers such as CVC4 and Z3.

CVC4 needs to be set up with the following arguments:

    ./new-validation-solver.py cvc4-20170103 /path/to/cvc4 --lang smt2 --no-interactive --no-interactive-prompt --strings-exp

To run a solver on a benchmark:

    ./run-solver.py solver-name solver-version benchmark solver-arguments

For example:

    ./run-solver.py z3 build-20170607 Kaluza smt.string_solver=z3str3

You may see some warnings which say "ANTLR runtime and generated code versions disagree"; this can be safely ignored.

The script will automatically run the solver on all cases in the given benchmark, record the time and result, and run all validation solvers against all cases for which the test solver answered SAT or UNSAT. SAT cases will validate the model given by the test solver; UNSAT cases will just re-run the case on the validation solver and check that it also answers UNSAT. After the script completes, it prints a test report and validation report.

When a run starts, the script prints out a run number. If you need to stop a run and resume it later, or to reprint the test report, you can use the resume-run script:

    ./resume-run.py run-number
