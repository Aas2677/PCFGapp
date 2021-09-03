from decimal import *
from flask_wtf.form import FlaskForm
from application.main.grammarerrors import *
from application.main.parsing import *
from application.main.grammars import ProbabilisticGrammar
from application.main.aux  import pretty_display_number as pretty
import application.main.grammarerrors as grammarerrors

from application.main.forms import TextInputForm,FileInputForm, TextInputFormNon, FileInputFormNon
from flask import url_for,render_template,flash,redirect,g,abort,request,current_app
from flask import Blueprint 
import json
import sys 
import re 




"""
Contains all the routing information for the web application. Note that all interactions with the grammars and parsing logc is handled via the responde_handler object.

"""

# set the decimal context for rendering probabilites 
context = Context(prec=8,  Emin=-999999, Emax=999999,
        capitals=1, clamp=0, flags=[], traps=[Overflow, DivisionByZero,
        InvalidOperation])


# get the main blueprint
main = Blueprint('main',__name__)






@main.route("/home",methods=['GET','POST'])
def home():
    # Route for the information page
    return render_template('mainopen.html')







@main.route("/",methods=['GET','POST'])
@main.route("/string_input",methods=['GET','POST'])
def string_input():

    ## Default route ## 
    ## route for probabilistic grammars in free text fromat ##
      
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
    nodes = 0 
    
    if form.validate_on_submit():

        response_handler = response_builder(form,"probabilistic_string_input",True,False)
        try:
            grammar,sentence,accepted,parses,data,total,tables,number_of_parses,comparison_mode,nodes = response_handler.build_repsonse()

            if response_handler.major_flags:
                # If there are major flags that would stop the parser from functioning correctly, give these warnings to the user.
                for flag in response_handler.critial_errors:
                    flash(flag,'3')
            
            else: 
                # Parsing was successful and we can proceed to give the user confirmaiton information and non-critical warnings

                for message in response_handler.confirmation_messages:
                    flash(message,'1')

                for warning in response_handler.non_critial_errors:
                    flash(warning,'2')


        except Exception as e: 
      
            flash('Your grammar input could not be intepreted. Please check the syntax guide and check for issues.','3')
    else:
        # if theres an error in the input form, caught be preliminary checks, flash these errors 
        flash_errors(form)
    
    
    
    return render_template('mainpage_string.html',title = 'PCFG exporer',form = form,m=grammar,sentence=sentence,parses=json.dumps(data),accepted=accepted,total = total, num_parses = number_of_parses,tables=tables,comparison_mode=comparison_mode,num_nodes=nodes)









@main.route("/non_prob_string_input",methods=['GET','POST'])
def non_prob_string_input():
    ## rotue for non-probabilistic grammars using free text input 
    
        form = TextInputFormNon() 
   
        grammar = 0 
        sentence = 0 
        accepted = False
        parses = []
        data = {}
        total = False
        tables = 0
        number_of_parses = False  
        nodes = 0 
       
        comparison_mode = False 
        if form.validate_on_submit():
    
            response_handler = response_builder(form,"probabilistic_string_input",False,False)
            try:
                grammar,sentence,accepted,parses,data,total,tables,number_of_parses,comparison_mode,nodes = response_handler.build_repsonse()
    
                if response_handler.major_flags:
                    # If there are major flags that would stop the parser from functioning correctly, give these warnings to the user.
                    for flag in response_handler.critial_errors:
                        flash(flag,'3')
                
                else: 
                    # Parsing was successful and we can proceed to give the user confirmaiton information and non-critical warnings
    
                    for message in response_handler.confirmation_messages:
                        flash(message,'1')
    
                    for warning in response_handler.non_critial_errors:
                        flash(warning,'2')
    
    
            except Exception as e: 
              
                flash('Your grammar input could not be intepreted. Please check the syntax guide and check for issues.','3')
        else:
            # if theres an error in the input form, caught be preliminary checks, flash these errors 
            flash_errors(form)
        
        
        
        return render_template('non_prob_string.html',title = 'PCFG exporer',form = form,m=grammar,sentence=sentence,parses=json.dumps(data),accepted=accepted,total = total, num_parses = number_of_parses,tables=tables,comparison_mode=comparison_mode,num_nodes=nodes)














