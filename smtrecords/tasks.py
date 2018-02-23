from __future__ import absolute_import

import os
import tempfile
import shutil
import subprocess
import time
import stat
import signal
import fcntl

from antlr4 import *
from smtrecords.SmtLib25Lexer import SmtLib25Lexer
from smtrecords.SmtLib25Parser import SmtLib25Parser
from smtrecords.SmtLib25Visitor import SmtLib25Visitor

class ResponseVisitor(SmtLib25Visitor):
    def __init__(self):
        self.status = None # will be replaced by 'sat', 'unsat', etc.
        self.errors = []
        self.model = {}
    
    def visitScript(self, ctx):
        raise Exception("attempted to parse a response, got a script")

    def visitCheck_sat_response(self, ctx):
        if self.status is not None:
            raise ValueError("multiple check-sat-response entries not supported")
        response = ctx.getText()
        if response == "sat":
            self.status = "sat"
        elif response == "unsat":
            self.status = "unsat"
        elif response == "timeout":
            self.status = "timeout"
        elif response == "unknown":
            self.status = "unknown"
        else:
            raise ValueError("unrecognized check-sat-response " + response)
        return self.visitChildren(ctx)

    def visitError_response(self, ctx):
        self.errors.append(ctx.string().getText())
        return self.visitChildren(ctx)

    def visitGet_model_response(self, ctx):
        for child in ctx.getChildren():
            modelEntry = self.visit(child)
            if modelEntry is not None:
                (varname, assignment) = modelEntry
                self.model[varname] = assignment
        return None

    def visitModel_response(self, ctx):
        return self.visit(ctx.getChild(2))

    def visitFun_def(self, ctx):
        # fun_def : symbol ( sorted_var* ) sort term
        return (ctx.getChild(0).getText(), self.visit(ctx.getChild(ctx.getChildCount() - 1)))

    def visitString(self, ctx):
        return ctx.getText()

    def visitNumeral(self, ctx):
        return ctx.getText()

    def visitIdentifier(self, ctx):
        return ctx.getText()

    def visitBoolean(self, ctx):
        return ctx.getText()

    def visitTerm(self, ctx):
        # handle terms like "( - 1 )"
        if ctx.getChildCount() == 1:
            return self.visit(ctx.getChild(0))
        elif ctx.getChildCount() > 1:
            operator = ctx.getChild(1).getText()
            if operator == "-":
                return "(- " + self.visit(ctx.getChild(2)) + ")"
            else:
                raise ValueError("Unrecognized operator " + operator)
        else:
            print(ctx.getText())
            raise ValueError("Not Implemented Yet")

# Parse an instance and collect all variables declared by (declare-fun), (declare-const), etc.
class InstanceVariableVisitor(SmtLib25Visitor):
    def __init__(self):
        self.variables = []

    def visitResponse(self, ctx):
        raise Exception("attempted to parse a script, got a response")

    def visitCommand(self, ctx):
        cmdtype = ctx.getChild(1).getText()
        if cmdtype == "declare-const" or cmdtype == "declare-fun":
            # SYMBOL is child[2]
            varname = ctx.getChild(2).getText()
            self.variables.append(varname)
        elif cmdtype == "define-fun":
            # SYMBOL is child[2].child[0]
            varname = ctx.getChild(2).getChild(0).getText()
            self.variables.append(varname)

# Parse an instance and collect all commands as a list in the order in which they appear,
# along with some information about them.

class CommandInfo():
    def __init__(self, cmd, is_check_sat):
        self.cmd = cmd
        self.is_check_sat = is_check_sat

class CommandListVisitor(SmtLib25Visitor):
    def __init__(self):
        self.cmdinfo = []

    def visitResponse(self, ctx):
        raise Exception("attempted to parse a script, got a response")

    def generic_string_conversion(self, expr):
        response = ""
        for child in expr.getChildren():
            result = self.visit(child)
            if result is None:
                response += child.getText()
            else:
                response += result
            response += " "
        return response
    
    def visitCommand(self, ctx):
        cmd = self.generic_string_conversion(ctx)
        cmdtype = ctx.getChild(1).getText()
        is_check_sat = False
        if cmdtype == 'check-sat':
            is_check_sat = True
        infoblock = CommandInfo(cmd, is_check_sat)
        self.cmdinfo.append(infoblock)
        
    def visitAttribute(self, ctx):
        return self.generic_string_conversion(ctx)

    def visitTerm(self, ctx):
        return self.generic_string_conversion(ctx)

    def visitOption(self, ctx):
        return self.generic_string_conversion(ctx)
            
