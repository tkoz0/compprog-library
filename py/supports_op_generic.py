'''
typing protocols for operator overloads, generic parameter for result type
'''

from abc import abstractmethod
from typing import Protocol

class SupportsGenEq[T](Protocol):
    ''' type implements == operator '''
    @abstractmethod
    def __eq__(self,other,/) -> T:
        pass

class SupportsGenNe[T](Protocol):
    ''' type implements != operator '''
    @abstractmethod
    def __ne__(self,other,/) -> T:
        pass

class SupportsGenLt[T](Protocol):
    ''' type implements < operator '''
    @abstractmethod
    def __lt__(self,other,/) -> T:
        pass

class SupportsGenGt[T](Protocol):
    ''' type implements > operator '''
    @abstractmethod
    def __gt__(self,other,/) -> T:
        pass

class SupportsGenLe[T](Protocol):
    ''' type implements <= operator '''
    @abstractmethod
    def __le__(self,other,/) -> T:
        pass

class SupportsGenGe[T](Protocol):
    ''' type implements >= operator '''
    @abstractmethod
    def __ge__(self,other,/) -> T:
        pass

class SupportsGenAdd[T](Protocol):
    ''' type implements + operator (binary) '''
    @abstractmethod
    def __add__(self,other,/) -> T:
        pass

class SupportsGenSub[T](Protocol):
    ''' type implements - operator (binary) '''
    @abstractmethod
    def __sub__(self,other,/) -> T:
        pass

class SupportsGenMul[T](Protocol):
    ''' type implements * operator '''
    @abstractmethod
    def __mul__(self,other,/) -> T:
        pass

class SupportsGenTrueDiv[T](Protocol):
    ''' type implements / operator '''
    @abstractmethod
    def __truediv__(self,other,/) -> T:
        pass

class SupportsGenFloorDiv[T](Protocol):
    ''' type implements // operator '''
    @abstractmethod
    def __floordiv__(self,other,/) -> T:
        pass

class SupportsGenMod[T](Protocol):
    ''' type implements % operator '''
    @abstractmethod
    def __mod__(self,other,/) -> T:
        pass

class SupportsGenPow[T](Protocol):
    ''' type implements ** operator '''
    @abstractmethod
    def __pow__(self,other,/) -> T:
        pass

class SupportsGenNeg[T](Protocol):
    ''' type implements - operator (unary) '''
    @abstractmethod
    def __neg__(self,/) -> T:
        pass

class SupportsGenPos[T](Protocol):
    ''' type implements + operator (unary) '''
    @abstractmethod
    def __pos__(self,/) -> T:
        pass

class SupportsGenInv[T](Protocol):
    ''' type implements ~ operator (unary) '''
    @abstractmethod
    def __invert__(self,/) -> T:
        pass

class SupportsGenShl[T](Protocol):
    ''' type implements << operator '''
    @abstractmethod
    def __lshift__(self,other,/) -> T:
        pass

class SupportsGenShr[T](Protocol):
    ''' type implements >> operator '''
    @abstractmethod
    def __rshift__(self,other,/) -> T:
        pass

class SupportsGenAnd[T](Protocol):
    ''' type implements & operator '''
    @abstractmethod
    def __and__(self,other,/) -> T:
        pass

class SupportsGenOr[T](Protocol):
    ''' type implements | operator '''
    @abstractmethod
    def __or__(self,other,/) -> T:
        pass

class SupportsGenXor[T](Protocol):
    ''' type implements ^ operator '''
    @abstractmethod
    def __xor__(self,other,/) -> T:
        pass
