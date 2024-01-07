'''
    Exceptions
    custom exceptions for this special usecase
'''

class NotCompileException(Exception):
    def __init__(self, errorText):
        self.errorText = errorText
        super().__init__(self.errorText)

class TestNotFoundException(Exception):
    def __init__(self, errorText):
        self.errorText = errorText
        super().__init__(self.errorText)