def get_process_children(pid):
    p = subprocess.Popen('ps --no-headers -o pid --ppid %d' % pid, shell = True,stdout = subprocess.PIPE, stderr = subprocess.PIPE)
    stdout, stderr = p.communicate()
    return [int(p) for p in stdout.split()]
        
# Run a command with a timeout, after which it will be forcibly killed.
def run(args, cwd = None, shell = False, kill_tree = True, timeout = -1, env = None):
    class Alarm(Exception):
        pass
    def alarm_handler(signum, frame):
        raise Alarm
    p = subprocess.Popen(args, shell = shell, cwd = cwd, stdout = subprocess.PIPE, stderr = subprocess.PIPE, env = env)
    if timeout != -1:
        signal.signal(signal.SIGALRM, alarm_handler)
        signal.alarm(timeout)
    try:
        stdout, stderr = p.communicate()
        stdout = stdout.decode(encoding='latin-1')
        stderr = stderr.decode(encoding='latin-1')
        if timeout != -1:
            signal.alarm(0)
    except Alarm:
        pids = [p.pid]
        if kill_tree:
            pids.extend(get_process_children(p.pid))
        for pid in pids:
            # process might have died before getting to this line
            # so wrap to avoid OSError: no such process
            try:
                os.kill(pid, signal.SIGKILL)
            except OSError:
                pass
        return -9, '', ''
    return p.returncode, stdout, stderr

class TestResult:
    def __init__(self, testname, runtime, result):
        self.testname = testname
        self.runtime = runtime
        self.result = result
        self.stdout = None
        self.stderr = None


def run_smtlib_solver(z3file, testfile, timeout=20, extraArguments = []):
    runtime = 0.0
    result = ''
    verify = ''
    solveroutput = ''
    solverstderr = ''
    error = ''

    try:
        startTime = time.time()
        args = [z3file]
        for extra in extraArguments:
            args.append(extra)
        args.append(testfile)
        (exitCode, output, errors) = run(args, timeout=timeout)
        solveroutput = output
        solverstderr = errors
        endTime = time.time()
        runtime = round( float(endTime - startTime), 3)
        if len(output) == 0 or exitCode == -9:
            result = 'timeout'
        else:
            lines = output.split("\n")
            errlines = errors.split("\n")

            combined_lines = ""
            for line in lines:
                combined_lines += " " + line
            for line in errlines:
                combined_lines += " " + line    
            
            lines = [line for line in lines if line.strip()]
            # check result status
            for line in lines:
                if line.startswith('(error'):
                    result = 'error'
                    error = combined_lines
                    break
                if 'unsat' in line:
                    result = 'unsat'
                    error = ''
                    break
                elif 'sat' in line:
                    result = 'sat'
                    error = ''
                    break
                elif 'unknown' in line:
                    result = 'unknown'
                    error = ''
                    break
                elif 'timeout' in line:
                    result = 'timeout'
                    error = ''
                    break
                else:
                    result = 'error'
                    error = combined_lines
                    break
    except Exception as e:
        result = 'crash'
        error = str(e)
        raise e
        
    result = TestResult(testfile, runtime, result)
    result.stdout = solveroutput
    result.stderr = solverstderr
    return result

class ValidationResult:
    def __init__(self, validationRunSuccessful, validationPassed, response):
        # validationRunSuccessful: Boolean. true if validation solver was invoked correctly and produced
        # a result, false if there was some error in validation
        self.validationRunSuccessful = validationRunSuccessful
        # validationPassed: Boolean. true if validation solver gave the same result as the run, false otherwise
        self.validationPassed = validationPassed
        # response: String. whatever result (sat/unsat/etc.) was returned by the validation solver
        self.response = response

    def __repr__(self):
        return "<ValidationResult: success={}, pass={}, response={}>".format(self.validationRunSuccessful, self.validationPassed, self.response)

def set_non_blocking(fd):
    flags = fcntl.fcntl(fd, fcntl.F_GETFL)
    flags = flags | os.O_NONBLOCK
    fcntl.fcntl(fd, fcntl.F_SETFL, flags)

expect_timeout = 2
    
def expect_success(stream):
    class Alarm(Exception):
        pass
    def alarm_handler(signum, frame):
        raise Alarm
    signal.signal(signal.SIGALRM, alarm_handler)
    signal.alarm(expect_timeout)
    response = b''
    try:
        while stream.readable():
            rx = stream.read(1024)
            if rx is not None:
                response += rx
            # look for newline
            if b'\n' in response:
                break
        # convert response to string, split along newline
        responseStr = response.decode('utf-8').split('\n')[0]
        signal.alarm(0) # cancel timeout
        return responseStr == "success"
    except Alarm:
        return False

