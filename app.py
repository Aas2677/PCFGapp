from flask import Flask,url_for,render_template,flash,redirect,session,g,abort,request 
from forms import TextInputForm,FileInputForm
import grammarerrors
from werkzeug.utils import secure_filename
from grammars import ProbabilisticGrammar
from parsing import *
import json

app = Flask(__name__)

app.config['SECRET_KEY'] = '0fdd7f0e0f4631a85cc4c4ec690c13fd'

def flash_errors(form):
    """Flashes form errors"""
    for field, errors in form.errors.items():
        for error in errors:
            flash(u"Error in the %s field - %s." % (
                getattr(form, field).label.text,
                error
            ), '3')



@app.route("/",methods=['GET','POST'])
@app.route("/home",methods=['GET','POST'])
def home():
    return render_template('mainopen.html')


@app.route("/string_input",methods=['GET','POST'])
def string_input():
    
       form = TextInputForm() 
   
       grammar = 0 
       sentence = 0 
       accepted = False
       parses = []
       test_arr = [1,2,3,4,5,6]
       data = {}
       total = False
       tables = 0
       number_of_parses = False   
       if form.validate_on_submit():
           grammar = str(form.grammar.data).strip('\n')
           sentence = str(form.sentence.data).strip('\n')
           number_of_parses = int(form.n_parses.data)
           total_needed = form.show_total.data
           table_needed = form.show_table.data 
           
        
           # setup the parser:
           grammar_object = ProbabilisticGrammar.from_string(grammar)
           parser = ProbabilisticCYKParser(grammar_object)
           try:
               data = {}
            
               raw_parses = parser.n_best_parses(number_of_parses,sentence)
               parses = [parse.get_full_tree() for parse in raw_parses]
               parses_d = [parse.get_full_tree(table=True) for parse in raw_parses]
            
            
            
               # only update the total if the user has checked the box to indicate they want this information 
               if total_needed:
                   total_probability_node = parser.total_probability(sentence)
                   total = total_probability_node.cumulative_prob

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
               if not grammar_object.consistent:
                   flash(' Warning - your grammar is inconsistent. Parsing can see be carried out, but there will not be a proper probability distribution over parses.','2')

               if grammar_object.ignored_rules:
                    flash ('Warning - some rules in your grammar were ignored as duplicates or incorrect construction.','2')
           except Exception as e:
               print(e)
               
               flash('Your input sentence is not accepted by this grammar.','3')
               accepted = False


       else:
           flash_errors(form)
           grammar = 0 
           sentence = 0  

       return render_template('mainpage_string.html',title = 'PCFG exporer',form = form,m=grammar,sentence=sentence,parses=json.dumps(data),accepted=accepted,test_arr=test_arr,total = total, num_parses = number_of_parses,tables=tables)


@app.route("/file_input",methods=['GET','POST'])
def file_input():
    
       form = FileInputForm() 
   
       grammar = 0 
       sentence = 0 
       accepted = False
       parses = []
       test_arr = [1,2,3,4,5,6]
       data = {}
       total = False
       tables = 0
       number_of_parses = False   
       if form.validate_on_submit():
           grammar = form.grammar.data 
           print(grammar)
           sentence = str(form.sentence.data).strip('\n')
           number_of_parses = int(form.n_parses.data)
           total_needed = form.show_total.data
           table_needed = form.show_table.data 
           

        
           # setup the parser:
           grammar_object = ProbabilisticGrammar.from_json(grammar)
           parser = ProbabilisticCYKParser(grammar_object)
           try:
               data = {}
            
               raw_parses = parser.n_best_parses(number_of_parses,sentence)
               parses = [parse.get_full_tree() for parse in raw_parses]
               parses_d = [parse.get_full_tree(table=True) for parse in raw_parses]
            
            
            
               # only update the total if the user has checked the box to indicate they want this information 
               if total_needed:
                   total_probability_node = parser.total_probability(sentence)
                   total = total_probability_node.cumulative_prob

               # only generate the leftmost derivation tables if the user wants them 
               if table_needed:
                   # lots of duplicate work done in the derivation builders, should come back to refactor 
                   # tables = [get_derivation_table(parse,grammar_object.processed_rules) for parse in parses_d]
                   tables = json.dumps({i+1: get_derivation_table(parse,grammar_object.processed_rules) for i,parse in enumerate(parses_d)})
                   pass 


               for i in range(len(parses)):
                   data[i+1] = parses[i]
            
               accepted = True
               flash("Your sentence is accepted by this grammar")
           except Exception as e :
               print(e)
               flash(f'Your input sentence is not accepted by this grammar ; {e}')
               accepted = False


       else:
           flash_errors(form)
           grammar = 0 
           sentence = 0  

       return render_template('mainpage_file.html',title = 'PCFG exporer',form = form,m=grammar,sentence=sentence,parses=json.dumps(data),accepted=accepted,test_arr=test_arr,total = total, num_parses = number_of_parses,tables=tables)



@app.route("/about")
def about():
    return "<h1>About this tool</h1>"




if __name__ == '__main__':
    app.run(debug=True)