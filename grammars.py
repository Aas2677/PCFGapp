
import grammarerrors 
import aux 
from collections import defaultdict
import math
import json 


def GetNonTerminals(items):
    pass 

class Terminal:
    """ class to represent non-terminal symbols in a grammar.
    overrides for convenience"""


    def __init__(self,token):
        self._token = token 
        

    def __eq__(self,other):
        # equals override to check if 2 non-terminal symbols are the same
        if not (isinstance(other, NonTerminal) or isinstance(other,Terminal)):
            raise grammarerrors.GrammarException("The argument is not a terminal or non-terminal object terter")
        else:
            return self._token == other._token 

    def __ne__(self,other):
        
        return not self == other

    def __hash__(self):
        # get has of underlying symbol 
        return hash(self._token)
    
    def __repr__(self) -> str:
        # return string 
        return f'{self._token}'


    def get_token(self):
        return self._token



class NonTerminal:
    """ class to represent non-terminal symbols in a grammar.
    overrides for convenience"""


    def __init__(self,token):
        self._token = token 
        

    def __eq__(self,other):
        # equals override to check if 2 non-terminal symbols are the same
        if not (isinstance(other, NonTerminal) or isinstance(other,Terminal)):
            raise grammarerrors.GrammarException("The argument is not a terminal or non-terminal object nonon")
        else:
            return self._token == other._token 

    def __ne__(self,other):
        
        return not self == other

    def __hash__(self):
        # get has of underlying symbol 
        return hash(self._token)
    
    def __repr__(self) -> str:
        # return string 
        return f'{self._token}'


    def get_token(self):
        return self._token

    def __str__(self):
        return self._token




class ProductionRule:

    def __init__(self,left,right,probability):

        __slots__ = '_left','_right','_probability'

        if not isinstance(left, NonTerminal):
            # Make sure left hand side is a non-terminal symbol 
            raise grammarerrors.GrammarException("Left hand side must be a non-terminal object")
       
        
        self._left = left 
        self._right = right 
        self._probability = probability 
      

    
    
    def __len__(self):
        # Length override, find what the length of the right hand side of production is
        return len(self._right)
    
    def __hash__(self) -> int:

        return hash(self._left,self._right)

    def __eq__(self,other):

        return (type(self) == type(other)) and (self._left == other._left) and (self._right == other._right)
    
    def __ne__(self,other):
        
        return not self == other 

    def __str__(self) -> str:

        # f'{self._left} -> {self._right} -- [{self._probability}]'
        if len(self._right) ==1:
            return f'{self._left} → {self._right[0]} ({round(math.exp( -1* self._probability),3)})'
        else:
            return  f'{self._left} → {self._right[0],self._right[1]} ({round(math.exp( -1* self._probability),3)})'


        
       

    
    def get_left(self):

        return self._left
    
    def get_right(self):
        
        return self._right 

    def get_probability(self):

        return self._probability

    def is_empty(self):

        # check if rule is empty r

        return len(self) == 1 and self._right[0] == NonTerminal('ε')

    def get_type(self):

        # mehtod to help determine the type of the rule 

        return [type(atom) for atom in self._right]

        

    
        