validation_timeout = 5
    
# Run a reference solver, specified by solverCommandLine, on a given case,
# augmented with an existing result and test output
# Returns a ValidationResult
def validate_result(solverCommandLine, casePath, expectedResult, testOutput):
    class Alarm(Exception):
        pass
    def alarm_handler(signum, frame):
        raise Alarm
    # read the case and parse it
    case_stream = FileStream(casePath, encoding='utf-8')
    case_lexer = SmtLib25Lexer(case_stream)
    case_token_stream = CommonTokenStream(case_lexer)
    case_parser = SmtLib25Parser(case_token_stream)
    case_tree = case_parser.smtfile()
    # get instance variables
    v = InstanceVariableVisitor()
    v.visit(case_tree)
    # get list of commands
    commandV = CommandListVisitor()
    commandV.visit(case_tree)

    # now parse the result
    result_stream = InputStream(testOutput)
    result_lexer = SmtLib25Lexer(result_stream)
    result_token_stream = CommonTokenStream(result_lexer)
    result_parser = SmtLib25Parser(result_token_stream)
    result_tree = result_parser.smtfile()
    responseV = ResponseVisitor()
    responseV.visit(result_tree)
    # double-check that the test output at least contains the expected result
    if responseV.status != expectedResult:
        return ValidationResult(False, False, responseV.status)
    modelAssertions = []
    if responseV.status == 'sat':
        # discard variables from the model that don't appear in the instance
        for var in v.variables:
            if var in responseV.model.keys():
                modelAssertions.append("(assert (= {} {}))".format(var, responseV.model[var]))

    # launch the solver interactively
    solverP = subprocess.Popen(solverCommandLine, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=False)
    set_non_blocking(solverP.stdout)
    set_non_blocking(solverP.stderr)

    # expect response after each command
    solverP.stdin.write("(set-option :print-success true)\n".encode('ascii'))
    solverP.stdin.flush()
    if not expect_success(solverP.stdout):
        solverP.kill()
        return ValidationResult(False, False, "solver error in setup")
    
    # start sending commands
    for cmdinfo in commandV.cmdinfo:
        if cmdinfo.is_check_sat:
            # send model assertions if the expected answer is SAT
            if responseV.status == 'sat':
                for modelAssertion in modelAssertions:
                    solverP.stdin.write(modelAssertion.encode('ascii'))
                    solverP.stdin.write('\n'.encode('ascii'))
                    solverP.stdin.flush()
                    if not expect_success(solverP.stdout):
                        solverP.kill()
                        return ValidationResult(False, False, "solver error while adding model assertions")
            # now run check-sat and look for a check-sat response
            solverP.stdin.write("(check-sat)\n".encode('ascii'))
            solverP.stdin.flush()
            # set a timeout for safety reasons
            signal.signal(signal.SIGALRM, alarm_handler)
            signal.alarm(validation_timeout)
            response = b''
            try:
                while solverP.stdout.readable():
                    rx = solverP.stdout.read(1024)
                    if rx is not None:
                        response += rx
                        if b'\n' in response:
                            signal.alarm(0) # cancel timeout
                            break
            except Alarm:
                # timeout
                solverP.kill()
                return ValidationResult(False, False, "timeout")
            solverP.stdin.write("(exit)\n".encode('ascii'))
            solverP.stdin.flush()
            solverP.stdin.close()
            solverP.stdout.close()
            solverP.stderr.close()
            solverP.wait()
            responseStr = response.decode('utf-8').split('\n')[0]
            if (responseV.status == 'sat' and responseStr == 'sat') or (responseV.status == 'unsat' and responseStr == 'unsat'):
                return ValidationResult(True, True, responseStr)
            elif (responseV.status == 'sat' and responseStr == 'unsat') or (responseV.status == 'unsat' and responseStr == 'sat'):
                return ValidationResult(True, False, responseStr)
            else:
                return ValidationResult(False, False, responseStr)
        else:
            solverP.stdin.write(cmdinfo.cmd.encode('ascii'))
            solverP.stdin.write('\n'.encode('ascii'))
            solverP.stdin.flush()
            if not expect_success(solverP.stdout):
                solverP.kill()
                return ValidationResult(False, False, "solver/parser error")
    
    solverP.stdin.write("(exit)\n".encode('utf-8'))
    solverP.stdin.flush()
    solverP.stdin.close()
    solverP.stdout.close()
    solverP.stderr.close()
    solverP.wait()

    return ValidationResult(False, False, "no (check-sat) in case")
