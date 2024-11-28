import integer
import operator

MOD_DEFAULT: int = 0

class ModInt:
    '''
    immutable integer with modulus
    '''
    def __init__(self, n: 'int|ModInt' = 0, mod: int|None = None):
        if isinstance(n,ModInt):
            self.n = n.n
            self.mod = n.mod
            if mod is not None:
                assert mod > 0
                self.mod = mod
                self.n %= mod
        else:
            if mod is None:
                mod = MOD_DEFAULT
            assert mod > 0
            self.mod = mod
            self.n = n % mod
    
    def __repr__(self) -> str:
        return f'ModInt({self.n},{self.mod})'

    def __str__(self) -> str:
        return str(self.n)

    def _cmpop(self,o:'int|ModInt',op) -> bool:
        if isinstance(o,ModInt):
            assert self.mod == o.mod, 'different modulus compare not allowed'
            return op(self.n,o.n)
        elif isinstance(o,int):
            return op(self.n,o%self.mod)
        return NotImplemented

    def __eq__(self,o:'int|ModInt') -> bool:
        ret = self._cmpop(o,operator.eq)
        return False if ret is NotImplemented else ret

    def __ne__(self,o:'int|ModInt') -> bool:
        ret = self._cmpop(o,operator.ne)
        return True if ret is NotImplemented else ret

    def __lt__(self,o:'int|ModInt') -> bool:
        return self._cmpop(o,operator.lt)

    def __le__(self,o:'int|ModInt') -> bool:
        return self._cmpop(o,operator.le)

    def __gt__(self,o:'int|ModInt') -> bool:
        return self._cmpop(o,operator.gt)

    def __ge__(self,o:'int|ModInt') -> bool:
        return self._cmpop(o,operator.ge)

    def __hash__(self) -> int:
        return hash((self.n,self.mod))

    def __bool__(self) -> int:
        return self.n != 0

    def __neg__(self) -> 'ModInt':
        return ModInt(-self.n,self.mod)

    def __pos__(self) -> 'ModInt':
        return self

    def __invert__(self) -> 'ModInt':
        return ModInt(integer.modinv(self.n,self.mod),self.mod)

    def __int__(self) -> int:
        return self.n

    def _arith(self,o:'int|ModInt',op) -> 'ModInt':
        if isinstance(o,ModInt):
            assert self.mod == o.mod, 'different modulus arithmetic not allowed'
            return ModInt(op(self.n,o.n),self.mod)
        elif isinstance(o,int):
            return ModInt(op(self.n,o%self.mod),self.mod)
        return NotImplemented

    def __add__(self,o:'int|ModInt') -> 'ModInt':
        return self._arith(o,operator.add)

    def __sub__(self,o:'int|ModInt') -> 'ModInt':
        return self._arith(o,operator.sub)

    def __mul__(self,o:'int|ModInt') -> 'ModInt':
        return self._arith(o,operator.mul)

    def __truediv__(self,o:'int|ModInt') -> 'ModInt':
        if isinstance(o,int):
            o = ModInt(o,self.mod)
        return self * (~o)

    def __radd__(self,o:int) -> 'ModInt':
        return self + o

    def __rsub__(self,o:int) -> 'ModInt':
        return -(self - o)

    def __rmul__(self,o:int) -> 'ModInt':
        return self * o

    def __rtruediv__(self,o:int) -> 'ModInt':
        return ModInt(o,self.mod) / self

    def __pow__(self,o:'int|ModInt') -> 'ModInt':
        if isinstance(o,ModInt):
            o = o.n
        if isinstance(o,int):
            if o >= 0:
                return ModInt(integer.modpow(self.n,o,self.mod),self.mod)
            else:
                b = integer.modinv(self.n,self.mod)
                return ModInt(integer.modpow(b,-o,self.mod),self.mod)
        return NotImplemented

    def __rpow__(self,o:int) -> int:
        if isinstance(o,int):
            return o**self.n
        return NotImplemented

