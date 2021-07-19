from itertools import combinations,product
from os import error
import application.main.grammars as grammars
import application.main.grammarerrors as grammarerrors 
import itertools 
import timeit 
import time 
from collections import defaultdict
import math 
import copy 
import json  

class ProbabilisticCYKParser:


    def __init__(self,grammar : grammars.ProbabilisticGrammar):
        self._grammar = grammar 
        self._reference_table = {}
        self._reference_list = [] 
        self._parse_table = {}
        self._sentence = None 
        self._tokens = None 
        self._nonatomic_reference_list = [] 
        self._n_best_table = None
        self._n_best_dict = defaultdict(int)
        self._n_best_consider = {}
        


    def recogniser(self) -> None:
        # setup leaf nodes 
        for i,j in self._reference_list[0]:
            atom = self._sentence[i]
            for rule in self._grammar.collapsed_rules:
                if rule.get_right()[0] == atom:
                    self._parse_table[(i,j)].append(rule)
                    

        # parse upwards
        for sub_word_length in self._nonatomic_reference_list:
            for (start_one,stop_one),(start_two,stop_two) in self._reference_table[sub_word_length]:
                left,right = self._parse_table[(start_one,stop_one)],self._parse_table[(start_two,stop_two)]
                if left and right:
                    for left_child,right_child in product(left,right):
                        left_child_root = left_child.get_left()
                        right_child_root = right_child.get_left()
                        for rule in self._grammar.expansion_rules:
                            right_side = rule.get_right()
                            if left_child_root == right_side[0] and right_child_root == right_side[1]:
                                self._parse_table[sub_word_length].append(rule)
        

                                
    
    def parse_string(self,records : bool = True) -> None:

        # setup leaf nodes by adding the rules that create the terminals
    
        for i,j in self._reference_list[0]:
            atom = self._tokens[i]
            rules = self._grammar.terminal_dict[atom]
            if rules:
                
                for r in rules:
                    node = ProbabilisticNode(r,None,None, leaf  = True)
                    self._parse_table[(i,j)].append(node)


        

        #parse upwards --- what a fucking mess. needs breaking up to use generators
        for sub_word_length in self._nonatomic_reference_list:
                for (start_one,stop_one),(start_two,stop_two) in self._reference_table[sub_word_length]:
                    left,right = self._parse_table[(start_one,stop_one)], self._parse_table[(start_two,stop_two)]
                    if left and right:
                        for left_child,right_child in product(left,right):
                            left_child_root = left_child.rule._left
                            right_child_root = right_child.rule._left
                            for rule in self._grammar.expansion_rules:
                                right_side = rule._right
                                if left_child_root._token == right_side[0]._token and right_child_root._token == right_side[1]._token:
                                    # we have successfully found an acceptable subtree !! :)
                                    self._parse_table[sub_word_length].append(ProbabilisticNode(rule,left_child,right_child))

        return [x.tree_probability() for x in self._parse_table[0,len(self._tokens)]]

       
    
    def experiment_parse(self):

        for i,j in self._reference_list[0]:
            atom = self._tokens[i]
            rules = self._grammar.terminal_dict[atom]
            if rules:
                for r in rules:
                    node = ProbabilisticNode(r,None,None,1, leaf  = True)
                    self._parse_table[(i,j)].append(node)

            
        

        #parse upwards --- what a fucking mess. needs breaking up to use generators
        for sub_word_length in self._nonatomic_reference_list:
                for (start_one,stop_one),(start_two,stop_two) in self._reference_table[sub_word_length]:
                    left,right = self._parse_table[(start_one,stop_one)], self._parse_table[(start_two,stop_two)]
                    if left and right:
                        for left_child,right_child in product(left,right):
                            left_child_root = left_child.rule._left._token
                            right_child_root = right_child.rule._left._token

                            rules = self._grammar.expansion_dict[left_child_root+right_child_root]
                            if rules:
                                for rule in rules:
                                    right_side = rule._right
                                    if left_child_root == right_side[0]._token and right_child_root == right_side[1]._token:
                                        self._parse_table[sub_word_length].append(ProbabilisticNode(rule,left_child,right_child,1))

        return [x.tree_probability() for x in self._parse_table[0,len(self._tokens)]]
        
        

    def best_parse(self,input_string, is_sentence = True):

        # Finds the best parse of the 

        parse_table = defaultdict(int)
        to_parse, tokens = self._preprocess_string(input_string, sentence = is_sentence)

        # setup the leaf nodes 
        length = len(tokens)
        for n in range(length):
            atom = tokens[n]
            for nonterminal in self._grammar.token_nonterminals:
                rule = self._grammar.terminal_rule_dict[nonterminal,atom]
                if rule:
                        parse_table[n,n,nonterminal] = ProbabilisticNode(rule,None, None, rule._probability,(j,k),leaf=True)

        
        for i in range(1,length):
            for j in range(length - i):
                k = j + i 
                for nonterminal in self._grammar.token_nonterminals:
                    highest_probability = 0 
                    best_node = None 
                    if self._grammar.expansion_lhs_lookup[nonterminal]:
                        rules = self._grammar.expansion_lhs_lookup[nonterminal]
                        for rule in rules:
                            left,right = rule._right[0]._token,rule._right[1]._token

                            for p in range(j,k):
                                # left_cons,right_cons = parse_table[j,p,left],parse_table[p+1,k,right]
                                if parse_table[j,p,left] and parse_table[p+1,k,right]:
                                    this_probability = rule._probability * parse_table[j,p,left].cumulative_prob * parse_table[p+1,k,right].cumulative_prob
                                    
                                    if highest_probability < this_probability:
                                        if highest_probability != 0:
                                            if this_probability == 0:
                                                print("oh")

                        
                                        highest_probability = this_probability
                                        best_node = ProbabilisticNode(rule, parse_table[j,p,left],parse_table[p+1,k,right], this_probability,(j,k))


                        

                        if highest_probability:
                           parse_table[j,k,nonterminal] = best_node

        if parse_table[0,length-1,self._grammar.start._token]:
            return parse_table[0,length-1,self._grammar.start._token]
        else:
            return grammarerrors.StringNotAccepted("The input is not generated by this grammar!")

    def get_bytes_output(self,parses):

        # accepts a list of probabilistic nodes representing full parses and translates their output into utf16 so they can be read into javascript 

        full_parses = [parse.get_full_tree() for parse in parses]

        return [json.dumps(p) for p in full_parses]
   

    
    def best_parse_all(self,input_string, is_sentence = True):

        # Finds the best parse of the 

        parse_table = defaultdict(int)
        to_parse, tokens = self._preprocess_string(input_string, sentence = is_sentence)

        # setup the leaf nodes 
        length = len(tokens)
        for n in range(length):
            atom = tokens[n]
            for nonterminal in self._grammar.token_nonterminals:
                rule = self._grammar.terminal_rule_dict_logs[nonterminal,atom]
                if rule:
                        parse_table[n,n,nonterminal] = ProbabilisticNode(rule,None, None, rule._probability,(n,n),leaf=True)

        
        for i in range(1,length):
            for j in range(length - i):
                k = j + i 
                for nonterminal in self._grammar.token_nonterminals:
                    lowest_weight = None
                    best_node = None 
                    if self._grammar.expansion_lhs_lookup[nonterminal]:
                        rules = self._grammar.expansion_lhs_lookup_logs[nonterminal]
                        for rule in rules:
                            left,right = rule._right[0]._token,rule._right[1]._token

                            for p in range(j,k):
                                # left_cons,right_cons = parse_table[j,p,left],parse_table[p+1,k,right]
                                if parse_table[j,p,left] and parse_table[p+1,k,right]:
                                    this_weight = math.fsum([rule._probability,parse_table[j,p,left].cumulative_prob, parse_table[p+1,k,right].cumulative_prob])
                                    if lowest_weight == None:
                                        lowest_weight = this_weight
                                        best_node = ProbabilisticNode(rule, parse_table[j,p,left],parse_table[p+1,k,right], this_weight,(j,k))
                                    else:
                                
                                        if this_weight < lowest_weight:
                                            lowest_weight = this_weight
                                            best_node = ProbabilisticNode(rule, parse_table[j,p,left],parse_table[p+1,k,right], this_weight,(j,k))

                                   


                        

                        if lowest_weight != None:
                           parse_table[j,k,nonterminal] = best_node

        if parse_table[0,length-1,self._grammar.start._token]:
            return parse_table,length
        else:
            return grammarerrors.StringNotAccepted("The input is not generated by this grammar!")

    def n_best_parses(self, n : int , input_string : str, is_sentence = True, j_bytes = False ):

        try:
            self._n_best_table,length = self.best_parse_all(input_string, is_sentence = is_sentence)
        except grammarerrors.StringNotAccepted as error :
            return error
        
        # If the grammar does generate the input, we can proceed to recover the n-best parses
        best_parse = self._n_best_table[0,length-1,self._grammar.start._token]
       

        # initial setup of n-best dictionary 
        for key in self._n_best_table.keys():
            if self._n_best_table[key]:
                self._n_best_dict[key] = [self._n_best_table[key]]
                self._n_best_consider[key] = []

        

        for k in range(2,n+1):
            # print(k)
            # print(self._n_best_dict[0,length-1,self._grammar.start._token][k-2])
            try:
                self.next_tree(self._n_best_dict[0,length-1,self._grammar.start._token][k-2],k)
            except IndexError:
                print("There aren't that many parses")
                break 
            
        

        if j_bytes:
            return self.get_bytes_output(self._n_best_dict[0,length-1,self._grammar.start._token])
        else:

            return self._n_best_dict[0,length-1,self._grammar.start._token]
    
    
    def next_tree(self,node , n : int) -> None:
        # Recursive descent to find nth best parse tree for input string after best_parse_all has found the best parse

        

        
        
        root_token = node.rule._left._token

        # for reference, get the spans of the whole tree, left and right children
        start_root,stop_root = node.span
        start_left,stop_left =  node.left_child.span 
        start_right,stop_right = node.right_child.span

       

        if n == 2:
            if self._grammar.expansion_lhs_lookup[root_token]:
                for rule in self._grammar.expansion_lhs_lookup_logs[root_token]:
                    left,right = rule._right[0]._token,rule._right[1]._token
                    for (left_start,left_stop),(right_start,right_stop) in self.partitions_2(start_root,stop_root):
                        if self._n_best_table[left_start,left_stop,left] and self._n_best_table[right_start,right_stop,right]:
                            this_weight = math.fsum([rule._probability,self._n_best_table[left_start,left_stop,left].cumulative_prob, self._n_best_table[right_start,right_stop,right].cumulative_prob])
                            self._n_best_consider[start_root,stop_root,root_token].append(ProbabilisticNode(rule, self._n_best_table[left_start,left_stop,left],self._n_best_table[right_start,right_stop,right],this_weight,node.span,rank=2))

                candidates = sorted(self._n_best_consider[start_root,stop_root,node.rule._left._token], key = lambda x : x.cumulative_prob)
                candidates.pop(0)
                self._n_best_consider[start_root,stop_root,node.rule._left._token] = candidates




        
        # if n == 2:
        #     print(node.span)
        #     for nonterminal in self._grammar.token_nonterminals:
        #         if self._grammar.expansion_lhs_lookup[nonterminal]:    
        #             for rule in self._grammar.expansion_lhs_lookup_logs[nonterminal]:
        #                 left,right = rule._right[0]._token,rule._right[1]._token
        #                 # print(left,right)

        #                 for (left_start,left_stop),(right_start,right_stop) in self.partitions_2(start_root,stop_root):
                            
                            
        #                     if self._n_best_table[left_start,left_stop,left] and self._n_best_table[right_start,right_stop,right]:
        #                         this_weight = math.fsum([rule._probability,self._n_best_table[left_start,left_stop,left].cumulative_prob, self._n_best_table[right_start,right_stop,right].cumulative_prob])
        #                         if node.rule._left._token == nonterminal:
        #                             self._n_best_consider[start_root,stop_root,node.rule._left._token].append(ProbabilisticNode(rule, self._n_best_table[left_start,left_stop,left],self._n_best_table[right_start,right_stop,right],this_weight,node.span,rank=2))

                                    

        #                         # self._n_best_consider[start_root,stop_root,node.rule._left._token].append(ProbabilisticNode(rule, self._n_best_table[left_start,left_stop,left],self._n_best_table[right_start,right_stop,right],this_weight,node.span,rank=2))
        #                        # print(rule, self._n_best_table[left_start,left_stop,left],self._n_best_table[right_start,right_stop,right],this_weight,node.span)
        #     candidates = sorted(self._n_best_consider[start_root,stop_root,node.rule._left._token], key = lambda x : x.cumulative_prob)
        #     for c in candidates:
        #         print(c)
            
        #     candidates.pop(0)
        #     self._n_best_consider[start_root,stop_root,node.rule._left._token] = candidates
        #     print("after")
        #     for c in self._n_best_consider[start_root,stop_root,node.rule._left._token]:
        #         print(c)
        #     print("\n")
                                

        
        if node.right_child.rank == 1 and (node.left_child.span[1] > node.left_child.span[0]) and len(self._n_best_dict[start_left,stop_left,node.left_child.rule._left._token]) < node.left_child.rank + 1:
            self.next_tree(node.left_child, node.left_child.rank + 1)
        
        if node.right_child.rank == 1 and len(self._n_best_dict[start_left,stop_left,node.left_child.rule._left._token]) >= node.left_child.rank + 1:
            # print("exists 1")
            # print(node.left_child.rank)

            new_left_tree = self._n_best_dict[start_left,stop_left,node.left_child.rule._left._token][node.left_child.rank]
            probability = math.fsum([node.rule._probability,new_left_tree.cumulative_prob,node.right_child.cumulative_prob])
            self._n_best_consider[start_root,stop_root,node.rule._left._token].append((ProbabilisticNode(node.rule,new_left_tree,node.right_child,probability,node.span,rank=n)))
            # if start_root == 0 and stop_root == 4 and node.rule._left._token == 'S':
                # print(new_left_tree)
        
        if stop_root > (start_right + 1) and len(self._n_best_dict[start_right,stop_right,node.right_child.rule._left._token]) < node.right_child.rank + 1:
            
            self.next_tree(node.right_child, node.right_child.rank + 1)
        
        if len(self._n_best_dict[start_right,stop_right,node.right_child.rule._left._token]) >= node.right_child.rank + 1:
            # print(node.right_child.rank)
            # print("exists 2")
            

            new_right_tree = self._n_best_dict[start_right,stop_right,node.right_child.rule._left._token][node.right_child.rank]
            probability = math.fsum([node.rule._probability,node.left_child.cumulative_prob,new_right_tree.cumulative_prob])
            self._n_best_consider[start_root,stop_root,node.rule._left._token].append((ProbabilisticNode(node.rule,node.left_child,new_right_tree,probability,node.span,rank=n)))
            # if start_root == 1 and stop_root == 4 and node.rule._left._token == 'V':
            #     for p in  self._n_best_dict[start_right,stop_right,node.right_child.rule._left._token]:
            #         print(p)
            #     print(self._n_best_dict[start_right,stop_right,node.right_child.rule._left._token])
            #     print(new_right_tree)
        

        candidates = sorted(self._n_best_consider[start_root,stop_root,node.rule._left._token], key = lambda x : x.cumulative_prob)
        
        
        if candidates:
            # print(next_best_tree)
            next_best_tree = candidates[0]
            
            next_best_tree.rank = n
            candidates.pop(0)
            self._n_best_dict[start_root,stop_root,node.rule._left._token].append(next_best_tree)
            self._n_best_consider[start_root,stop_root,node.rule._left._token] = candidates
        else:
            # next best tree doesn't exist 
            # print(f'{n}th best parse at {node.span} does not exist')
            pass 
            


        

        




                
           

    

        



    def all_parse(self,input_string, is_sentence = True):

        # finds the total probability of the input string being generated by the grammar. Throws error if not accepted

        parse_table = defaultdict(int)
        all_table = defaultdict(int)
        to_parse, tokens = self._preprocess_string(input_string, sentence = is_sentence)

        # setup the leaf nodes 
        length = len(tokens)
        for n in range(length):
            atom = tokens[n]
            for nonterminal in self._grammar.token_nonterminals:
                rule = self._grammar.terminal_rule_dict[nonterminal,atom]
                if rule:
                        parse_table[n,n,nonterminal] = ProbabilisticNode(rule,None, None, rule._probability,(n,n),leaf = True)
                        all_table[n,n,nonterminal] = [ProbabilisticNode(rule,None, None, rule._probability,(n,n),leaf = True)]

        
        for i in range(1,length):
            for j in range(length - i):
                k = j + i 
                for nonterminal in self._grammar.token_nonterminals:
                    possible = False
                    total_node = None 
                    if self._grammar.expansion_lhs_lookup[nonterminal]:
                        # best_rule  = (self._grammar.expansion_lhs_lookup[nonterminal],key = lambda x : x._probability)
                        rules = self._grammar.expansion_lhs_lookup[nonterminal]
                        for rule in rules:

                           left,right = rule._right[0]._token,rule._right[1]._token

                           for p in range(j,k):
                               if all_table[j,p,left] and all_table[p+1,k,right]:
                                   for L,R in product(all_table[j,p,left], all_table[p+1,k,right]):
                                       this_probability = rule._probability * L.cumulative_prob * R.cumulative_prob
                                       if possible:
                                           all_table[j,k,nonterminal].append(ProbabilisticNode(rule,L,R,this_probability,(j,k)))
                                       else:
                                            all_table[j,k,nonterminal] = []
                                            all_table[j,k,nonterminal].append(ProbabilisticNode(rule,L,R,this_probability,(j,k)))
                                            possible = True 


                                #    this_probability = rule._probability * parse_table[j,p,left].cumulative_prob * parse_table[p+1,k,right].cumulative_prob
                                #    if possible:
                                #        total_node.cumulative_prob += this_probability
                                #        all_table[j,k,nonterminal].append(ProbabilisticNode(rule,parse_table[j,p,left],parse_table[p+1,k,right],this_probability))
                                #    else:
                                #        total_node = ProbabilisticNode(rule, left, right, this_probability)
                                #        all_table[j,k,nonterminal] = []
                                #        all_table[j,k,nonterminal].append(ProbabilisticNode(rule,parse_table[j,p,left],parse_table[p+1,k,right],this_probability))
                                #        possible = True 
                                       


                    if possible:
                        parse_table[j,k,nonterminal] = total_node

        if all_table[0,length-1,self._grammar.start._token]:
            return all_table[0,length-1,self._grammar.start._token]
        else:
            return grammarerrors.StringNotAccepted("The input is not generated by this grammar!")
    

    



    def total_probability(self,input_string, is_sentence = True):

        # finds the total probability of the input string being generated by the grammar. Throws error if not accepted

        parse_table = defaultdict(int)
        to_parse, tokens = self._preprocess_string(input_string, sentence = is_sentence)

        # setup the leaf nodes 
        length = len(tokens)
        for n in range(length):
            atom = tokens[n]
            for nonterminal in self._grammar.token_nonterminals:
                rule = self._grammar.terminal_rule_dict[nonterminal,atom]
                if rule:
                        parse_table[n,n,nonterminal] = ProbabilisticNode(rule,None, None, rule._probability,(n,n))

        
        for i in range(1,length):
            for j in range(length - i):
                k = j + i 
                for nonterminal in self._grammar.token_nonterminals:
                    possible = False
                    total_node = None 
                    if self._grammar.expansion_lhs_lookup[nonterminal]:
                        # best_rule  = (self._grammar.expansion_lhs_lookup[nonterminal],key = lambda x : x._probability)
                        rules = self._grammar.expansion_lhs_lookup[nonterminal]
                        for rule in rules:

                           left,right = rule._right[0]._token,rule._right[1]._token

                           for p in range(j,k):
                               if parse_table[j,p,left] and parse_table[p+1,k,right]:
                                   this_probability = rule._probability * parse_table[j,p,left].cumulative_prob * parse_table[p+1,k,right].cumulative_prob
                                   if possible:
                                       total_node.cumulative_prob += this_probability
                                   else:
                                       total_node = ProbabilisticNode(rule, left, right, this_probability,(j,k))
                                       possible = True 
                                       


                    if possible:
                        parse_table[j,k,nonterminal] = total_node

        if parse_table[0,length-1,self._grammar.start._token]:
            return parse_table[0,length-1,self._grammar.start._token]
        else:
            return grammarerrors.StringNotAccepted("The input is not generated by this grammar!")



            
                                
                     
           
    def _preprocess_string(self,string : str , sentence: bool = True) -> list:

        # sentence flag means split the input on spaces. If the sentence flag is false, split every atom in the input  
       if sentence:
           tokens =   [x for x in string.split(" ") if x != '']
           to_parse = [grammars.Terminal(x) for x in string.split(" ") if x != '']
           
           
       else:
           to_parse = [grammars.Terminal(x) for x in list(string)]
           tokens = list(string)
           

       # Check if all the terminals are actually in the grammar's terminal alphabet, if not we can reject it straight away 
       for terminal in to_parse:
           if terminal not in self._grammar.alphabet:
               raise grammarerrors.StringNotAccepted("The input string is not generated by this grammar!")

       return to_parse,tokens


    def setup_parser(self,input_string : str, sentence : bool = True) -> None:

        # get a list of input tokens from the input string 
        to_parse,tokens = self._preprocess_string(input_string, sentence = sentence)
        self._sentence = to_parse
        self._tokens = tokens

        string_length = len(to_parse)
       

        # setup the dictionary keys for the parse chart 
        self._reference_list = [self.n_lengths(string_length,n) for n in range(1,string_length+1)]

        # setup the flat upward list 
        self._nonatomic_reference_list = [i for sublist in self._reference_list[1:] for i in sublist]
        
        #setup the reference table for the leaf nodes
        for index in self._reference_list[0]:
            self._reference_table[index] = [index]


        #setup the reference list for all other non leaf nodes 
        for index in self._reference_list[1:]:
            for i,j in index:
                self._reference_table[(i,j)] = self.partitions(i,j)

        #setup empty parse table:
        self._parse_table = {key:[] for key in self._reference_table.keys()}


    def n_lengths(self,list_len,n : int) -> list:
        # returns all the n - length sub lists from a list or string
       

        return [ (i,j) for i,j in combinations(range(list_len+1), r=2) if j - i == n ]

    
    def partitions(self,x:int,y:int) -> list:

        # returns the 2-partition indexes of a substring slice x:y 
        # there should never be an occaision where x - y < 2 
        difference = y - x 
        partitions = []

        if difference == 1:
            return ValueError("Can't partition a single atom ")
        else:
            step =  1

            while step < difference:
                partitions.append(((x,x+step),(x+step,y)))
                step += 1 

            return partitions
    
    def partitions_2(self,x:int,y:int) -> list:
    # attempt to make the partitions function a bit quicker
            return (((x,x+step),(x+step+1,y)) for step in range(y))



