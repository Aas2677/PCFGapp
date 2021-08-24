from application.main.parsing import *
from application.main.grammars import ProbabilisticGrammar
import application.main.grammarerrors as grammarerrors

from application.main.forms import TextInputForm,FileInputForm, TextInputFormNon, FileInputFormNon
from flask import url_for,render_template,flash,redirect,g,abort,request,current_app
from flask import Blueprint 
import json
import sys 
import re 

main = Blueprint('main',__name__)

def flash_errors(form):
    """Flashes form errors"""
    for field, errors in form.errors.items():
        for error in errors:
            flash(u"Error in the %s field - %s." % (
                getattr(form, field).label.text,
                error
            ), '3')




@main.route("/home",methods=['GET','POST'])
def home():
    return render_template('mainopen.html')


@main.route("/",methods=['GET','POST'])
@main.route("/string_input",methods=['GET','POST'])
def string_input():
       print("hello")
    
       form = TextInputForm() 
   
       grammar = 0 
       sentence = 0 
       accepted = False
       parses = []
       data = {}
       total = False
       tables = 0
       number_of_parses = False
       comparison_mode = False 

       if form.validate_on_submit():
           grammar = re.sub('\n','', re.sub('\r','',str(form.grammar.data)))
      
           sentence = re.sub('\n','', re.sub('\r','',str(form.sentence.data)))
           number_of_parses = int(form.n_parses.data)
           total_needed = not form.show_total.data
           table_needed = not form.show_table.data 
           comparison = form.comparison_mode.data 
          
           # if comparison mode is on, then we can ignore the tables 
           if comparison:
              
               comparison_mode = True 
               table_needed = False

           
        
           # setup the parser:
           grammar_object = ProbabilisticGrammar.from_string(grammar)
           parser = ProbabilisticCYKParser(grammar_object)
           try:
               data = {}
            
               raw_parses = parser.n_best_parses(number_of_parses,sentence)
               best_parse = raw_parses[0]
               count = best_parse.counter 
               # if total is needed, pull it out of the best best
               if total_needed:
                   total = best_parse.tracker_probability
              
               
               parses = [parse.get_full_tree() for parse in raw_parses]
               parses_d = [parse.get_full_tree(table=True) for parse in raw_parses]
            
            
    
                  

               # only generate the leftmost derivation tables if the user wants them 
               if table_needed:
                   # lots of duplicate work done in the derivation builders, should come back to refactor 
                   # tables = [get_derivation_table(parse,grammar_object.processed_rules) for parse in parses_d]
                   tables = json.dumps({i+1: get_derivation_table(parse,grammar_object.processed_rules) for i,parse in enumerate(parses_d)})
                   pass 


               for i in range(len(parses)):
                   data[i+1] = parses[i]
            
               accepted = True
               flash("Your sentence is accepted by this grammar.",'1')

               if len(parses) < int(number_of_parses):
                   if len(parses) == 1:
                       flash(f'This sentence is unambiguous, meaning that there is only one way to parse the sentence and only 1 unique leftmost derivation','2')
                   else:
                        flash(f'There are only {len(parses)} ways to parse this sentence, so {number_of_parses} cannot be given.','2')
               else:
                  flash(f'There are {count} ways to parse this sentence.','1')

                          

               if not grammar_object.consistent:
                   flash(' Warning - your grammar is inconsistent. Parsing can see be carried out, but there will not be a proper probability distribution over parses.','2')

               if grammar_object.ignored_rules:
                    flash ('Warning - some rules in your grammar were ignored as duplicates or incorrect construction.','2')

               # set number of parses to number actually generated 
               number_of_parses = len(parses)
           except Exception as e:
               print(e)
               
           

              
               flash('Your input sentence is not accepted by this grammar.','3')
               accepted = False


       else:
           flash_errors(form)
           grammar = 0 
           sentence = 0  

       return render_template('mainpage_string.html',title = 'PCFG exporer',form = form,m=grammar,sentence=sentence,parses=json.dumps(data),accepted=accepted,total = total, num_parses = number_of_parses,tables=tables,comparison_mode=comparison_mode)
       

