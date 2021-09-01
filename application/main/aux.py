
import re
import application.main.grammarerrors as grammarerrors





def parse_string(input,separator = ","):
    # function to pull out the start symbol and rules of a grammar from a string input. Always assumes LHS of first rule is the start symbol  

    separated_input = input.split(separator) 
    rules = []
    variables = []
    start = "S"
    # separated_input = [x for x in [ re.findall("\S+",i) for i in separated_input] if x]
    
    try:
        for rule in separated_input:
          if re.findall("\S+",rule):

           
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
                    
                    if len(probabilities) == 0:
                        probability = 1
                 
                     # raise grammarerrors.StringInputException("There's something wrong with the way you've entered the proabilities")
                    else: 
                     # Get the raw number out of the brackets
                        probability = float(just_numbers.findall(probabilities[0])[0])
     
     
                     # strip out the RHS variables and terminals. assume that spaces indicate seperate atoms. Get rid of escapes.
                    product =  list(filter(lambda x : x != '' and x != '\r\n' and x != '\r' and x != '\n',(re.sub(probability_strip,"",product)).split(" ")))
                     #    print(product)
                    product = [re.sub('\n','', re.sub('\r','',item))for item in product]
                        
                       
     
     
                    if len(product) == 0:
                            raise grammarerrors.StringInputException("Empty productions are not permitted")
                    try:
                         # If the probability is numerical, add the rule 
                         probability = float(probability)
                         if probability != 0:
                             rules.append((left,product,probability))

                     
     
                    except ValueError:
                         # If the characters inside the brackets are non-numerical, then discard the production entirely
                            pass 
    except Exception as e:
    
        raise grammarerrors.StringInputException("Please read the information page and follow the grammar input rules")

    

    # By default, the first LHS variable is the start variable
    start = variables[0]

    

    return rules,variables,start




def parse_string_non(input,separator = ","):
    # function to pull out the start symbol and rules of a grammar from a string input. Always assumes LHS of first rule is the start symbol  

    separated_input = input.split(separator) 
    rules = []
    variables = []
    start = "S"
    # only consider nonempty rules 
 
    try:
        for rule in separated_input:
            if re.findall("\S+",rule):
           
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
                   
    
    
                   # strip out the RHS variables and terminals. assume that spaces indicate seperate atoms. Get rid of escapes.
                   product =  list(filter(lambda x : x != '' and x != '\r\n' and x != '\r' and x != '\n',product.split(" ")))
                  
                   product = [re.sub('\n','', re.sub('\r','',item))for item in product]
                   
                      
    
    
                   if len(product) == 0:
                       raise grammarerrors.StringInputException("Empty productions are not permitted")
    
                   # assign a probability of 1 to each rule.
                   rules.append((left,product,1))
                  
    except Exception as e:
        
        raise grammarerrors.StringInputException("Please read the information page and follow the grammar input rules")

    

    # By default, the first LHS variable is the start variable
    start = variables[0]

    

    return rules,variables,start




def pretty_display_number(number:float): 

    
  
    return ('%.15f' % number).rstrip('0').rstrip('.')






 
     



