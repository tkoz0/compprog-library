'''
typing protocols for operator overloads, expecting result type to be the same
'''

from abc import abstractmethod
from typing import Protocol, Self

class SupportsSelfEq(Protocol):
    ''' type implements == operator '''
    @abstractmethod
    def __eq__(self,other,/) -> Self:
        pass

class SupportsSelfNe(Protocol):
    ''' type implements != operator '''
    @abstractmethod
    def __ne__(self,other,/) -> Self:
        pass

class SupportsSelfLt(Protocol):
    ''' type implements < operator '''
    @abstractmethod
    def __lt__(self,other,/) -> Self:
        pass

class SupportsSelfGt(Protocol):
    ''' type implements > operator '''
    @abstractmethod
    def __gt__(self,other,/) -> Self:
        pass

class SupportsSelfLe(Protocol):
    ''' type implements <= operator '''
    @abstractmethod
    def __le__(self,other,/) -> Self:
        pass

class SupportsSelfGe(Protocol):
    ''' type implements >= operator '''
    @abstractmethod
    def __ge__(self,other,/) -> Self:
        pass

class SupportsSelfAdd(Protocol):
    ''' type implements + operator (binary) '''
    @abstractmethod
    def __add__(self,other,/) -> Self:
        pass

class SupportsSelfSub(Protocol):
    ''' type implements - operator (binary) '''
    @abstractmethod
    def __sub__(self,other,/) -> Self:
        pass

class SupportsSelfMul(Protocol):
    ''' type implements * operator '''
    @abstractmethod
    def __mul__(self,other,/) -> Self:
        pass

class SupportsSelfTrueDiv(Protocol):
    ''' type implements / operator '''
    @abstractmethod
    def __truediv__(self,other,/) -> Self:
        pass

class SupportsSelfFloorDiv(Protocol):
    ''' type implements // operator '''
    @abstractmethod
    def __floordiv__(self,other,/) -> Self:
        pass

class SupportsSelfMod(Protocol):
    ''' type implements % operator '''
    @abstractmethod
    def __mod__(self,other,/) -> Self:
        pass

class SupportsSelfPow(Protocol):
    ''' type implements ** operator '''
    @abstractmethod
    def __pow__(self,other,/) -> Self:
        pass

class SupportsSelfNeg(Protocol):
    ''' type implements - operator (unary) '''
    @abstractmethod
    def __neg__(self,/) -> Self:
        pass

class SupportsSelfPos(Protocol):
    ''' type implements + operator (unary) '''
    @abstractmethod
    def __pos__(self,/) -> Self:
        pass

class SupportsSelfInv(Protocol):
    ''' type implements ~ operator (unary) '''
    @abstractmethod
    def __invert__(self,/) -> Self:
        pass

class SupportsSelfShl(Protocol):
    ''' type implements << operator '''
    @abstractmethod
    def __lshift__(self,other,/) -> Self:
        pass

class SupportsSelfShr(Protocol):
    ''' type implements >> operator '''
    @abstractmethod
    def __rshift__(self,other,/) -> Self:
        pass

class SupportsSelfAnd(Protocol):
    ''' type implements & operator '''
    @abstractmethod
    def __and__(self,other,/) -> Self:
        pass

class SupportsSelfOr(Protocol):
    ''' type implements | operator '''
    @abstractmethod
    def __or__(self,other,/) -> Self:
        pass

class SupportsSelfXor(Protocol):
    ''' type implements ^ operator '''
    @abstractmethod
    def __xor__(self,other,/) -> Self:
        pass