@main.route("/non_prob_string_input",methods=['GET','POST'])
def non_prob_string_input():
    
       form = TextInputFormNon() 
   
       grammar = 0 
       sentence = 0 
       accepted = False
       parses = []
       data = {}
       total=False
       tables = 0
       number_of_parses = False   
       comparison_mode = False 
       if form.validate_on_submit():
           grammar = re.sub('\n','', re.sub('\r','',str(form.grammar.data)))
           sentence = re.sub('\n','', re.sub('\r','',str(form.sentence.data)))
           number_of_parses = int(form.n_parses.data)
           table_needed =  not form.show_table.data
           comparison = form.comparison_mode.data 
          
           # if comparison mode is on, then we can ignore the tables 
           if comparison:
              
               comparison_mode = True 
               table_needed = False

           
        
           # setup the parser:
           grammar_object = ProbabilisticGrammar.from_string(grammar,probabilistic=False)
           parser = ProbabilisticCYKParser(grammar_object)
           try:
               data = {}
            
               raw_parses = parser.n_best_parses(number_of_parses,sentence)
               best_parse = raw_parses[0]
               parses = [parse.get_full_tree() for parse in raw_parses]
               parses_d = [parse.get_full_tree(table=True) for parse in raw_parses]
               count = best_parse.counter
            
            
        
               # only generate the leftmost derivation tables if the user wants them 
               if table_needed:
                   # lots of duplicate work done in the derivation builders, should come back to refactor 
                   # tables = [get_derivation_table(parse,grammar_object.processed_rules) for parse in parses_d]
                   tables = json.dumps({i+1: get_derivation_table(parse,grammar_object.processed_rules) for i,parse in enumerate(parses_d)})
                   pass 


               for i in range(len(parses)):
                   data[i+1] = parses[i]
            
               accepted = True
               flash("Your sentence is accepted by this grammar.",'1')

               if len(parses) < int(number_of_parses):

                    if len(parses) == 1:
                       flash(f'This sentence is unambiguous, meaning that there is only one way to parse the sentence and only 1 unique leftmost derivation','2')
                    else:
                        flash(f'There are only {len(parses)} ways to parse this sentence, so {number_of_parses} cannot be given.','2')
               else:
                   flash(f'There are {count} ways to parse this sentence.','1')

                           

          
               if grammar_object.ignored_rules:
                    flash ('Warning - some rules in your grammar were ignored as duplicates or incorrect construction.','2')

               # set number of parses to number actually generated 
               number_of_parses = len(parses)
           except Exception as e:
               
               
               flash('Your input sentence is not accepted by this grammar.','3')
               accepted = False


       else:
           flash_errors(form)
           grammar = 0 
           sentence = 0  

       return render_template('non_prob_string.html',title = 'PCFG exporer',form = form,m=grammar,sentence=sentence,parses=json.dumps(data),accepted=accepted,total = total, num_parses = number_of_parses,tables=tables,comparison_mode=comparison_mode)

@main.route("/file_input",methods=['GET','POST'])
def file_input():
    
       form = FileInputForm() 
   
       grammar = 0 
       sentence = 0 
       accepted = False
       parses = []
       data = {}
       total = False
       tables = 0
       number_of_parses = False  
       consistent = True  
       comparison_mode = False 
       if form.validate_on_submit():
           try:
               
               grammar = form.grammar_file.data
               
               
               
               sentence = re.sub('\n','', re.sub('\r','',str(form.sentence.data)))
            
               number_of_parses = int(form.n_parses.data)
               total_needed = not form.show_total.data
               table_needed = not form.show_table.data 
               comparison = form.comparison_mode.data 
          
               # if comparison mode is on, then we can ignore the tables 
               if comparison:
              
                   comparison_mode = True 
                   table_needed = False

               
    
            
               # setup the parser:
               grammar_object = ProbabilisticGrammar.from_json(grammar)
               parser = ProbabilisticCYKParser(grammar_object)

               # check the number of rules in the grammar 
               number_of_rules  = len(grammar_object.collapsed_rules)

               if grammar_object.CNF and number_of_rules <= 200:
                  

                   try:
                       data = {}
                    
                       raw_parses = parser.n_best_parses(number_of_parses,sentence)
                       best_parse = raw_parses[0]
                       count = best_parse.counter 
                       # if total is needed, pull it out of the best best parse
                       if total_needed:
                           total = best_parse.tracker_probability
                      
                       parses = [parse.get_full_tree() for parse in raw_parses]
                       parses_d = [parse.get_full_tree(table=True) for parse in raw_parses]
                            
                    
                    
                       
                       # only generate the leftmost derivation tables if the user wants them 
                       if table_needed:
                         
                           tables = json.dumps({i+1: get_derivation_table(parse,grammar_object.processed_rules) for i,parse in enumerate(parses_d)})
                           pass 
        
        
                       for i in range(len(parses)):
                           data[i+1] = parses[i]
                    
                       accepted = True
                       flash("Your sentence is accepted by this grammar.",'1')
                      

                       if len(parses) < int(number_of_parses):
                            if len(parses) == 1:
                                flash(f'This sentence is unambiguous, meaning that there is only one way to parse the sentence and only 1 unique leftmost derivation','2')
                            else:
                                 flash(f'There are only {len(parses)} ways to parse this sentence, so {number_of_parses} cannot be given.','2')
                       else:
                             flash(f'There are {count} ways to parse this sentence.','1')

                       if not grammar_object.consistent:
                           flash(' Warning - your grammar is inconsistent. Parsing can see be carried out, but there will not be a proper probability distribution over parses.','2')
        
                       if grammar_object.ignored_rules:
                            flash ('Warning - some rules in your grammar were ignored as duplicates or incorrect construction.','2')

                       # set number of parses to number actually generated 
                       number_of_parses = len(parses)
                   except Exception as e :
                       
                  
                       flash('Your input sentence is not accepted by this grammar.','3')
                       accepted = False
                    
               else:
                   if not grammar_object.CNF:

                       flash("Your grammar is not in chomksy normal form, refer to the guide for more informmation.",'3')
                   if number_of_rules > 200:
                       flash(f'The maximum grammar size is 200, meaning you cant have more than 200 rules. Your grammar has {number_of_rules} rules.')


           except Exception as e:
               flash(f'There is a problem with your JSON file structure. Please read the structure guide:{e}','3')

       

       else:
           flash_errors(form)
           grammar = 0 
           sentence = 0  
        

       return render_template('mainpage_file.html',title = 'PCFG exporer',form = form,m=grammar,sentence=sentence,parses=json.dumps(data),accepted=accepted,total = total, num_parses = number_of_parses,tables=tables,comparison_mode=comparison_mode)



