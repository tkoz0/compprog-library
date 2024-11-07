
class RatFrac:
    '''
    an immutable fraction class that behaves like python's fraction
    but it only allows operations that maintain exact rational results
    new operator: ~ flips the fraction
    '''
    def __init__(self,n:int=0,d:int=1):
        assert isinstance(n,int)
        assert isinstance(d,int)
        assert d != 0
        if d < 0:
            d = -d
            n = -n
        self.n = n
        self.d = d
        self._simplify()

    def ratio(self) -> tuple[int,int]:
        ''' returns tuple of numerator and denominator '''
        return (self.n,self.d)

    @staticmethod
    def _gcd(a:int,b:int) -> int:
        while b != 0:
            a,b = b,a%b
        return a

    @staticmethod
    def _lcm(a:int,b:int) -> int:
        return a*b//RatFrac._gcd(a,b)

    def _simplify(self):
        g = RatFrac._gcd(self.n,self.d)
        self.n //= g
        self.d //= g

    def __repr__(self) -> str:
        return f'RatFrac({self.n},{self.d})'

    def __str__(self) -> str:
        return f'{self.n}' if self.d == 1 else f'{self.n}/{self.d}'

    def _make_cmp_ints(self,o:'RatFrac|int') -> tuple[int,int]:
        if isinstance(o,int):
            return (self.n,o*self.d)
        elif isinstance(o,RatFrac):
            return (self.n*o.d, o.n*self.d)
        else:
            assert 0, 'frac can be compared with only frac or int'

    def __lt__(self,o:'RatFrac|int') -> bool:
        a,b = self._make_cmp_ints(o)
        return a < b

    def __le__(self,o:'RatFrac|int') -> bool:
        a,b = self._make_cmp_ints(o)
        return a <= b

    def __eq__(self,o:'RatFrac|int') -> bool:
        # fractions are kept in simplified form so this is ok
        if isinstance(o,int):
            return self.n == o and self.d == 1
        elif isinstance(o,RatFrac):
            return self.n == o.n and self.d == o.d
        else:
            assert 0, 'frac can be compared with only frac or int'

    def __ne__(self,o:'RatFrac|int') -> bool:
        return not (self == o)

    def __gt__(self,o:'RatFrac|int') -> bool:
        a,b = self._make_cmp_ints(o)
        return a > b

    def __ge__(self,o:'RatFrac|int') -> bool:
        a,b = self._make_cmp_ints(o)
        return a >= b

    def __hash__(self) -> int:
        return hash((self.n,self.d))

    def __bool__(self) -> int:
        # unique representation of 0 is 0/1
        return self.n != 0

    def __add__(self,o:'RatFrac|int') -> 'RatFrac':
        if isinstance(o,int):
            return RatFrac(self.n + self.d*o, self.d)
        elif isinstance(o,RatFrac):
            l = RatFrac._lcm(self.d,o.d)
            return RatFrac(self.n*l//self.d + o.n*l//o.d, l)
        else:
            assert 0, 'frac arithmetic supported only with frac or int'

    def __sub__(self,o:'RatFrac|int') -> 'RatFrac':
        if isinstance(o,int):
            return RatFrac(self.n - self.d*o, self.d)
        elif isinstance(o,RatFrac):
            l = RatFrac._lcm(self.d,o.d)
            return RatFrac(self.n*l//self.d - o.n*l//o.d, l)
        else:
            assert 0, 'frac arithmetic supported only with frac or int'

    def __mul__(self,o:'RatFrac|int') -> 'RatFrac':
        if isinstance(o,int):
            return RatFrac(self.n*o, self.d)
        elif isinstance(o,RatFrac):
            return RatFrac(self.n*o.n, self.d*o.d)
        else:
            assert 0, 'frac arithmetic supported only with frac or int'

    def __truediv__(self,o:'RatFrac|int') -> 'RatFrac':
        if isinstance(o,int):
            return RatFrac(self.n,self.d*o)
        elif isinstance(o,RatFrac):
            return RatFrac(self.n*o.d, self.d*o.n)
        else:
            assert 0, 'frac arithmetic supported only with frac or int'

    def __floordiv__(self,o:'RatFrac|int') -> int:
        return (self/o).__floor__()

    def __mod__(self,o:'RatFrac|int') -> 'RatFrac':
        if isinstance(o,int):
            return RatFrac(self.n % (self.d*o), self.d)
        elif isinstance(o,RatFrac):
            l = RatFrac._lcm(self.d,o.d)
            return RatFrac((self.n*l//self.d) % (o.n*l//o.d), l)
        else:
            assert 0, 'frac arithmetic supported only with frac or int'

    def __divmod__(self,o:'RatFrac|int') -> tuple[int,'RatFrac']:
        return (self//o,self%o)

    @staticmethod
    def _iroot(r:int,n:int) -> int:
        # integer rth root of n with binary method
        # raises exception for irrational result
        # TODO changing this behavior may be desirable
        assert r >= 1
        assert n >= 0
        if r == 1:
            return n
        if n <= 1:
            return n
        ret = 1
        while (ret<<1)**r <= n:
            ret <<= 1
        bit = ret >> 1
        while bit:
            if (ret|bit)**r <= n:
                ret |= bit
            bit >>= 1
        if ret**r != n:
            assert 0, 'irrational result'
        return ret

    # TODO maybe make this return some kind of integer radical type
    def __pow__(self,o:'RatFrac|int') -> 'RatFrac':
        if isinstance(o,int):
            if o > 0:
                return RatFrac(self.n**o, self.d**o)
            elif o < 0:
                return RatFrac(self.d**(-o), self.n**(-o))
            else:
                return RatFrac(1)
        elif isinstance(o,RatFrac):
            if o.d == 1:
                return self**o.n
            # compute dth roots
            if o.d % 2 == 0 and self.n < 0:
                assert 0, 'even root of negative value'
            rn = RatFrac._iroot(o.d,self.n) if self.n >= 0 else -RatFrac._iroot(o.d,-self.n)
            rd = RatFrac._iroot(o.d,self.d)
            return RatFrac(rn,rd)**o.n
        else:
            assert 0, 'frac arithmetic only supported with frac or int'

    def __radd__(self,o:int) -> 'RatFrac':
        assert isinstance(o,int)
        return self+o

    def __rsub__(self,o:int) -> 'RatFrac':
        assert isinstance(o,int)
        return -(self-o)

    def __rmul__(self,o:int) -> 'RatFrac':
        assert isinstance(o,int)
        return self*o

    def __rtruediv__(self,o:int) -> 'RatFrac':
        assert isinstance(o,int)
        return RatFrac(o)/self

    def __rfloordiv__(self,o:int) -> int:
        assert isinstance(o,int)
        return RatFrac(o)//self

    def __rmod__(self,o:int) -> 'RatFrac':
        assert isinstance(o,int)
        return RatFrac(o)%self

    def __rdivmod__(self,o:int) -> tuple[int,'RatFrac']:
        assert isinstance(o,int)
        return divmod(RatFrac(o),self)

    def __rpow__(self,o:int) -> 'RatFrac':
        assert isinstance(o,int)
        if o < 0:
            if self.d % 2 == 0:
                assert 0, 'even root of a negative value'
            r = -RatFrac._iroot(self.d,-o)
            return RatFrac(r)**self.n
        else:
            r = RatFrac._iroot(self.d,o)
            return RatFrac(r)**self.n

    def __neg__(self) -> 'RatFrac':
        return RatFrac(-self.n,self.d)

    def __pos__(self) -> 'RatFrac':
        return self

    def __abs__(self) -> 'RatFrac':
        return RatFrac(abs(self.n),self.d)

    def __invert__(self) -> 'RatFrac':
        return RatFrac(self.d,self.n)

    def __round__(self) -> int:
        if self.d == 1:
            return self.n
        elif self.d == 2:
            # round to even
            r = self.n % 4
            return self.n//2 if r == 1 else (self.n+1)//2
        else:
            q,r = divmod(self.n,self.d)
            return q if r <= self.d//2 else q+1

    def __trunc__(self) -> int:
        # round toward 0
        return self.__ceil__() if self.n < 0 else self.__floor__()

    def __floor__(self) -> int:
        return self.n//self.d

    def __ceil__(self) -> int:
        q,r = divmod(self.n,self.d)
        return q if r == 0 else q+1

    def _approx_slow(self, max_denom: int) -> 'RatFrac':
        # slow algorithm (try every denominator)
        best_frac = RatFrac(self.n//self.d)
        best_diff = RatFrac(1)
        for d in range(1,max_denom+1):
            n,rem = divmod(self.n*d,self.d)
            if rem > self.d//2:
                n += 1
            frac = RatFrac(n,d)
            diff = abs(self-frac)
            if diff < best_diff:
                best_frac = frac
                best_diff = diff
        return best_frac

    def _approx_fast(self, max_denom: int) -> 'RatFrac':
        # fast algorithm (using (semi)convergents)
        if self.d <= max_denom:
            return self
        h0,k0,h1,k1 = 0,1,1,0 # initialize with 0/1 and 1/0
        # note: at any point, h0*k1 - k0*h1 = 1 or -1
        n,d = self.n,self.d # n/d is next value to use for continued fraction
        # compute convergents as long as d <= max_denom
        while True:
            a = n//d # number in continued fraction representation
            h2,k2 = a*h1 + h0, a*k1 + k0 # next convergent
            if k2 > max_denom:
                break
            h0,k0,h1,k1 = h1,k1,h2,k2
            n,d = d, n - a*d # subtract a and flip
        # pick the semiconvergent that gets closest within max_denom constraint
        s = (max_denom - k0) // k1
        hs,ks = h0 + s*h1, k0 + s*k1
        # distance between h1/k1 and hs/ks is 1/(k1*ks)
        # distance between h1,k1 and self.n/self.d is d/(k1*self.d)
        # (show by induction, may be a little complicated, base case d/self.d)
        return RatFrac(h1,k1) if 2*d*ks <= self.d else RatFrac(hs,ks)

    def approx(self, max_denom: int) -> 'RatFrac':
        '''
        finds the closest rational approximation with a maximum denominator
        if max_denom==1 and number is halfway between integers, uses the floor
        '''
        assert max_denom >= 1
        # the fast algorithm should always be used in practice
        # slow algorithm is left in as an option for testing
        return self._approx_fast(max_denom)

if __name__ == '__main__':

    #from fractions import Fraction as PF
    from math import trunc, floor, ceil
    import operator as op

    def raises(func,*args) -> bool:
        ''' returns true if func(*args) raises an exception '''
        try:
            func(*args)
            return False
        except:
            return True

    RF = RatFrac

    # __init__ and ratio
    assert raises(RF,0,0)
    assert raises(RF,3,0)
    assert raises(RF,-4,0)
    assert RF(5,6).ratio() == (5,6)
    assert RF(2,4).ratio() == (1,2)
    assert RF(-6,15).ratio() == (-2,5)
    assert RF(-16,-24).ratio() == (2,3)
    assert RF(3,-4).ratio() == (-3,4)
    assert RF(18,30).ratio() == (3,5)
    assert RF(30,18).ratio() == (5,3)
    assert RF(-650,50).ratio() == (-13,1)
    assert RF(-6).ratio() == (-6,1)
    assert RF(7).ratio() == (7,1)
    assert RF(0).ratio() == (0,1)
    assert RF(0,-8).ratio() == (0,1)

    # __str__
    assert str(RF(5,10)) == '1/2'
    assert str(RF(-2,3)) == '-2/3'
    assert str(RF(12,-15)) == '-4/5'
    assert str(RF(0)) == '0'
    assert str(RF(-6)) == '-6'
    assert str(RF(20)) == '20'

    # __eq__ ==
    assert RF(1,2) == RF(1,2)
    assert RF(1,2) == RF(2,4)
    assert RF(-1,-2) == RF(1,2)
    assert RF(7,8) == RF(175,200)
    assert RF(-1,1) == RF(-1)
    assert RF(1,-3) == RF(-1,3)
    assert RF(-11,-15) == RF(110,150)
    assert RF(0) == RF(0,-12)

    # __ne__ !=
    assert RF(1,2) != RF(2,3)
    assert RF(1) != RF(2)
    assert RF(-1,2) != RF(1,2)
    assert RF(2,-3) != RF(2,3)
    assert RF(-6,15) != RF(-8,15)
    assert RF(0) != RF(1)
    assert RF(0,5) != RF(-1,2)

    # tuples of (a,b,comp) where comp is lt,gt,eq
    CMP_TESTS: list[tuple[int|RF,int|RF,str]] = [
        (RF(0),RF(0),'eq'),
        (RF(0),RF(1),'lt'),
        (RF(5),RF(5),'eq'),
        (RF(8),RF(17,5),'gt'),
        (RF(1,99),RF(1,100),'gt'),
        (RF(23,33),RF(7,10),'lt'),
        (RF(12,24),RF(1,2),'eq'),
        (RF(-91,100),RF(-9,10),'lt'),
        (0,RF(0),'eq'),
        (RF(0),0,'eq'),
        (73,RF(73),'eq'),
        (RF(7),12,'lt'),
        (RF(-8),-10,'gt'),
        (RF(2,3),RF(3,4),'lt'),
        (RF(600,17),RF(89,4),'gt'),
        (RF(-7,5),RF(877,3),'lt'),
        (RF(58,6),RF(43,-43),'gt'),
        (12,RF(11),'gt'),
        (76,RF(1000,11),'lt')
    ]

    # __eq__ ==
    for a,b,c in CMP_TESTS:
        assert a == b if c == 'eq' else not (a == b), (a,b,c)

    # __ne__ !=
    for a,b,c in CMP_TESTS:
        assert not (a != b) if c == 'eq' else a != b, (a,b,c)

    # __lt__ <
    for a,b,c in CMP_TESTS:
        assert a < b if c == 'lt' else not (a < b), (a,b,c)

    # __le__ <=
    for a,b,c in CMP_TESTS:
        assert not (a <= b) if c == 'gt' else a <= b, (a,b,c)

    # __gt__ >
    for a,b,c in CMP_TESTS:
        assert a > b if c == 'gt' else not (a > b), (a,b,c)

    # __ge__ >=
    for a,b,c in CMP_TESTS:
        assert not (a >= b) if c == 'lt' else a >= b, (a,b,c)

    # __bool__
    assert bool(RF()) == False
    assert bool(RF(0)) == False
    assert bool(RF(-5,9)) == True
    assert bool(RF(6,-2)) == True
    assert bool(RF(0,12)) == False
    assert bool(RF(1,2)) == True

    # __add__ +
    assert RF(60) + 91 == 151
    assert RF(7,3) + RF(2,3) == 3
    assert RF(1,5) + RF(1,5) == RF(2,5)
    assert RF(6,-7) + RF(6,7) == RF()
    assert RF(4,3) + RF(7,5) == RF(41,15)
    assert RF(1,6) + RF(1,3) == RF(1,2)
    assert RF(1,6) + RF(-1,7) == RF(1,42)
    assert RF(1,6) + RF(3,8) == RF(13,24)
    assert RF(1,6) + 0 == RF(1,6)
    assert RF(1,6) + 3 == RF(19,6)
    assert RF(-12) + RF(8,5) == RF(-52,5)

    # __sub__ -
    assert RF(1,12) - RF(1,30) == RF(1,20)
    assert RF(6) - 7 == -1
    assert RF(12,5) - RF(8,5) == RF(4,5)
    assert RF(23,33) - RF(4,11) == RF(1,3)
    assert RF(1,7) - RF(1,5) == RF(-2,35)
    assert RF(16,7) - RF(18,-7) == RF(34,7)
    assert RF(1,6) - RF(1,2) == RF(-1,3)
    assert RF(25,12) - RF(4,9) == RF(59,36)
    assert RF(16,7) - 0 == RF(16,7)
    assert RF(87,40) - 2 == RF(7,40)

    # __mul__ *
    assert RF(1,3) * 6 == 2
    assert RF(3,7) * 7 == RF(3)
    assert RF(2,3) * RF(3,4) == RF(1,2)
    assert RF(12,29) * 0 == 0
    assert RF(12,-89) * RF(-89,12) == 1
    assert RF(1,2) * RF(1,2) == RF(1,4)
    assert RF(3,40) * RF(1,5) == RF(3,200)
    assert RF(14,3) * -2 == RF(-28,3)
    assert RF(-3,2) * 3 == RF(-9,2)

    # __truediv__ /
    assert raises(op.truediv,RF(1,7),0)
    assert raises(op.truediv,RF(1,9),RF(0,-5))
    assert RF(1,2) / RF(1,2) == 1
    assert RF(8,15) / RF(4,9) == RF(6,5)
    assert RF(-6,5) / 2 == RF(-3,5)
    assert RF(2) / RF(3) == RF(2,3)
    assert RF(5,2) / RF(1,4) == 10
    assert RF(12,5) / RF(27,5) == RF(4,9)
    assert RF(7,15) / RF(4) == RF(7,60)

    DIV_TESTS: list[tuple[RF|int,RF|int,int,RF]] = [
        (RF(80),7,11,RF(3)),
        (RF(127),17,7,RF(8)),
        (RF(1,2),1,0,RF(1,2)),
        (RF(-1,2),1,-1,RF(1,2)),
        (RF(2,3),RF(-1,4),-3,RF(-1,12)),
        (RF(60,13),RF(4,5),5,RF(8,13)),
        (RF(-61,12),RF(-41,30),3,RF(-59,60)),
        (RF(15,2),RF(2),3,RF(3,2)),
        (RF(15,2),RF(-2),-4,RF(-1,2))
    ]

    # __floordiv__ //
    assert raises(op.floordiv,RF(8,3),0)
    assert raises(op.floordiv,RF(0),RF(0))
    for a,b,c,_ in DIV_TESTS:
        assert a // b == c

    # __mod__ %
    assert raises(op.mod,RF(8,3),RF(0))
    assert raises(op.mod,RF(0),0)
    for a,b,_,c in DIV_TESTS:
        assert a % b == c

    # __divmod__
    assert raises(divmod,RF(8,3),RF(0))
    assert raises(divmod,RF(0),0)
    for a,b,c,d in DIV_TESTS:
        assert divmod(a,b) == (c,d)
        assert c*b + d == a

    # __pow__ **
    assert RF(0) ** 0 == 1
    assert RF(0) ** 1 == 0
    assert RF(0) ** 2 == 0
    assert RF(0) ** RF(0) == 1
    assert RF(0) ** RF(1) == 0
    assert RF(0) ** RF(2) == 0
    assert raises(op.pow,RF(0),-1)
    assert raises(op.pow,RF(0),-2)
    assert raises(op.pow,RF(0),RF(-1))
    assert raises(op.pow,RF(0),RF(-2))
    assert RF(3,7) ** 3 == RF(27,343)
    assert RF(-3,7) ** 3 == RF(-27,343)
    assert RF(3,7) ** -3 == RF(343,27)
    assert RF(-3,7) ** -3 == RF(-343,27)
    assert RF(1,2) ** 11 == RF(1,2048)
    assert RF(1,2) ** -11 == 2048
    assert RF(-1,7) ** 4 == RF(1,2401)
    assert RF(-1,7) ** -4 == 2401
    assert raises(op.pow,RF(-2,7),RF(1,2))
    assert raises(op.pow,RF(-80,9),RF(-7,2))
    assert RF(-216,343) ** RF(1,3) == RF(-6,7)
    assert raises(op.pow,RF(-216,342),RF(1,3))
    assert RF(64,729) ** RF(2,3) == RF(16,81)
    assert RF(484,49) ** RF(1,2) == RF(22,7)
    assert RF(49,484) ** RF(-1,2) == RF(22,7)
    assert raises(op.pow,RF(5610,67),RF(4,11))
    assert raises(op.pow,RF(-617,47),RF(-7,4))

    # __radd__ +
    assert 6 + RF(1,2) == RF(13,2)
    assert 0 + RF(5,12) == RF(5,12)
    assert 8 + RF(6) == 14

    # __rsub__ -
    assert 3 - RF(2) == RF(1)
    assert 3 - RF(2,7) == RF(19,7)
    assert 8 - RF(6) == 2

    # __rmul__ *
    assert 3 * RF(2,3) == 2
    assert 4 * RF(6,7) == RF(24,7)
    assert 0 * RF(6789,1234) == 0

    # __rtruediv__ /
    assert 12 / RF(4) == 3
    assert 0 / RF(65,7) == 0
    assert 15 / RF(10,3) == RF(9,2)

    # __rfloordiv__ //
    assert 12 // RF(7,6) == 10
    assert -1 // RF(2) == -1
    assert -7 // RF(-3,2) == 4

    # __rmod__ %
    assert 16 % RF(5) == 1
    assert 12 % RF(7,3) == RF(1,3)
    assert 8 % RF(-3,11) == RF(-2,11)

    # __rdivmod__
    assert divmod(7,RF(3,5)) == (11,RF(2,5))
    assert divmod(14,RF(-17,12)) == (-10,RF(-1,6))
    assert raises(divmod,10,RF(0))

    # __rpow__ **
    assert 0**RF(0) == 1
    assert 0**RF(1) == 0
    assert raises(op.pow,0,RF(-1))
    assert raises(op.pow,0,RF(-2,5))
    assert 2**RF(6) == 64
    assert 64**RF(1,6) == 2
    assert 729**RF(4,3) == 6561
    assert 6561**RF(1,2) == 81
    assert 16**RF(-1,2) == RF(1,4)
    assert (-6)**RF(3) == -216
    assert raises(op.pow,-1216,RF(1,4))
    assert raises(op.pow,-215,RF(1,3))
    assert (-5)**RF(2) == 25
    assert 256**RF(3,4) == 64
    assert (-4096)**RF(2,3) == 256

    # __neg__ -
    assert -RF(0) == RF(0)
    assert -RF(1,8) == RF(-1,8)
    assert -RF(-3,14) == RF(3,14)

    # __pos__ +
    assert +RF(0) == RF(0)
    assert +RF(1,8) == RF(1,8)
    assert +RF(-3,14) == RF(-3,14)

    # __abs__
    assert abs(RF(0)) == RF(0)
    assert abs(RF(1,8)) == RF(1,8)
    assert abs(RF(-3,14)) == RF(3,14)

    # __invert__ ~
    assert raises(op.inv,RF(0))
    assert ~RF(1,8) == 8
    assert ~RF(-3,14) == RF(-14,3)

    # __round__
    assert round(RF(0)) == 0
    assert round(RF(-3)) == -3
    assert round(RF(6)) == 6
    assert round(RF(17,2)) == 8
    assert round(RF(15,2)) == 8
    assert round(RF(1,3)) == 0
    assert round(RF(2,3)) == 1
    assert round(RF(22,5)) == 4
    assert round(RF(23,5)) == 5
    assert round(RF(-17,6)) == -3
    assert round(RF(-17,4)) == -4

    # __trunc__
    assert trunc(RF(0)) == 0
    assert trunc(RF(-3)) == -3
    assert trunc(RF(6)) == 6
    assert trunc(RF(99,20)) == 4
    assert trunc(RF(101,20)) == 5
    assert trunc(RF(-65,16)) == -4
    assert trunc(RF(-63,16)) == -3
    assert trunc(RF(-1,12)) == 0
    assert trunc(RF(1,9)) == 0

    # __floor__
    assert floor(RF(0)) == 0
    assert floor(RF(-3)) == -3
    assert floor(RF(6)) == 6
    assert floor(RF(-6,7)) == -1
    assert floor(RF(-8,7)) == -2
    assert floor(RF(56,13)) == 4
    assert floor(RF(62,13)) == 4
    assert floor(RF(67,13)) == 5

    # __ceil__
    assert ceil(RF(0)) == 0
    assert ceil(RF(-3)) == -3
    assert ceil(RF(6)) == 6
    assert ceil(RF(-6,7)) == 0
    assert ceil(RF(-8,7)) == -1
    assert ceil(RF(50,13)) == 4
    assert ceil(RF(56,13)) == 5
    assert ceil(RF(62,13)) == 5

    # approx
    assert RF(5).approx(24) == RF(5)
    assert RF(4,3).approx(2) == RF(3,2)
    assert RF(4,3).approx(1) == RF(1)
    assert RF(5,3).approx(2) == RF(3,2)
    assert RF(5,3).approx(1) == RF(2)
    assert RF(7,2).approx(1) == 3
    assert RF(9,2).approx(1) == 4
    assert RF(314,100).approx(20) == RF(22,7)
    assert RF(314,100).approx(30) == RF(91,29)
    assert RF(271828,100000).approx(100) == RF(193,71)
    assert RF(271828,100000).approx(1000) == RF(1264,465)
    assert RF(271828,100000).approx(465) == RF(1264,465)
    assert RF(271828,100000).approx(464) == RF(1071,394)
    assert RF(661359,1000000).approx(1000) == RF(623,942)
    assert RF(982364859,12371399).approx(1000) == RF(59634,751)
    assert RF(-538689314,69012129).approx(1000) == RF(-6549,839)
    assert RF(-195621288289942163063,162289497291).approx(30000) == RF(-34607802118098,28711)
    assert RF(5738648626427468489168946151,509709478686285916).approx(30000) == RF(321581268488696,28563)
    assert RF(-1856719865,486286485183).approx(10000) == RF(-32,8381)
    assert RF(7286718651,815869864189).approx(10000) == RF(30,3359)