@main.route("/file_input",methods=['GET','POST'])
def file_input():
      ## Route for probabilistic grammars in file input mode ##
    
       form = FileInputForm() 

       grammar = 0 
       sentence = 0 
       accepted = False
       parses = []
       data = {}
       total = False
       tables = 0
       number_of_parses = False  
       nodes =  0
      
       comparison_mode = False 
       if form.validate_on_submit():
   
           response_handler = response_builder(form,"probabilistic_string_input",True,True)
           try:
               grammar,sentence,accepted,parses,data,total,tables,number_of_parses,comparison_mode,nodes = response_handler.build_repsonse()
   
               if response_handler.major_flags:
                   # If there are major flags that would stop the parser from functioning correctly, give these warnings to the user.
                   for flag in response_handler.critial_errors:
                       flash(flag,'3')
               
               else: 
                   # Parsing was successful and we can proceed to give the user confirmaiton information and non-critical warnings
   
                   for message in response_handler.confirmation_messages:
                       flash(message,'1')
   
                   for warning in response_handler.non_critial_errors:
                       flash(warning,'2')
   
   
           except Exception as e: 
              
               flash('Your grammar input could not be intepreted. Please check the syntax guide and check for issues.','3')
       else:
           # if theres an error in the input form, caught be preliminary checks, flash these errors 
           flash_errors(form)
       
       
       
       return render_template('mainpage_file.html',title = 'PCFG exporer',form = form,m=grammar,sentence=sentence,parses=json.dumps(data),accepted=accepted,total = total, num_parses = number_of_parses,tables=tables,comparison_mode=comparison_mode,num_nodes=nodes)

  








@main.route("/non_prob_file_input",methods=['GET','POST'])
def non_prob_file_input():
       ## route for non-probabilistic grammars using file input
    
       form = FileInputFormNon() 


       grammar = 0 
       sentence = 0 
       accepted = False
       parses = []
       data = {}
       total = False
       tables = 0
       number_of_parses = False  
       nodes = 0 
      
       comparison_mode = False 
       if form.validate_on_submit():
   
           response_handler = response_builder(form,"probabilistic_string_input",False,True)
           try:
               grammar,sentence,accepted,parses,data,total,tables,number_of_parses,comparison_mode,nodes = response_handler.build_repsonse()
   
               if response_handler.major_flags:
                   # If there are major flags that would stop the parser from functioning correctly, give these warnings to the user.
                   for flag in response_handler.critial_errors:
                       flash(flag,'3')
               
               else: 
                   # Parsing was successful and we can proceed to give the user confirmaiton information and non-critical warnings
   
                   for message in response_handler.confirmation_messages:
                       flash(message,'1')
   
                   for warning in response_handler.non_critial_errors:
                       flash(warning,'2')
   
   
           except Exception as e: 
    
               flash('Your grammar input could not be intepreted. Please check the syntax guide and check for issues.','3')
       else:
           # if theres an error in the input form, caught be preliminary checks, flash these errors 
           flash_errors(form)
       
       
       
       return render_template('non_prob_file.html',title = 'PCFG exporer',form = form,m=grammar,sentence=sentence,parses=json.dumps(data),accepted=accepted,total = total, num_parses = number_of_parses,tables=tables,comparison_mode=comparison_mode,num_nodes=nodes)








#### Helper classes and functions ########################

