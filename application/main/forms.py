from flask_wtf import FlaskForm 
from wtforms import StringField,SubmitField,TextAreaField,IntegerField,BooleanField,SelectField
from flask_wtf.file import FileField,FileRequired,FileAllowed
from wtforms.validators import DataRequired,ValidationError,Length,NumberRange
from application.main.grammars import ProbabilisticGrammar
import application.main.grammarerrors as grammarerrors
import sys 

def validate_grammar(self,grammar):
    
    # Makes a preliminary validation check on the grammar input fle to make sure that passing it to the parsing structures is safe --- Does not generate noncritical warnings -- 

    string_representation = str(grammar.data).strip('\n')


    try:
        formal_grammar = ProbabilisticGrammar.from_string(string_representation)
        
        if not formal_grammar.CNF:
            
            raise ValidationError("Your grammar is not in Chomsky normal form, check your production rules")
    except grammarerrors.StringInputException:
            raise ValidationError("Please follow the conventions for entering your grammar")


def validate_file(self,grammar_file):
    # Cannot use. Reads json byte stream so it cannnot be read again by the route function. validation must be done by the route function. 
  
    try:
        print(grammar_file.data)
        print(sys.getsizeof(grammar_file))
        formal_grammar = ProbabilisticGrammar.from_json(grammar_file.data)
        print(formal_grammar.alphabet)
        if not formal_grammar.CNF:
            
           
            raise ValidationError("Your grammar is not in Chomsky normal form, check your production rules")
    except Exception as e:
       
        raise ValidationError(f'There is an error in your JSON file structure: {e}')

       
class  TextInputForm(FlaskForm):
    grammar = TextAreaField('Grammar input', render_kw={"rows": 10, "cols": 50}, validators = [DataRequired(),Length(min=2, max=2000),validate_grammar ]) # add in validators as another argument into stringfield

    sentence = TextAreaField('String input ',render_kw={"rows": 6, "cols": 50}, validators = [ DataRequired()])
    n_parses  = IntegerField( validators = [DataRequired(),NumberRange(1,100)])
    show_total = BooleanField('Calulcate total probability')
    show_table = BooleanField('Show  leftmost derivation table')
    submitgrammar = SubmitField('Submit')


class  FileInputForm(FlaskForm):
    grammar_file = FileField('Grammar file input' , validators = [FileRequired(),FileAllowed(['json'], '.json files only')]) # add in validators as another argument into stringfield

    sentence = TextAreaField('Input your test sentence here',render_kw={"rows": 7, "cols": 50}, validators = [ DataRequired()])
    n_parses  = IntegerField( validators = [DataRequired(),NumberRange(1,100)])
    show_total = BooleanField('Would you like to calculae the total probability of this sentence?')
    show_table = BooleanField('Show derivation table')
    submitgrammar = SubmitField('Submit')
    
    













