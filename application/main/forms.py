from flask_wtf import FlaskForm 
from wtforms import StringField,SubmitField,TextAreaField,IntegerField,BooleanField,SelectField
from flask_wtf.file import FileField,FileRequired,FileAllowed
from wtforms.validators import DataRequired,ValidationError,Length,NumberRange
from application.main.grammars import ProbabilisticGrammar
import application.main.grammarerrors as grammarerrors
import sys 
import re

def validate_grammar(self,grammar):
    
    # Makes a preliminary validation check on the grammar input fle to make sure that passing it to the parsing structures is safe --- Does not generate noncritical warnings -- 

    string_representation_1 =  product = re.sub('\n','', re.sub('\r','',grammar.data))
    string_representation = str(grammar.data).strip('\n')
   


    try:
        formal_grammar = ProbabilisticGrammar.from_string(string_representation_1)
        number_of_rules  = len(formal_grammar.collapsed_rules)

        if number_of_rules > 200:
            raise ValidationError(f'The maximum grammar size is 200, meaning you cant have more than 200 rules. Your grammar has {number_of_rules} rules.')
        
        if not formal_grammar.CNF:
            
            raise ValidationError("Your grammar is not in Chomsky normal form, check your production rules")
    except grammarerrors.StringInputException:
            raise ValidationError("Please follow the conventions for entering your grammar")





def validate_grammar_non_prob(self,grammar):
    
    # Makes a preliminary validation check on the grammar input fle to make sure that passing it to the parsing structures is safe --- Does not generate noncritical warnings -- 

    string_representation_1 =  product = re.sub('\n','', re.sub('\r','',grammar.data))
    string_representation = str(grammar.data).strip('\n')
   


    try:
        formal_grammar = ProbabilisticGrammar.from_string(string_representation_1,probabilistic=False)
        number_of_rules  = len(formal_grammar.collapsed_rules)

        if number_of_rules > 200:
            raise ValidationError(f'The maximum grammar size is 200, meaning you cant have more than 200 rules. Your grammar has {number_of_rules} rules.')
        
        if not formal_grammar.CNF:
            
            raise ValidationError("Your grammar is not in Chomsky normal form, check your production rules")
    except grammarerrors.StringInputException:
            raise ValidationError("Please follow the conventions for entering your grammar")






def validate_sentence(self,sentence):
    
    sentence_data = re.sub('\n','', re.sub('\r','',str(sentence.data))).split(' ')

    if len(sentence_data) > 80:
        raise ValidationError(f'The size limit for test strings is 80, your test string has length {len(sentence_data)}')


       
class  TextInputForm(FlaskForm):
    #Input form for free text probabilistic grammars
    grammar = TextAreaField('Grammar input', render_kw={"rows": 10, "cols": 50}, validators = [DataRequired(),Length(min=2, max=10000),validate_grammar ]) # add in validators as another argument into stringfield

    sentence = TextAreaField('String input ',render_kw={"rows": 6, "cols": 50}, validators = [ DataRequired(),validate_sentence])
    n_parses  = IntegerField( validators = [DataRequired(),NumberRange(1,100)])
    show_total = BooleanField('Calulcate total probability')
    show_table = BooleanField('Show  leftmost derivation table')
    submitgrammar = SubmitField('Submit')



class  TextInputFormNon(FlaskForm):
    #Input form for non-probabilistic free-text grammars
    grammar = TextAreaField('Grammar input', render_kw={"rows": 10, "cols": 50}, validators = [DataRequired(),Length(min=2, max=10000),validate_grammar_non_prob ]) # add in validators as another argument into stringfield

    sentence = TextAreaField('String input ',render_kw={"rows": 6, "cols": 50}, validators = [ DataRequired(),validate_sentence])
    n_parses  = IntegerField( validators = [DataRequired(),NumberRange(1,100)])
    show_table = BooleanField('Show  leftmost derivation table')
    submitgrammar = SubmitField('Submit')


class  FileInputForm(FlaskForm):
    #Input form for probabilistic file input grammars
    grammar_file = FileField('Grammar file input' , validators = [FileRequired(),FileAllowed(['json'], '.json files only')]) # add in validators as another argument into stringfield

    sentence = TextAreaField('String input',render_kw={"rows": 7, "cols": 50}, validators = [ DataRequired(),validate_sentence])
    n_parses  = IntegerField( validators = [DataRequired(),NumberRange(1,100)])
    show_total = BooleanField('Would you like to calculae the total probability of this sentence?')
    show_table = BooleanField('Show derivation table')
    submitgrammar = SubmitField('Submit')


class  FileInputFormNon(FlaskForm):
    #Input form for non-probabilistic file input grammars
    grammar_file = FileField('Grammar file input' , validators = [FileRequired(),FileAllowed(['json'], '.json files only')]) # add in validators as another argument into stringfield

    sentence = TextAreaField('String input',render_kw={"rows": 7, "cols": 50}, validators = [ DataRequired(),validate_sentence])
    n_parses  = IntegerField( validators = [DataRequired(),NumberRange(1,100)])
    show_table = BooleanField('Show  leftmost derivation table')
    submitgrammar = SubmitField('Submit')
    
    
    
    













