'''
typing protocols for supporting compare operators with standard bool result
'''

from abc import abstractmethod
from typing import Protocol

class SupportsCmpEq(Protocol):
    ''' type implements == operator '''
    @abstractmethod
    def __eq__(self,other,/) -> bool:
        pass

class SupportsCmpNe(Protocol):
    ''' type implements != operator '''
    @abstractmethod
    def __ne__(self,other,/) -> bool:
        pass

class SupportsCmpLt(Protocol):
    ''' type implements < operator '''
    @abstractmethod
    def __lt__(self,other,/) -> bool:
        pass

class SupportsCmpGt(Protocol):
    ''' type implements > operator '''
    @abstractmethod
    def __gt__(self,other,/) -> bool:
        pass

class SupportsCmpLe(Protocol):
    ''' type implements <= operator '''
    @abstractmethod
    def __le__(self,other,/) -> bool:
        pass

class SupportsCmpGe(Protocol):
    ''' type implements >= operator '''
    @abstractmethod
    def __ge__(self,other,/) -> bool:
        pass
