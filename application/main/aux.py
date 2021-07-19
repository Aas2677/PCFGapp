from math import prod
import re
import application.main.grammarerrors as grammarerrors



def parse_string(input,separator = ","):
    # function to pull out the start symbol and rules of a grammar from a string input. Always assumes LHS of first rule is the start symbol  

    separated_input = input.split(separator) 
    rules = []
    variables = []
    start = "S"
    try:
        for rule in separated_input:
        
           # get lHS and RHS 
           left,right = rule.split('->')
        
           # Remove spaces from the LHS 
           left = re.sub(r"\s+", "",left, flags=re.UNICODE) 


           # add the variable to list of variables if it is not already there 
           if left not in variables:
               variables.append(left)
        
 
        

           #get a list of right hand side productions, sepatated by | 
           products = right.split("|")

           for product in products:
               # Find probabilities passed
               probability_pattern = re.compile(r"( \[ [\d\.]+ \] ) \s*", re.VERBOSE)
               probability_strip = re.compile(r"( \[ [\d\.]+ \] ) .*", re.VERBOSE)
               just_numbers = re.compile(r"([\d\.]+)\s*", re.VERBOSE)

               # check to make sure only one probability is given
               probabilities = probability_pattern.findall(product)
               if len(probabilities) != 1:
                   pass
            
                # raise grammarerrors.StringInputException("There's something wrong with the way you've entered the proabilities")
               else: 
                # Get the raw number out of the brackets
                   probability = float(just_numbers.findall(probabilities[0])[0])


                # strip out the RHS variables and terminals. assume that spaces indicate seperate atoms. Get rid of escapes.
                   product =  list(filter(lambda x : x != '' and x != '\r\n' and x != '\r' and x != '\n',(re.sub(probability_strip,"",product)).split(" ")))
                #    print(product)
                   product = [re.sub('\n','', re.sub('\r','',item))for item in product]
                #    print(product)
                  


                   if len(product) == 0:
                       raise grammarerrors.StringInputException("Empty productions are not permitted")
                   try:
                    # If the probability is numerical, add the rule 
                    probability = float(probability)
                    rules.append((left,product,probability))
                    


                   except ValueError:
                    # If the characters inside the brackets are non-numerical, then discard the production entirely
                       pass 
    except Exception as e:
        raise grammarerrors.StringInputException("Please read the information page and follow the grammar input rules")

    

    # By default, the first LHS variable is the start variable
    start = variables[0]

    

    return rules,variables,start





# print(parse_string("A -> B [0.6] | C [0.4], B -> alex [0.5] | kraken  aaron[0.5], C -> cat[0.2]| doggo"))


