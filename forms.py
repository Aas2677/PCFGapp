from flask_wtf import FlaskForm 
from wtforms import StringField,SubmitField,TextAreaField,IntegerField,BooleanField
from wtforms.validators import DataRequired,ValidationError,Length,NumberRange
from grammars import ProbabilisticGrammar
import grammarerrors

def validate_grammar(self,grammar):

    string_representation = str(grammar.data).strip('\n')


    try:
        formal_grammar = ProbabilisticGrammar.from_string(string_representation)
        if not formal_grammar.CNF:
            print("shit")
            raise ValidationError("Your grammar is not in Chomsky normal form, check your production rules")
    except grammarerrors.StringInputException:
            raise ValidationError("Please follow the conventions for entering your grammar")

       
class  TextInputForm(FlaskForm):
    grammar = TextAreaField('Input your grammar here', render_kw={"rows": 7, "cols": 50}, validators = [DataRequired(),Length(min=2, max=2000),validate_grammar ]) # add in validators as another argument into stringfield

    sentence = TextAreaField('Input your test sentence here',render_kw={"rows": 7, "cols": 50}, validators = [ DataRequired()])
    n_parses  = IntegerField( validators = [DataRequired(),NumberRange(1,100)])
    show_total = BooleanField('Would you like to calculae the total probability of this sentence?')
    show_table = BooleanField('Show derivation table')
    submitgrammar = SubmitField('Submit to parser')
    















    # def validate_grammar(self,form,field):
    #     number = int(field.data)
    #     if number // 3 != 0:
    #         raise ValidationError("not a multipule of 3")

