# Generated from SmtLib25.g4 by ANTLR 4.5.1
from antlr4 import *
if __name__ is not None and "." in __name__:
    from .SmtLib25Parser import SmtLib25Parser
else:
    from SmtLib25Parser import SmtLib25Parser

# This class defines a complete listener for a parse tree produced by SmtLib25Parser.
class SmtLib25Listener(ParseTreeListener):

    # Enter a parse tree produced by SmtLib25Parser#smtfile.
    def enterSmtfile(self, ctx:SmtLib25Parser.SmtfileContext):
        pass

    # Exit a parse tree produced by SmtLib25Parser#smtfile.
    def exitSmtfile(self, ctx:SmtLib25Parser.SmtfileContext):
        pass


    # Enter a parse tree produced by SmtLib25Parser#script.
    def enterScript(self, ctx:SmtLib25Parser.ScriptContext):
        pass

    # Exit a parse tree produced by SmtLib25Parser#script.
    def exitScript(self, ctx:SmtLib25Parser.ScriptContext):
        pass


    # Enter a parse tree produced by SmtLib25Parser#option.
    def enterOption(self, ctx:SmtLib25Parser.OptionContext):
        pass

    # Exit a parse tree produced by SmtLib25Parser#option.
    def exitOption(self, ctx:SmtLib25Parser.OptionContext):
        pass


    # Enter a parse tree produced by SmtLib25Parser#command.
    def enterCommand(self, ctx:SmtLib25Parser.CommandContext):
        pass

    # Exit a parse tree produced by SmtLib25Parser#command.
    def exitCommand(self, ctx:SmtLib25Parser.CommandContext):
        pass


    # Enter a parse tree produced by SmtLib25Parser#fun_def.
    def enterFun_def(self, ctx:SmtLib25Parser.Fun_defContext):
        pass

    # Exit a parse tree produced by SmtLib25Parser#fun_def.
    def exitFun_def(self, ctx:SmtLib25Parser.Fun_defContext):
        pass


    # Enter a parse tree produced by SmtLib25Parser#numeral.
    def enterNumeral(self, ctx:SmtLib25Parser.NumeralContext):
        pass

    # Exit a parse tree produced by SmtLib25Parser#numeral.
    def exitNumeral(self, ctx:SmtLib25Parser.NumeralContext):
        pass


    # Enter a parse tree produced by SmtLib25Parser#boolean.
    def enterBoolean(self, ctx:SmtLib25Parser.BooleanContext):
        pass

    # Exit a parse tree produced by SmtLib25Parser#boolean.
    def exitBoolean(self, ctx:SmtLib25Parser.BooleanContext):
        pass


    # Enter a parse tree produced by SmtLib25Parser#string.
    def enterString(self, ctx:SmtLib25Parser.StringContext):
        pass

    # Exit a parse tree produced by SmtLib25Parser#string.
    def exitString(self, ctx:SmtLib25Parser.StringContext):
        pass


    # Enter a parse tree produced by SmtLib25Parser#spec_constant.
    def enterSpec_constant(self, ctx:SmtLib25Parser.Spec_constantContext):
        pass

    # Exit a parse tree produced by SmtLib25Parser#spec_constant.
    def exitSpec_constant(self, ctx:SmtLib25Parser.Spec_constantContext):
        pass


    # Enter a parse tree produced by SmtLib25Parser#s_expr.
    def enterS_expr(self, ctx:SmtLib25Parser.S_exprContext):
        pass

    # Exit a parse tree produced by SmtLib25Parser#s_expr.
    def exitS_expr(self, ctx:SmtLib25Parser.S_exprContext):
        pass


    # Enter a parse tree produced by SmtLib25Parser#identifier.
    def enterIdentifier(self, ctx:SmtLib25Parser.IdentifierContext):
        pass

    # Exit a parse tree produced by SmtLib25Parser#identifier.
    def exitIdentifier(self, ctx:SmtLib25Parser.IdentifierContext):
        pass


    # Enter a parse tree produced by SmtLib25Parser#index.
    def enterIndex(self, ctx:SmtLib25Parser.IndexContext):
        pass

    # Exit a parse tree produced by SmtLib25Parser#index.
    def exitIndex(self, ctx:SmtLib25Parser.IndexContext):
        pass


    # Enter a parse tree produced by SmtLib25Parser#sort.
    def enterSort(self, ctx:SmtLib25Parser.SortContext):
        pass

    # Exit a parse tree produced by SmtLib25Parser#sort.
    def exitSort(self, ctx:SmtLib25Parser.SortContext):
        pass


    # Enter a parse tree produced by SmtLib25Parser#attribute_value.
    def enterAttribute_value(self, ctx:SmtLib25Parser.Attribute_valueContext):
        pass

    # Exit a parse tree produced by SmtLib25Parser#attribute_value.
    def exitAttribute_value(self, ctx:SmtLib25Parser.Attribute_valueContext):
        pass


    # Enter a parse tree produced by SmtLib25Parser#attribute.
    def enterAttribute(self, ctx:SmtLib25Parser.AttributeContext):
        pass

    # Exit a parse tree produced by SmtLib25Parser#attribute.
    def exitAttribute(self, ctx:SmtLib25Parser.AttributeContext):
        pass


    # Enter a parse tree produced by SmtLib25Parser#qual_identifier.
    def enterQual_identifier(self, ctx:SmtLib25Parser.Qual_identifierContext):
        pass

    # Exit a parse tree produced by SmtLib25Parser#qual_identifier.
    def exitQual_identifier(self, ctx:SmtLib25Parser.Qual_identifierContext):
        pass


    # Enter a parse tree produced by SmtLib25Parser#var_binding.
    def enterVar_binding(self, ctx:SmtLib25Parser.Var_bindingContext):
        pass

    # Exit a parse tree produced by SmtLib25Parser#var_binding.
    def exitVar_binding(self, ctx:SmtLib25Parser.Var_bindingContext):
        pass


    # Enter a parse tree produced by SmtLib25Parser#sorted_var.
    def enterSorted_var(self, ctx:SmtLib25Parser.Sorted_varContext):
        pass

    # Exit a parse tree produced by SmtLib25Parser#sorted_var.
    def exitSorted_var(self, ctx:SmtLib25Parser.Sorted_varContext):
        pass


    # Enter a parse tree produced by SmtLib25Parser#term.
    def enterTerm(self, ctx:SmtLib25Parser.TermContext):
        pass

    # Exit a parse tree produced by SmtLib25Parser#term.
    def exitTerm(self, ctx:SmtLib25Parser.TermContext):
        pass


    # Enter a parse tree produced by SmtLib25Parser#response.
    def enterResponse(self, ctx:SmtLib25Parser.ResponseContext):
        pass

    # Exit a parse tree produced by SmtLib25Parser#response.
    def exitResponse(self, ctx:SmtLib25Parser.ResponseContext):
        pass


    # Enter a parse tree produced by SmtLib25Parser#error_response.
    def enterError_response(self, ctx:SmtLib25Parser.Error_responseContext):
        pass

    # Exit a parse tree produced by SmtLib25Parser#error_response.
    def exitError_response(self, ctx:SmtLib25Parser.Error_responseContext):
        pass


    # Enter a parse tree produced by SmtLib25Parser#check_sat_response.
    def enterCheck_sat_response(self, ctx:SmtLib25Parser.Check_sat_responseContext):
        pass

    # Exit a parse tree produced by SmtLib25Parser#check_sat_response.
    def exitCheck_sat_response(self, ctx:SmtLib25Parser.Check_sat_responseContext):
        pass


    # Enter a parse tree produced by SmtLib25Parser#get_model_response.
    def enterGet_model_response(self, ctx:SmtLib25Parser.Get_model_responseContext):
        pass

    # Exit a parse tree produced by SmtLib25Parser#get_model_response.
    def exitGet_model_response(self, ctx:SmtLib25Parser.Get_model_responseContext):
        pass


    # Enter a parse tree produced by SmtLib25Parser#model_response.
    def enterModel_response(self, ctx:SmtLib25Parser.Model_responseContext):
        pass

    # Exit a parse tree produced by SmtLib25Parser#model_response.
    def exitModel_response(self, ctx:SmtLib25Parser.Model_responseContext):
        pass


