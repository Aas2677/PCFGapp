from flask import Flask,url_for,render_template,flash,redirect,session,g,abort,request 
from forms import TextInputForm
import grammarerrors
from grammars import ProbabilisticGrammar
from parsing import ProbabilisticCYKParser,ProbabilisticNode
import json

app = Flask(__name__)

app.config['SECRET_KEY'] = '0fdd7f0e0f4631a85cc4c4ec690c13fd'

def flash_errors(form):
    """Flashes form errors"""
    for field, errors in form.errors.items():
        for error in errors:
            flash(u"Error in the %s field - %s" % (
                getattr(form, field).label.text,
                error
            ), 'error')

test_tree = [['S -> [X, V]'], ['X -> [scientists]'], ['V -> [M, X]', ['M -> [see]'], ['X -> [X, Q]', ['X -> [cells]'], ['Q -> [T, X]', ['T -> [with]'], ['X -> [microscopes]']]]]]

@app.route("/",methods=['GET','POST'])
def hello():
    form = TextInputForm() 
   
    grammar = 0 
    sentence = 0 
    parses = [1,2]
    if form.validate_on_submit():
        grammar = str(form.grammar.data).strip('\n')
        sentence = str(form.sentence.data).strip('\n')
        
        # setup the parser:
        grammar_object = ProbabilisticGrammar.from_string(grammar)
        parser = ProbabilisticCYKParser(grammar_object)
        parses = [parse.get_full_tree() for parse in parser.n_best_parses(2000,sentence)]


    else:
        flash_errors(form)
        grammar = 0 
        sentence = 0  

    return render_template('mainpage.html',title = 'PCFG exporer',form = form,m=grammar,sentence=sentence,parses=parses)


   
            


@app.route("/parse",methods = ['GET'])
def parse():
    k = request.args.get('parameter')
    x = x =  '{ "name":"John", "age":30, "city":"New York"}'
    y = json.loads(x)
    return y


# @app.route("/trees",methods=['GET','POST'])
# def trees():
#     form = TextInputForm()
#     kek = 0 
#     if form.validate_on_submit():
#         kek = str(form.grammar)
#         flash(f'Your grammar is accepted')
#         flash(f'{kek}')
    
#     return render_template('trees.html',title = 'PCFG exporer',tree_list = test_tree,m = kek)

@app.route("/about")
def copy():
    return "<h1>About this tool</h1>"




if __name__ == '__main__':
    app.run(debug=True)