class ProbabilisticGrammar: 



    """ class to represent a probabilistic context-free grammar"""

    def __init__(self,processed_rules,collapsed_rules,processed_rules_log,collapsed_rules_log,nonterminals,alphabet,bad_rules = False,start = NonTerminal('S'), tolerance = 0.02):
        # initially set CNF check to true 
        self.CNF = True 
        self.consistent = True 
        self.start = start 
        self.processed_rules = processed_rules
        self.processed_rules_log = processed_rules_log
        self.nonterminals = nonterminals 
        self.token_nonterminals = [atom._token for atom in self.nonterminals]
        self.alphabet = alphabet
        self.tolerance = tolerance
        self.check_CNF()
        self.check_consistency()
        self.collapsed_rules = collapsed_rules
        self.collapsed_rules_log = collapsed_rules_log 
        self.expansion_rules  = [rule for rule in self.collapsed_rules if len(rule.get_right()) == 2]
        self.expansion_rules_log = [rule for rule in self.collapsed_rules_log if len(rule.get_right()) == 2]
        self.terminal_rules = [rule for rule in self.collapsed_rules if len(rule.get_right()) == 1]
        self.terminal_rules_log = [rule for rule in self.collapsed_rules_log if len(rule.get_right()) == 1]
        self.terminal_dict = self.generate_dict(self.terminal_rules)
        self.expansion_dict = self.generate_dict(self.expansion_rules)
        self.terminal_rule_dict = self.generate_total_dict(self.terminal_rules)
        self.terminal_rule_dict_logs = self.generate_total_dict(self.terminal_rules_log)
        self.expansion_rule_dict = self.generate_total_dict(self.expansion_rules)
        self.terminal_lhs_lookup = self.make_lookup(1)
        self.expansion_lhs_lookup = self.make_lookup(2)
        self.expansion_lhs_lookup_logs = self.make_lookup(2,logs=True)
        self.ignored_rules = bad_rules 
       
      

  
    
    
    

    @classmethod 
    def from_string(cls,input):
       # function to generate a grammar from a string input 
       rules, non_terminals,start = aux.parse_string(input)

       # initialise empty terminal alphabet
       alphabet = [] 

       # initialise empty processed rules dictionary 
       processed_rules = {}
       processed_rules_log = {}
       collapsed_rules = []
       collapsed_rules_log = [] 

       
       # Create NonTerminal objects
       processed_non_terminals = [NonTerminal(token) for token in non_terminals]
       processed_start = NonTerminal(start)

       # create the keys for the unprocessed rules
       for lhs,atoms,probability in rules:

           lhs = NonTerminal(lhs) 

           if lhs not in processed_rules.keys():
               processed_rules[lhs] = [] 
               processed_rules_log[lhs] = []


        # Check for duplicate rules, only recognise the first delaration of a specific lhs/rhs combination 
       duplicate_checker = []
       ignored_rules = False 


        # parse the right hand sides of rules to identify terminals and non-terminals 
       for lhs,atoms,probability in rules:
           processed_atoms = [NonTerminal(atom) if atom in non_terminals else Terminal(atom) for atom in atoms]
           # Add terminal atoms to the terminal alphabet of the grammar 
           for atom in processed_atoms:
               if type((atom)) == Terminal and atom not in alphabet:
                   alphabet.append(atom)    


           # add standard and negative log versions of each to to the respective reference list/dictionary
           checker_tuple = (lhs,*atoms)

           if checker_tuple not in duplicate_checker:
              processed_rules[NonTerminal(lhs)].append(ProductionRule(NonTerminal(lhs), processed_atoms, probability))
              processed_rules_log[NonTerminal(lhs)].append(ProductionRule(NonTerminal(lhs), processed_atoms, -1* math.log(probability)))
              collapsed_rules.append(ProductionRule(NonTerminal(lhs), processed_atoms, probability))
              collapsed_rules_log.append(ProductionRule(NonTerminal(lhs), processed_atoms, -1* math.log(probability)))
           else:
               ignored_rules = True 
      


           

            
    

       return cls(processed_rules,collapsed_rules,processed_rules_log,collapsed_rules_log,processed_non_terminals,alphabet,start = processed_start, bad_rules = ignored_rules)

    

    @classmethod 
    def from_json(cls,input_file):

       # function to generate a grammar from a json input 
       

       try:
           data = json.load(input_file)
           rules = data["rules"]
           non_terminals = data["non_terminals"]
           terminals = data["terminals"]
           start = NonTerminal(data["start_symbol"])
       except Exception as e:
            print("fuck me ")
            print(e)
            return grammarerrors.JSONFileError(f'{e}')


       # create  terminal/ nonterminal  alphabet
       alphabet = [Terminal(letter) for letter in list(dict.fromkeys(terminals))]
       processed_non_terminals = [NonTerminal(token) for token in list(dict.fromkeys(non_terminals))]
   

       # initialise empty processed rules dictionary 
       processed_rules = {}
       processed_rules_log = {}
       collapsed_rules = []
       collapsed_rules_log = [] 

       

       

       # create the keys for the unprocessed r
       for letter in processed_non_terminals:

           if letter not in processed_rules.keys():
               processed_rules[letter] = [] 
               processed_rules_log[letter] = []


       # duplicate checker
       duplicate_checker = [] 


        # set flag for incorrectly specificed rules 
       ignored_rules = False

        # parse the right hand sides of rules
       for rule in rules:
            try:
               # If the lhs not in the nonterminal alphabet or is also declared a terminal, then ignore 
               if not rule["nonterminal"] in non_terminals or rule["nonterminal"] in terminals:
                   ignored_rules = True 
                
               else:
                   
                   # since the terminals and nonterminals are asked for in the json, we should not see any new characters in the rules. If not, we'll ignore the rule. 
                   if all(atom in terminals or atom in non_terminals  for atom in rule["expansion"]):
                       rhs = [NonTerminal(atom) if atom in non_terminals else Terminal(atom) for atom in rule["expansion"]]
                       new_rule = ProductionRule(NonTerminal(rule["nonterminal"]),rhs,float(rule["probability"]))
                       new_rule_log = ProductionRule(NonTerminal(rule["nonterminal"]),rhs,-1* math.log(float(rule["probability"])))
                       
                       checker_tuple = (rule["nonterminal"],*rule["expansion"])
                       
                       # if rule not already declared, add to rules, else ignore the ducplicate declaration 
                       if checker_tuple not in duplicate_checker:
                
                           processed_rules[NonTerminal(rule["nonterminal"])].append(new_rule)
                           processed_rules_log[NonTerminal(rule["nonterminal"])].append(new_rule_log)
                           collapsed_rules.append(new_rule)
                           collapsed_rules_log.append(new_rule_log)
                           duplicate_checker.append(checker_tuple)
                  
                       

                       
            except Exception as e :
                print(e)
                ignored_rules = True 
                continue
                
            
    
       return cls(processed_rules,collapsed_rules,processed_rules_log,collapsed_rules_log,processed_non_terminals,alphabet,start=start,bad_rules = ignored_rules)







    
   

    def make_lookup(self,length,logs = False):

        if logs:
            reference = self.processed_rules_log
           
        else:
            reference = self.processed_rules
        
        output_dict =  {key._token:[] for key, _ in reference.items()} 

        for key in reference.keys():
            for rule in reference[key]:
                if len(rule) == length:
                    output_dict[key._token].append(rule)
        
        return output_dict

    def generate_total_dict(self,rules) -> dict:
        # generates a defaultdict to allow for easy lookups to rules based on their left hand side 

        return_dict = defaultdict(int)
        
        for rule in rules:
            root = rule._left._token
            productions = [atom._token for atom in rule._right]
            accessible_string = ''.join([str(elem) for elem in productions])
            # get the raw token out for faster dictionary lookups
            
            # add in the dictionary entry
            return_dict[root,accessible_string] = rule
        
        return return_dict


    def generate_dict(self,rules) -> dict:

        # generates a defualtdict to allow for easy lookups to rules based on their productions 
        return_dict = defaultdict(int)

        for rule in rules:
            productions = [atom._token for atom in rule._right]
            # we want to speed up accessing elements of the dictionary, so we treat a series of nontemrinals as just a concatenated string
            accessible_string = ''.join([str(elem) for elem in productions])
            if accessible_string not in return_dict.keys():
                return_dict[accessible_string] = [] 
                return_dict[accessible_string].append(rule)
            else:
                return_dict[accessible_string].append(rule)
        
        return return_dict
               








    def check_CNF(self):
        

        # Test the rules to check if the grammar is in CNF 

        for rules in self.processed_rules.values():
            for rule in rules:
                is_start = rule.get_left() == self.start
                empty = rule.is_empty()
                length = len(rule)
                rhs_types = rule.get_type()
                rhs_atoms = rule.get_right()

                if not self.check_rule(is_start, rhs_atoms, rhs_types, length, empty):
                   self.CNF = False 
                   break 

        

            

    def check_rule(self,start,rhs,types,length,empty):

        # return true if rule in CNF, false otherwise 



        # CNF prohibits empty producitons 
        if empty:
            print('empty',rhs)
            return False 

        # singleton rules can't have a nonterminal lhs 
        if length == 1:
            if not types[0] == Terminal:
                print('1',rhs)
                return False
        
        if length == 2:
            if not all([atom_type == NonTerminal for atom_type in types]):
                print('2',rhs)
                return False 

        if length > 2:
            print('2+',rhs)
            return False 
        
        # checks passed 
        return True 


        # if length > 2:

        #     return False 
        # else:
        #     if empty:
        #         if not start:
        #             print(rhs)
        #             print("empty")
        #             return False 
        #     else:
        #         if self.start in rhs:             
        #             pass
        #         elif length == 2 and all([type(atom) == NonTerminal for atom in rhs]):
        #             return True 
        #         elif length == 1 and types[0] == Terminal:
                  
        #             return True 
        #         else:
        #             print(rhs)
        #             print("other")                  
        #             return False 

    def check_consistency(self):
    

        for variable,rules in self.processed_rules.items():
       

            total_probability = sum([x.get_probability() for x in rules])
        
            if total_probability <= 1 - self.tolerance or total_probability >= 1 + self.tolerance:
                self.consistent = False 




            


           
            

            

              
   







    

    


    


    



    
         

    






