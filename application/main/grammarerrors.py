
"""
Custom grammar errors.

"""

class GrammarException(Exception):

    def __init__(self, message = "Generic grammar exception"):
        self.message = message 
        super().__init__(self.message)
    

class StringInputException(Exception):

    def __init__(self, message = "Generic string input error exception"):
        self.message = message 
        super().__init__(self.message)


class StringNotAccepted(Exception):

    def __init__(self, message = "String is not accepted"):
        self.message = message 
        super().__init__(self.message)


class JSONFileError(Exception):

    def __init__(self, message = "There is a missing category "):
        self.message = message 
        super().__init__(self.message)
    
    
    