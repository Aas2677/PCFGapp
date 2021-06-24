from flask_wtf import FlaskForm 
from wtforms import StringField,SubmitField,TextAreaField
from wtforms.validators import DataRequired,ValidationError,Length
from grammars import ProbabilisticGrammar
import grammarerrors

def validate_grammar(self,grammar):

    string_representation = str(grammar.data).strip('\n')


    try:
        formal_grammar = ProbabilisticGrammar.from_string(string_representation)
        if not formal_grammar.CNF:
            raise ValidationError("Your grammar is not in Chomsky normal form, check your production rules")
    except grammarerrors.StringInputException:
            raise ValidationError("Please follow the conventions for entering your grammar")

       
class  TextInputForm(FlaskForm):
    grammar = TextAreaField('Input your grammar here', render_kw={"rows": 7, "cols": 100}, validators = [DataRequired(),Length(min=2, max=2000),validate_grammar ]) # add in validators as another argument into stringfield 
    sentence = StringField('Input your test sentence here')
    submitgrammar = SubmitField('Validate grammar')
    submitsentence = SubmitField('Check if all words are in the grammar')
















    # def validate_grammar(self,form,field):
    #     number = int(field.data)
    #     if number // 3 != 0:
    #         raise ValidationError("not a multipule of 3")