class response_builder:
     """ Helps to deal with collecting calling the back-end so that the route functions don't have to do this explicitly and repeat a lot of code
        Builds the logic needed for the routes to return the correct response. Also helps collect error messages in an ordered fashion"""


     def __init__(self,form:FlaskForm,route:str,probabilistic:bool,file:bool) -> None:
            
            self.form = form 
            self.route = route 
            self.probabilistic = probabilistic 
            self.file = file 
            # Hold critial and non critical errors in seperate lists 
            self.confirmation_messages = [] 
            self.non_critial_errors = [] 
            self.critial_errors = []
            self.accepted = True 
            self.major_flags = False






     def build_repsonse(self):

         # Builds response from server based on information provided

         # set initial flags 
         grammar = 0 
         sentence = 0 
         accepted = False
         parses = []
         data = {}
         total = False
         tables = 0
         number_of_parses = False  
         comparison_mode = False 
         nodes = 0 
         

         try: 
             # Get the grammar data from the form and create our grammar object accordning to file/text and probabilistic/non probabilistic modes 
             if self.file:
                 grammar = self.form.grammar_file.data 
                 if self.probabilistic:
                    grammar_object = ProbabilisticGrammar.from_json(grammar)
                 else: 
                    grammar_object = ProbabilisticGrammar.from_json(grammar,probabilistic=False)
             else: 
                grammar = re.sub('\n','', re.sub('\r','',str(self.form.grammar.data)))
                if self.probabilistic:
                    grammar_object = ProbabilisticGrammar.from_string(grammar)
                else: 
                    grammar_object = ProbabilisticGrammar.from_string(grammar,probabilistic=False)

             parser = ProbabilisticCYKParser(grammar_object)

         except Exception as e: 
             self.major_flags = True 
             raise StringInputException("There is a major syntax error in your gramamr file or input string")
    
    
        

        # No problems creating the grammar object and parser object:



      

         # get the test string 
         sentence = re.sub('\n','', re.sub('\r','',str(self.form.sentence.data)))


         # get the required number of parses 
         number_of_parses = int(self.form.n_parses.data)

         # if we have a probabilistic grammar, check if the user asked for total probability 
         if self.probabilistic:
             total_needed = not self.form.show_total.data

        
         # check if tables are required 
         table_needed = not self.form.show_table.data   
 
         # comparison mode or not
         comparison = self.form.comparison_mode.data 
         if comparison:
             comparison_mode = True 
             table_needed = False 


         # set major error flags before attempting to parse 
         if not grammar_object.CNF:
             self.major_flags = True 
             self.critical_errors.append("Your grammar is not in Chomsky normal form, check your production rules")
        
         if not grammar_object.correct_terminal_size:
             self.major_flags = True 
             self.critial_errors.append("One or more of your terminals has more than the 18 character limit. Please change this in order to parse using this grammar.")


         if not grammar_object.correct_nonterminal_size:
             self.major_flags = True 
             self.critial_errors.append("One or more of your non-terminals has more than the 4 character limit. Please change this in order to parse using this grammar.")

         if  grammar_object.overlapping_alphabets:
             self.major_flags = True 
             self.critial_errors.append("There is overlap between your terminal and non-terminal alphabets, parsing cannot proceeed.")
        
         if  len(grammar_object.processed_rules) > 200:
             self.major_flags = True 
             self.critial_errors.append("The maximum number of rules your grammar can have is 200.")


         if  len(grammar_object.processed_rules) < 3:
             self.major_flags = True 
             self.critial_errors.append("The minimum number of rules your grammar can have is 3.")

        
        # Make sure there are no negative probabilities 

         for rule in grammar_object.collapsed_rules:
             if rule._probability < 0:
                 self.major_flags = True 
                 self.critial_errors.append("One or more of your rules has a negative probability, which cannot be used.")


     

         
         # Set non-critical warnings 

         if not grammar_object.consistent: 
             self.non_critial_errors.append("Warning! Your grammar is inconsistent, meaning the sum of probabilities for each rule over each non-terminal do not sum to 1. Parsing can still proceed, but there will not be a proper probability distribution over parses and the total and cumulative probabilities reflect weights rather than an actualy probability.")
         
         if grammar_object.ignored_rules:
             self.non_critial_errors.append("Warning! One or more rules has been ignored due to syntax error or repeated rules. Please make sure rules are unique, excluding the probabilities.")


        
        
        
        

        # attempt parsing if there's no major flags
         if not self.major_flags:

             try:
    
                 if self.probabilistic:
                     data = {}
                
                     raw_parses = parser.n_best_parses(number_of_parses,sentence)
                     best_parse = raw_parses[0]
                     count = best_parse.counter 
                     
                     
                     # if total is needed, pull it out of the best best
                     if total_needed:
                         total = Decimal(best_parse.tracker_probability).normalize(context=context)
                      
                     
                     parses = [parse.get_full_tree() for parse in raw_parses]
                     parses_d = [parse.get_full_tree(table=True) for parse in raw_parses]

                     nodes = best_parse.node_count 
               
    
                     # only generate the leftmost derivation tables if the user wants them 
                    
                     if table_needed:
                         # lots of duplicate work done in the derivation builders, should come back to refactor 
                         # tables = [get_derivation_table(parse,grammar_object.processed_rules) for parse in parses_d]
                         tables = json.dumps({i+1: get_derivation_table(parse,grammar_object.processed_rules) for i,parse in enumerate(parses_d)})
                         pass 
      
      
                     for i in range(len(parses)):
                         data[i+1] = parses[i]

                     accepted = True 
                     
                    
                 else: 
                     # non probabilistic parsing 
                     data = {}
            
                     raw_parses = parser.n_best_parses(number_of_parses,sentence)
                     best_parse = raw_parses[0]
                     parses = [parse.get_full_tree() for parse in raw_parses]
                     parses_d = [parse.get_full_tree(table=True) for parse in raw_parses]
                     count = best_parse.counter
                     nodes = best_parse.node_count
                  
                  
              
                     # only generate the leftmost derivation tables if the user wants them 
                     if table_needed:
                         # lots of duplicate work done in the derivation builders, should come back to refactor 
                         # tables = [get_derivation_table(parse,grammar_object.processed_rules) for parse in parses_d]
                         tables = json.dumps({i+1: get_derivation_table(parse,grammar_object.processed_rules) for i,parse in enumerate(parses_d)})
                         pass 
      
      
                     for i in range(len(parses)):
                         data[i+1] = parses[i]
                  
                     accepted = True
                    
                
                # Set confirmation messages and noncritical errors 
                 self.accepted = accepted
                 if self.accepted:
                    self.confirmation_messages.append("Your string is accepted by this grammar.")
                 
                 if len(parses) < int(number_of_parses):
 
                     if len(parses) == 1:
                         self.non_critial_errors.append("This sentence is unambiguous, meaning that there is only one way to parse the sentence and only 1 unique leftmost derivation")
                        
                     else:
                         self.non_critial_errors.append(f'There are only {len(parses)} ways to parse this sentence, so {number_of_parses} cannot be given.')
                 else:
                     self.confirmation_messages.append(f'There are {count} ways to parse this setnence.')

                
                 if nodes > 40:
                    self.non_critial_errors.append("Your parse trees have 40 or more  non-terminal nodes. To aid with rendering your parse trees, they will be presented horizontally. The parses are equivalent to vertical trees.The derivation step order is still depth first, but is now top to bottom instead of left to right.")
                
                 else:
                     self.confirmation_messages.append("Your parse trees are small enough to be rendered vertically. To correspond with the leftmost derivation table, the derivation step order in the tree is depth first from left to right.") 
                
                


                

                
                
                 # set the number of parses to the number actually generated, rather than the number requested
                 number_of_parses = len(parses)
                 
                  
 


                    

            # Either the string is not accepted, or there may be some other uncaught error in the program. 
             except Exception as e:
                  
           
                    self.major_flags = True 
                    self.critial_errors.append("Your input string is not accepted by this grammar.")
        

         
         return grammar,sentence,accepted,parses,data,total,tables,number_of_parses,comparison_mode,nodes 
      
                


   
def flash_errors(form):
    """Flashes form errors"""
    for field, errors in form.errors.items():
        for error in errors:
            flash(u"Error in the %s field - %s." % (
                getattr(form, field).label.text,
                error
            ), '3')