@main.route("/non_prob_file_input",methods=['GET','POST'])
def non_prob_file_input():
    
       form = FileInputFormNon() 
   
       grammar = 0 
       sentence = 0 
       accepted = False
       parses = []
       data = {}
       total = False
       tables = 0
       number_of_parses = False  
       consistent = True  
       comparison_mode = False 
       if form.validate_on_submit():
           try:
               
               grammar = form.grammar_file.data
               
               
               
               sentence = re.sub('\n','', re.sub('\r','',str(form.sentence.data)))
            
               number_of_parses = int(form.n_parses.data)
               table_needed =  not form.show_table.data 
               comparison = form.comparison_mode.data 
          
               # if comparison mode is on, then we can ignore the tables 
               if comparison:
                  
                   comparison_mode = True 
                   table_needed = False

               
    
            
               # setup the parser:
               grammar_object = ProbabilisticGrammar.from_json(grammar,probabilistic=False)
               parser = ProbabilisticCYKParser(grammar_object)

               # check the number of rules in the grammar 
               number_of_rules  = len(grammar_object.collapsed_rules)

               if grammar_object.CNF and number_of_rules <= 200:
                  

                   try:
                       data = {}
                    
                       raw_parses = parser.n_best_parses(number_of_parses,sentence)
                       best_parse = raw_parses[0]
                       parses = [parse.get_full_tree() for parse in raw_parses]
                       parses_d = [parse.get_full_tree(table=True) for parse in raw_parses]
                       count = best_parse.counter
                    
                    
                    
                     
        
                       # only generate the leftmost derivation tables if the user wants them 
                       if table_needed:
                           # lots of duplicate work done in the derivation builders, should come back to refactor 
                           # tables = [get_derivation_table(parse,grammar_object.processed_rules) for parse in parses_d]
                           tables = json.dumps({i+1: get_derivation_table(parse,grammar_object.processed_rules) for i,parse in enumerate(parses_d)})
                           pass 
        
        
                       for i in range(len(parses)):
                           data[i+1] = parses[i]
                    
                       accepted = True
                       flash("Your sentence is accepted by this grammar.",'1')
                      

                       if len(parses) < int(number_of_parses):
                           
                           if len(parses) == 1:
                                flash(f'This sentence is unambiguous, meaning that there is only one way to parse the sentence and only 1 unique leftmost derivation','2')
                           else:
                                 flash(f'There are only {len(parses)} ways to parse this sentence, so {number_of_parses} cannot be given.','2')
                       else:
                           flash(f'There are {count} ways to parse this sentence.','1')
               
         
        
                       if grammar_object.ignored_rules:
                            flash ('Warning - some rules in your grammar were ignored as duplicates or incorrect construction.','2')

                       # set number of parses to number actually generated 
                       number_of_parses = len(parses)
                   except Exception as e :
                       
                  
                       flash('Your input sentence is not accepted by this grammar.','3')
                       accepted = False
                    
               else:
                   if not grammar_object.CNF:

                       flash("Your grammar is not in chomksy normal form, refer to the guide for more informmation.",'3')
                   if number_of_rules > 200:
                       flash(f'The maximum grammar size is 200, meaning you cant have more than 200 rules. Your grammar has {number_of_rules} rules.')


           except Exception as e:
               flash(f'There is a problem with your JSON file structure. Please read the structure guide:{e}','3')

       

       else:
           flash_errors(form)
           grammar = 0 
           sentence = 0  
        

       return render_template('non_prob_file.html',title = 'PCFG exporer',form = form,m=grammar,sentence=sentence,parses=json.dumps(data),accepted=accepted,total = total, num_parses = number_of_parses,tables=tables,comparison_mode=comparison_mode)


