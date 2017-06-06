# Generated from SmtLib25.g4 by ANTLR 4.5.1
from antlr4 import *
if __name__ is not None and "." in __name__:
    from .SmtLib25Parser import SmtLib25Parser
else:
    from SmtLib25Parser import SmtLib25Parser

# This class defines a complete generic visitor for a parse tree produced by SmtLib25Parser.

class SmtLib25Visitor(ParseTreeVisitor):

    # Visit a parse tree produced by SmtLib25Parser#smtfile.
    def visitSmtfile(self, ctx:SmtLib25Parser.SmtfileContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SmtLib25Parser#script.
    def visitScript(self, ctx:SmtLib25Parser.ScriptContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SmtLib25Parser#option.
    def visitOption(self, ctx:SmtLib25Parser.OptionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SmtLib25Parser#command.
    def visitCommand(self, ctx:SmtLib25Parser.CommandContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SmtLib25Parser#fun_def.
    def visitFun_def(self, ctx:SmtLib25Parser.Fun_defContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SmtLib25Parser#numeral.
    def visitNumeral(self, ctx:SmtLib25Parser.NumeralContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SmtLib25Parser#boolean.
    def visitBoolean(self, ctx:SmtLib25Parser.BooleanContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SmtLib25Parser#string.
    def visitString(self, ctx:SmtLib25Parser.StringContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SmtLib25Parser#spec_constant.
    def visitSpec_constant(self, ctx:SmtLib25Parser.Spec_constantContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SmtLib25Parser#s_expr.
    def visitS_expr(self, ctx:SmtLib25Parser.S_exprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SmtLib25Parser#identifier.
    def visitIdentifier(self, ctx:SmtLib25Parser.IdentifierContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SmtLib25Parser#index.
    def visitIndex(self, ctx:SmtLib25Parser.IndexContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SmtLib25Parser#sort.
    def visitSort(self, ctx:SmtLib25Parser.SortContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SmtLib25Parser#attribute_value.
    def visitAttribute_value(self, ctx:SmtLib25Parser.Attribute_valueContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SmtLib25Parser#attribute.
    def visitAttribute(self, ctx:SmtLib25Parser.AttributeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SmtLib25Parser#qual_identifier.
    def visitQual_identifier(self, ctx:SmtLib25Parser.Qual_identifierContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SmtLib25Parser#var_binding.
    def visitVar_binding(self, ctx:SmtLib25Parser.Var_bindingContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SmtLib25Parser#sorted_var.
    def visitSorted_var(self, ctx:SmtLib25Parser.Sorted_varContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SmtLib25Parser#term.
    def visitTerm(self, ctx:SmtLib25Parser.TermContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SmtLib25Parser#response.
    def visitResponse(self, ctx:SmtLib25Parser.ResponseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SmtLib25Parser#error_response.
    def visitError_response(self, ctx:SmtLib25Parser.Error_responseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SmtLib25Parser#check_sat_response.
    def visitCheck_sat_response(self, ctx:SmtLib25Parser.Check_sat_responseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SmtLib25Parser#get_model_response.
    def visitGet_model_response(self, ctx:SmtLib25Parser.Get_model_responseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SmtLib25Parser#model_response.
    def visitModel_response(self, ctx:SmtLib25Parser.Model_responseContext):
        return self.visitChildren(ctx)



del SmtLib25Parser