if __name__ == '__main__':

    import operator as op

    def raises(func,*args) -> bool:
        ''' returns true if func(*args) raises an exception '''
        try:
            func(*args)
            return False
        except:
            return True

    MI = ModInt

    # __init__
    assert raises(MI,0,0)
    assert MI(0,1).n == 0
    assert MI(0,1).mod == 1
    assert MI(0,7).n == 0
    assert MI(0,7).mod == 7
    assert MI(4,15).n == 4
    assert MI(-4,15).n == 11
    assert MI(4,15).mod == 15
    assert MI(62,15).n == 2
    assert MI(MI(-1,13)).n == 12
    assert MI(MI(-1,13)).mod == 13

    # __str__
    assert str(MI(0,1)) == '0'
    assert str(MI(-1,1)) == '0'
    assert str(MI(-3,12)) == '9'
    assert str(MI(16,11)) == '5'
    assert str(MI(3,5)) == '3'
    assert str(MI(-100,14)) == '12'

    # __eq__ ==
    assert raises(op.eq,MI(4,13),MI(4,11))
    assert raises(op.eq,MI(5,11),MI(6,19))
    assert MI(5,7) == 5
    assert MI(5,7) == -2
    assert MI(5,7) == 12
    assert MI(0,1) == 1234
    assert MI(-3,10) == 7
    assert MI(-3,10) == -3
    assert MI(-3,10) == 17
    assert MI(-3,10) == MI(27,10)
    assert MI(14,17) == MI(-3,17)
    assert MI(-20,83) == MI(893,83)

    # __ne__ !=
    assert raises(op.ne,MI(3,7),MI(3,10))
    assert MI(3,4) != '3'
    assert MI(3,4) != MI(2,4)
    assert MI(10,21) != MI(11,21)
    assert MI(6,7) != 7

    # __lt__ <
    assert raises(op.lt,MI(0,15),MI(0,16))
    assert not (MI(5,10) < 4)
    assert not (MI(5,10) < 5)
    assert MI(5,10) < 6
    assert not (MI(9,30) < MI(8,30))
    assert not (MI(9,30) < MI(9,30))
    assert MI(9,30) < MI(10,30)

    # __le__ <=
    assert raises(op.le,MI(0,15),MI(0,16))
    assert not (MI(5,10) <= 4)
    assert MI(5,10) <= 5
    assert MI(5,10) <= 6
    assert not (MI(9,30) <= MI(8,30))
    assert MI(9,30) <= MI(9,30)
    assert MI(9,30) <= MI(10,30)

    # __gt__ >
    assert raises(op.gt,MI(0,15),MI(0,16))
    assert MI(5,10) > 4
    assert not (MI(5,10) > 5)
    assert not (MI(5,10) > 6)
    assert MI(9,30) > MI(8,30)
    assert not (MI(9,30) > MI(9,30))
    assert not (MI(9,30) > MI(10,30))

    # __ge__ >=
    assert raises(op.ge,MI(0,15),MI(0,16))
    assert MI(5,10) >= 4
    assert MI(5,10) >= 5
    assert not (MI(5,10) >= 6)
    assert MI(9,30) >= MI(8,30)
    assert MI(9,30) >= MI(9,30)
    assert not (MI(9,30) >= MI(10,30))

    # __bool__
    assert bool(MI(0,1)) == False
    assert bool(MI(0,9)) == False
    assert bool(MI(1,1)) == False
    assert bool(MI(1,2)) == True
    assert bool(MI(3,9)) == True

    # __neg__ -
    assert -MI(0,1) == MI(0,1)
    assert -MI(0,3) == MI(0,3)
    assert -MI(1,3) == MI(2,3)
    assert -MI(12,30) == MI(18,30)
    assert -MI(-3,29) == MI(3,29)
    assert -MI(26,29) == MI(3,29)

    # __pos__ +
    assert +MI(0,1) == MI(0,1)
    assert +MI(3,16) == MI(3,16)
    assert +MI(0,16) == MI(0,16)
    assert +MI(8,16) == MI(8,16)

    # __invert__ ~
    assert raises(op.inv,MI(0,1))
    assert raises(op.inv,MI(0,2))
    assert ~MI(1,2) == MI(1,2)
    assert ~MI(1,3) == MI(1,3)
    assert ~MI(2,3) == MI(2,3)
    assert ~MI(2,5) == MI(3,5)
    assert ~MI(3,5) == MI(2,5)
    assert ~MI(2,19) == MI(10,19)
    assert ~MI(4,17) == MI(13,17)
    assert ~MI(5,24) == MI(5,24)

    # __int__
    assert int(MI(0,1)) == 0
    assert int(MI(0,18)) == 0
    assert int(MI(-1,18)) == 17
    assert int(MI(21,42)) == 21
    assert int(MI(31,42)) == 31

    # __add__ +
    assert raises(op.add,MI(1,6),MI(1,7))
    assert MI(0,1) + MI(0,1) == MI(0,1)
    assert MI(1,3) + MI(2,3) == MI(0,3)
    assert MI(7,10) + MI(4,10) == MI(1,10)
    assert MI(6,15) + 0 == MI(6,15)
    assert MI(12,23) + 14 == MI(3,23)
    assert MI(12,23) + (-3) == MI(9,23)

    # __sub__ -
    assert raises(op.sub,MI(13,21),MI(10,19))
    assert MI(0,1) - MI(0,1) == MI(0,1)
    assert MI(14,37) - MI(9,37) == MI(5,37)
    assert MI(21,31) - MI(0,31) == MI(21,31)
    assert MI(6,41) - MI(7,41) == MI(40,41)
    assert MI(5,17) - 3 == MI(2,17)
    assert MI(5,17) - 0 == MI(5,17)
    assert MI(5,17) - (-7) == MI(12,17)

    # __mul__ *
    assert raises(op.mul,MI(15,17),MI(11,13))
    assert MI(0,1) * MI(0,1) == MI(0,1)
    assert MI(1,2) * MI(1,2) == MI(1,2)
    assert MI(4,7) * MI(3,7) == MI(5,7)
    assert MI(-1,12) * MI(8,12) == MI(4,12)
    assert MI(5,13) * MI(7,13) == MI(-4,13)
    assert MI(5,18) * 2 == MI(10,18)
    assert MI(5,18) * 0 == MI(0,18)
    assert MI(5,18) * (-3) == MI(3,18)

    # __truediv__ /
    assert raises(op.truediv,MI(3,13),MI(4,11))
    assert raises(op.truediv,MI(4,8),MI(2,8))
    assert MI(1,2) / MI(1,2) == MI(1,2)
    assert MI(4,13) / MI(5,13) == MI(6,13)
    assert MI(3,9) / MI(2,9) == MI(6,9)

    # __radd__ +
    assert 0 + MI(5,8) == MI(5,8)
    assert 3 + MI(5,8) == MI(0,8)
    assert -6 + MI(5,8) == MI(7,8)

    # __rsub__ -
    assert 0 - MI(4,14) == MI(10,14)
    assert 12 - MI(4,14) == MI(8,14)
    assert -3 - MI(4,14) == MI(7,14)

    # __rmul__ *
    assert 0 * MI(3,6) == MI(0,6)
    assert -2 * MI(4,6) == MI(4,6)
    assert 3 * MI(3,6) == MI(3,6)

    # __rtruediv__ /
    assert raises(op.truediv,5,MI(2,20))
    assert 5 / MI(2,5) == MI(0,5)
    assert 3 / MI(5,7) == MI(2,7)
    assert -1 / MI(2,9) == MI(4,9)

    # __pow__ **
    assert raises(op.pow,MI(0,1),-1)
    assert raises(op.pow,MI(3,9),-2)
    assert MI(0,1) ** 5790 == MI(0,1)
    assert MI(0,1) ** 0 == MI(0,1)
    assert MI(1,15) ** 10 == MI(1,15)
    assert MI(4,15) ** -1 == MI(4,15)
    assert MI(7,15) ** -2 == MI(4,15)
    assert MI(12,17) ** -1 == MI(10,17)
    assert MI(12,17) ** -2 == MI(-2,17)
    assert MI(12,17) ** -16 == MI(1,17)
    assert MI(7,20) ** 8 == MI(1,20)

    # __rpow__ **
    assert 3 ** MI(0,1) == 1
    assert 4 ** MI(3,8) == 64
    assert 5 ** MI(15,13) == 25
    assert (-2) ** MI(-4,7) == -8
    assert 0 ** MI(0,15) == 1
    assert 0 ** MI(4,11) == 0
    assert (-7) ** MI(-12,14) == 49