class CandidateContainer:

    __slots__ = 'table_pointer','candidates'

    def __init__(self,table_pointer,candiates : list):

        self.table_pointer = table_pointer
        self.candiates = [] 
    
class ProbabilisticNode:

    __slots__ = 'rule','leaf','left_child','right_child','cumulative_prob','span','rank'
    def __init__(self,rule, left ,right, prob,span,rank = 1, leaf = False):
        self.leaf = leaf
        self.rule = rule 
        self.left_child = left 
        self.right_child = right
        self.cumulative_prob = prob
        self.span = span 
        self.rank = rank 

    def __str__(self):
        return f'{self.rule}, {self.cumulative_prob}'

    def is_leaf(self) -> bool:
        return self.left_child == None and self.right_child == None

    
    def get_full_tree(self,table=False) -> list:

        # recursivley builds a dicitonary with all relevant details of the full parse tree and each sub-tree 
        # if table is set to true, return the actual rule objects, otherwise return string representaitons of everything 

        local_dict = {}


        if table:
            local_dict["name"] = self.rule._left
            local_dict["rule"] = self.rule
            local_dict["rule_probability"] = round(math.exp( -1* self.rule._probability),3)
            local_dict["children"] = [] 

            if self.leaf:
                local_dict["children"].append({"name": self.rule._right[0]})
                return local_dict
            else:

                # otherwise  we need to recursivley build the tree 
                local_dict["children"] = [] 
                local_dict["children"].append(self.left_child.get_full_tree(table=True))
                local_dict["children"].append(self.right_child.get_full_tree(table=True))
                
                return local_dict




            
        else:




            # setup the name,rule and cumulative probabilities of the node.
            local_dict["name"] = f'{self.rule._left}'
            local_dict["rule"] = str(self.rule)
            local_dict["cumulative_prob"] = math.exp(-1 * self.cumulative_prob)
            local_dict["children"] = [] 
        
        
            if self.leaf:
                # if the node is a leaf, then there's no more recursive calls to build the full dictionary
                local_dict["children"].append({"name": str(self.rule._right[0]),"rule":"Leaf - not applicable","cumulative_prob":"Leaf - not applicable"})
                return local_dict
            else:
                # otherwise  we need to recursivley build the 
                local_dict["children"] = [] 
                local_dict["children"].append(self.left_child.get_full_tree())
                local_dict["children"].append(self.right_child.get_full_tree())

                helper = MiniBuilder(local_dict)
                helper = helper.add_steps()
                add_leaf_messages(helper)



                return helper


   
        




    def tree_probability(self) -> float:

        # deprecated, use cumulative_prob attribute (parsing algorithm has been changed to keep track of cumulative probabilities of trees )

        if self.leaf:
            return self.rule.get_probability()
        else:
            return self.rule.get_probability() * self.left_child.tree_probability() * self.right_child.tree_probability()
    
    
    

class MiniBuilder:

    """just adds 'step' information to a parse tree so that it can be cross referenced with the leftmost derivation table
    ---- probably doesn't need a class :)
    
    ---- Input is the dictionary represenation of the parse tree, not the probabilistic node object"""


    def __init__(self,tree:dict) -> None:
        self.step = 0 
        self.tree = tree

    
    def x(self):
        self.step = 1


    def add_steps(self):
        self.tree["step"] = 0 
        self.step += 1 

        children = self.tree["children"]

        # traverse down the tree 
        self.recurse_steps(children)

        return self.tree
    
    def recurse_steps(self,children):

        children = [child for child in children if "children" in child]

        for child in children:
            child["step"] = self.step 
            self.step += 1 
        
        children_of_children = list(itertools.chain(*[child["children"] for child in children]))

        if children_of_children:
            self.recurse_steps(children_of_children)
        





class DerivationBuilder:
    """class to help build a leftmost derivation table using the probabilistic nodes generated by the parsing
    algorthm"""
    

    def __init__(self,tree,ruleset:list) -> None:
       
        self.step = 0 
        self.rules = self.rank_rules(ruleset)
        self.tree = tree 
        self.table = {}
        self.current_string = None

    def rank_rules(self,ruleset):
        # Take the rules dictionary and rank all of the rules in descensing order for each nonterminal

        for nonterminal in ruleset.keys():
            ruleset[nonterminal] = sorted(ruleset[nonterminal],key = lambda x: x._probability)
        
        return ruleset


    def build_leftmost_derivation(self):

        # The first 2 entries of the parse table need to be created just from the root node, then we can recurse 



        
        # instantiate inner dict
        self.table[0] = {}

        rule = self.tree["rule"]
        self.table[0]["nonterminal"] = "Not applicable"
        self.table[0]["rule"]  = "Not applicable"
        self.table[0]["probability"] = 1
        self.table[0]["rule_rank"] = "Not applicable"
        self.current_string = f'{self.tree["name"]}'
        self.table[0]["current_string"] = self.current_string
        self.step += 1

        self.table[1] = {}


       
        self.table[1]["nonterminal"] = str(self.tree["name"])
        self.table[1]["rule"]  = str(rule)
        self.table[1]["probability"] = self.tree["rule_probability"]
        self.table[1]["rule_rank"] = self.rules[self.tree["name"]].index(rule)+1 
        if len(rule) == 1:
            self.current_string = f'{rule._right[0]}'
        else:
            self.current_string = f'{str(rule._right[0])} {str(rule._right[1])}'
        

      
        self.table[1]["current_string"] = self.current_string
        self.step += 1

        

        # recursivley build children 

        self.build_recurse(self.tree["children"])

        # return finished table
        return self.table


    def build_recurse(self,children):

        # if a child is a leaf node, we can ignore it 
        children = [child for child in children if "children" in child]



        # add the children on this level first from left to right 
        for child in children:
            # no need to operate on leaves 
            try:
                self.table[self.step] = {}
                rule = child["rule"]

                self.table[self.step]["rule"] = str(rule)
                self.table[self.step]["nonterminal"] = str(child["name"])
                self.table[self.step]["probability"] = child["rule_probability"]
                self.table[self.step]["rule_rank"] = self.rules[child["name"]].index(rule) + 1
                if len(rule) == 1:
                    self.current_string = self.current_string.replace(str(child["name"]),str(rule._right[0]),1)

                else:
                    self.current_string = self.current_string.replace(str(child["name"]),f'{str(rule._right[0])} {str(rule._right[1])}',1)
                
                self.table[self.step]["current_string"] = self.current_string

                self.step += 1 
            except KeyError:
                # leaf node
                pass 

                
        # recurse on children of children as a flattened list (if they exist)
        children_of_children = list(itertools.chain(*[child["children"] for child in children]))

        if children_of_children:
                    self.build_recurse(children_of_children) 




# Extra aux functions outside classes 

def get_derivation_table(tree:dict,rules) -> dict:

    # Quick function to turn tree format dict into table format dict 

    derivations_list = [] 
    helper = DerivationBuilder(tree,rules)

    return helper.build_leftmost_derivation()

def add_leaf_messages(tree:dict) -> dict:

    try:
        children = tree["children"]
        for child in children:
            add_leaf_messages(child)
        
    except KeyError:
        tree["step"] = "Leaf - not applicable"

    
        
        
        

            
                
            







            

    

    




















