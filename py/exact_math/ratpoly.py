from ratfrac import RatFrac
import integer

class RatPoly:
    '''
    immutable representation of a polynomial with rational coefficients
    '''
    def __init__(self,*coefs:RatFrac|int|str,hi_to_lo=True):
        '''
        initialize with coefficients, default order is highest first
        '''
        if hi_to_lo:
            coefs = coefs[::-1]
        coeflist = [RatFrac(coef) for coef in coefs]
        while len(coeflist) > 0 and coeflist[-1] == 0:
            coeflist.pop()
        self.c = tuple(coeflist)

    def __repr__(self) -> str:
        return f'RatPoly({','.join(repr(c) for c in self.c[::-1])})'

    def __str__(self) -> str:
        if len(self.c) == 0:
            return '0'
        if len(self.c) == 1:
            return str(self.c[0])
        xstr = lambda i : '' if i == 0 else ('x' if i == 1 else f'x^{i}')
        cstr = lambda c : '-' if c == -1 else ('' if c == 1 else f'{c}*')
        ret = f'{cstr(self.c[-1])}{xstr(len(self.c)-1)}'
        for i in range(len(self.c)-2,0,-1):
            ci = self.c[i]
            if ci > 0:
                ret += f' + {cstr(ci)}{xstr(i)}'
            elif ci < 0:
                ret += f' - {cstr(-ci)}{xstr(i)}'
        c0 = self.c[0]
        if c0 > 0:
            ret += f' + {c0}'
        elif c0 < 0:
            ret += f' - {-c0}'
        return ret

    def __eq__(self, p: 'RatPoly') -> bool:
        return isinstance(p,RatPoly) and self.c == p.c

    def __ne__(self, p: 'RatPoly') -> bool:
        return not (self == p)

    def degree(self) -> int:
        '''
        exponent of the leading term
        '''
        return 0 if len(self.c) == 0 else len(self.c)-1

    def lead_coef(self) -> RatFrac:
        '''
        leading coefficient, 0 for the 0 polynomial
        '''
        return RatFrac() if len(self.c) == 0 else self.c[-1]

    def __hash__(self) -> int:
        return hash(self.c)

    def __bool__(self) -> bool:
        return len(self.c) > 0

    def __pos__(self) -> 'RatPoly':
        return self

    def __neg__(self) -> 'RatPoly':
        return RatPoly(*(-c for c in self.c),hi_to_lo=False)

    def __add__(self, p: 'int|str|RatFrac|RatPoly') -> 'RatPoly':
        if isinstance(p,RatPoly):
            if len(self.c) > len(p.c):
                t = list(self.c)
                u = p.c
            else:
                t = list(p.c)
                u = self.c
            for i,v in enumerate(u):
                t[i] += v
            return RatPoly(*t,hi_to_lo=False)
        elif isinstance(p,(RatFrac,int,str)):
            p = RatFrac(p)
            if len(self.c) == 0:
                return RatPoly(p,hi_to_lo=False)
            return RatPoly(*(c+p if i == 0 else c
                for i,c in enumerate(self.c)),hi_to_lo=False)
        return NotImplemented

    def __sub__(self, p: 'int|str|RatFrac|RatPoly') -> 'RatPoly':
        if isinstance(p,RatPoly):
            if len(self.c) > len(p.c):
                t = list(self.c)
                u = p.c
                swap = False
            else:
                t = list(p.c)
                u = self.c
                swap = True
            for i,v in enumerate(u):
                t[i] -= v
            r = RatPoly(*t,hi_to_lo=False)
            return -r if swap else r
        elif isinstance(p,(RatFrac,int,str)):
            p = RatFrac(p)
            if len(self.c) == 0:
                return RatPoly(-p,hi_to_lo=False)
            return RatPoly(*(c-p if i == 0 else c
                for i,c in enumerate(self.c)),hi_to_lo=False)
        return NotImplemented

    def __mul__(self, p: 'int|str|RatFrac|RatPoly') -> 'RatPoly':
        if isinstance(p,RatPoly):
            if len(self.c) == 0 or len(p.c) == 0:
                return RatPoly()
            t = [RatFrac(0)] * (len(self.c) + len(p.c) - 1)
            for i,ci in enumerate(self.c):
                for j,cj in enumerate(p.c):
                    t[i+j] += ci*cj
            return RatPoly(*t,hi_to_lo=False)
        elif isinstance(p,(RatFrac,int,str)):
            p = RatFrac(p)
            return RatPoly(*(p*c for c in self.c),hi_to_lo=False)
        return NotImplemented

    # TODO support division by ratpoly for rational functions
    def __truediv__(self, p: 'int|str|RatFrac') -> 'RatPoly':
        if isinstance(p,RatPoly):
            raise NotImplementedError('rational functions not supported yet')
        elif isinstance(p,(RatFrac,int,str)):
            p = RatFrac(p)
            return RatPoly(*(c/p for c in self.c),hi_to_lo=False)
        return NotImplemented

    def __floordiv__(self, p: 'int|str|RatFrac|RatPoly') -> 'RatPoly':
        if isinstance(p,RatPoly):
            return divmod(self,p)[0]
        elif isinstance(p,(RatFrac,int,str)):
            return self/RatFrac(p)
        return NotImplemented

    def __mod__(self, p: 'int|str|RatFrac|RatPoly') -> 'RatPoly':
        if isinstance(p,RatPoly):
            return divmod(self,p)[1]
        elif isinstance(p,(RatFrac,int,str)):
            return RatPoly()
        return NotImplemented

    def __divmod__(self, p: 'int|str|RatFrac|RatPoly') -> tuple['RatPoly','RatPoly']:
        if isinstance(p,RatPoly):
            assert p, 'division by 0'
            selfdeg = self.degree()
            pdeg = p.degree()
            if pdeg > selfdeg:
                return RatPoly(),self
            r = list(self.c) if len(self.c) > 0 else [RatFrac()]
            o = selfdeg - pdeg
            q = [RatFrac() for _ in range(o+1)]
            plead = p.lead_coef()
            while o >= 0:
                t = r[o+pdeg] / plead
                for i in range(pdeg+1):
                    r[o+i] -= t * p.c[i]
                q[o] = t
                o -= 1
            return RatPoly(*q,hi_to_lo=False),RatPoly(*r,hi_to_lo=False)
        elif isinstance(p,(RatFrac,int,str)):
            return self/RatFrac(p),RatPoly()
        return NotImplemented

    def __pow__(self, n: int) -> 'RatPoly':
        if not isinstance(n,int):
            return NotImplemented
        # TODO rational function for negative exponent
        if n < 0:
            raise NotImplementedError('rational functions not implemented yet')
        if n == 0:
            return RatPoly(1)
        b = self
        while n % 2 == 0:
            n //= 2
            b *= b
        ret = b
        n //= 2
        while n > 0:
            b *= b
            if n % 2 == 1:
                ret *= b
            n //= 2
        return ret

    def __radd__(self, o: int|str|RatFrac) -> 'RatPoly':
        if isinstance(o,(RatFrac,int,str)):
            return self+o
        return NotImplemented

    def __rsub__(self, o: int|str|RatFrac) -> 'RatPoly':
        if isinstance(o,(RatFrac,int,str)):
            return -(self-o)
        return NotImplemented

    def __rmul__(self, o: int|str|RatFrac) -> 'RatPoly':
        if isinstance(o,(RatFrac,int,str)):
            return self*o
        return NotImplemented

    # TODO rational function
    def __rtruediv__(self, o: int|str|RatFrac) -> 'RatPoly':
        raise NotImplementedError('rational functions not implemented yet')

    def _eval_normal(self, x: RatFrac|int|str) -> RatFrac:
        # basic method of polynomial evaluation
        x = RatFrac(x)
        ret = RatFrac()
        for i,c in enumerate(self.c):
            ret += c * x**i
        return ret

    def _eval_horner(self, x: RatFrac|int|str) -> RatFrac:
        # horners method reduces required multiplication
        x = RatFrac(x)
        if len(self.c) == 0:
            return RatFrac()
        ret = self.c[-1]
        for i in range(len(self.c)-2,-1,-1):
            ret = (ret*x) + self.c[i]
        return ret

    def eval(self, x: RatFrac|int|str) -> RatFrac:
        '''
        evaluate the polynomial at a point
        '''
        return self._eval_horner(x)

    def _compose_normal(self, p: 'RatPoly') -> 'RatPoly':
        # basic method
        ret = RatPoly()
        for i,c in enumerate(self.c):
            if c != 0:
                ret += c * p**i
        return ret

    def _compose_horner(self, p: 'RatPoly') -> 'RatPoly':
        # horners method
        if len(self.c) == 0:
            return RatPoly()
        ret = RatPoly(self.c[-1],hi_to_lo=False)
        for i in range(len(self.c)-2,-1,-1):
            ret = (ret*p) + self.c[i]
        return ret

    def compose(self, p: 'RatPoly') -> 'RatPoly':
        '''
        function composition with another polynomial
        '''
        return self._compose_horner(p)

    def __call__(self, x: 'RatFrac|int|str|RatPoly') -> 'RatFrac|RatPoly':
        if isinstance(x,RatPoly):
            return self.compose(x)
        elif isinstance(x,(RatFrac,int,str)):
            return self.eval(x)
        assert 0, f'cannot call RatPoly with type {type(x)}'

    def ratroots(self) -> list[RatFrac]:
        '''
        finds all distinct rational roots
        '''
        if len(self.c) < 2:
            return []
        i = 0
        while self.c[i] == 0:
            i += 1
        if i == self.degree():
            return [RatFrac()]
        ret = []
        if i > 0:
            ret.append(RatFrac())
            poly = RatPoly(*self.c[i:],hi_to_lo=False)
        else:
            poly = self
        m = integer.lcm(*(z.d for z in self.c))
        a0 = m * poly.c[0]
        an = m * poly.c[-1]
        tried = set()
        for p in integer.list_factors(abs(a0.n)):
            for q in integer.list_factors(abs(an.n)):
                r = RatFrac(p,q)
                if r not in tried:
                    tried.add(r)
                    if poly(r) == 0:
                        ret.append(r)
                    if poly(-r) == 0:
                        ret.append(-r)
        return sorted(ret)

    def derivative(self) -> 'RatPoly':
        '''
        derivative
        '''
        if len(self.c) < 2:
            return RatPoly()
        return RatPoly(*(i*self.c[i] for i in range(1,len(self.c))),hi_to_lo=False)

    def integral(self,C:int|str|RatFrac=0) -> 'RatPoly':
        '''
        integral with constant
        '''
        C = RatFrac(C)
        return RatPoly(C,*(c/(i+1) for i,c in enumerate(self.c)),hi_to_lo=False)

    # TODO multiple differentiation/integration
    # add optional parameter for how many times

    def discriminant(self) -> RatFrac:
        '''
        polynomial discriminant
        '''
        raise NotImplementedError('discriminant not implemented yet') # TODO

    @staticmethod
    def interpolate(*points:tuple[int|str|RatFrac,int|str|RatFrac]) -> 'RatPoly':
        '''
        interpolate n points to a degree n-1 polynomial
        '''
        raise NotImplementedError('polynomial interpolation not implemented yet') # TODO

    @staticmethod
    def parse_str(s: str) -> 'RatPoly':
        '''
        parse from a string formatted like the following examples
        '''
        raise NotImplementedError('polynomial string parsing not implemented yet') # TODO

if __name__ == '__main__':

    import operator as op

    def raises(func,*args) -> bool:
        ''' returns true if func(*args) raises an exception '''
        try:
            func(*args)
            return False
        except:
            return True

    RP = RatPoly
    RF = RatFrac

    # __init__
    assert RP().c == ()
    assert RP(0).c == ()
    assert RP(1).c == (1,)
    assert RP(1,-1).c == (-1,1)
    assert RP(5,0,-1,-2).c == (-2,-1,0,5)
    assert RP(-2,3,hi_to_lo=False).c == (-2,3)
    assert RP(-9,-6,1,hi_to_lo=False).c == (-9,-6,1)
    assert RP(0,6,-9).c == (-9,6)

    # __str__
    assert str(RP()) == '0'
    assert str(RP(-8)) == '-8'
    assert str(RP(RF(7,64))) == '7/64'
    assert str(RP(1,0)) == 'x'
    assert str(RP(1,1)) == 'x + 1'
    assert str(RP(1,-1)) == 'x - 1'
    assert str(RP(2,RF(1,123))) == '2*x + 1/123'
    assert str(RP('1/2','-1/2')) == '1/2*x - 1/2'
    assert str(RP('-1/4','5/3','-6/11')) == '-1/4*x^2 + 5/3*x - 6/11'
    assert str(RP(1,0,RF(1,2),'-1/2')) == 'x^3 + 1/2*x - 1/2'
    assert str(RP(0,6,-9)) == '6*x - 9'
    assert str(RP(1,-RF(1,2),RF(1,3),-RF(1,4),RF(1,5))) == 'x^4 - 1/2*x^3 + 1/3*x^2 - 1/4*x + 1/5'

    # __eq__
    assert RP() == RP(0)
    assert RP(0,1,2) == RP(1,2)
    assert RP(0,1,2,3) == RP(3,2,1,0,hi_to_lo=False)

    # __ne__
    assert RP() != RP('1/2')
    assert RP(1,'-1/2') != RP(1,'1/2')
    assert RP(1,0,0) != RP(1,0)

    # degree
    assert RP().degree() == 0
    assert RP(RF(-6,25)).degree() == 0
    assert RP(RF(2,5),RF(-4,25)).degree() == 1
    assert RP(RF(0),RF(1),RF(2)).degree() == 1
    assert RP(RF(1),0,0,0).degree() == 3

    # lead_coef
    assert RP().lead_coef() == 0
    assert RP('5/13').lead_coef() == '5/13'
    assert RP(5,0,-1).lead_coef() == 5
    assert RP(-5,0,1,hi_to_lo=False).lead_coef() == 1
    assert RP(0,0,1,-1).lead_coef() == 1

    # __bool__
    assert not bool(RP())
    assert bool(RP(RF(5,2)))
    assert bool(RP(6,RF(3,8)))

    # __pos__ +
    assert +RP(0) == RP()
    assert +RP(RF(-4,7)) == RP('-4/7')
    assert +RP(6,-12) == RP(6,-12)

    # __neg__ -
    assert -RP(3) == RP(-3)
    assert -RP(5,3,1) == RP(-5,-3,-1)
    assert -RP(1,0,0,-1) == RP(1,0,0,-1,hi_to_lo=False)

    # __add__ +
    assert RP() + RP(1,'2/3',RF(1,9)) == RP(1,RF(2,3),'1/9')
    assert RP(6,-1) + RP(-3,2) == RP(3,1)
    assert RP(4) + RP(1,-3,-4) == RP(1,-3,0)
    assert RP(5,6,7,8) + RP(-3,-4,-5) == RP(5,3,3,3)
    assert RP(7) + 3 == RP(10)
    assert RP(RF(1,2)) + '1/2' == RP(1)
    assert RP(1,-1,4) + RF(-2,5) == RP(1,-1,RF(18,5))

    # __sub__ -
    assert RP(RF(2,3),-6,RF(7,2)) - RP() == RP('2/3','-6','7/2')
    assert RP(3,6,9) - RP(9,-12) == RP(3,-3,21)
    assert RP(4,-2) - RP(2,-7,-9,16) == RP(-2,7,13,-18)
    assert RP(16) - RP(1,0,0,0,0) == RP(-1,0,0,0,16)
    assert RP(1,0,0,1) - RP(1,1) == RP(1,0,-1,0)
    assert RP(6,0) - '3/7' == RP(6,-RF(3,7))
    assert RP(1,1,-1) - 1 == RP(1,1,-2)
    assert RP() + RF(3,4) == RP('3/4')

    # __mul__ *
    assert RP() * RP('-6/17',3,0,0,-1,-2,'56867/3') == RP()
    assert RP(6,'-1/7',RF(-460,17)) * RP() == RP()
    assert RP('1/7') * RP('1/9') == RP('1/63')
    assert RP(1,-6) * RP(1,-6) == RP(1,-12,36)
    assert RP(1,-2) * RP(1,-3) == RP(1,-5,6)
    assert RP(1,'-3/2') * RP(1,RF(3,2)) == RP(1,0,RF(-9,4))
    assert RP(1,-5,6) * RP(1,-5,4) == RP(1,-10,35,-50,24)
    assert RP(1,-1) * RP(1,-2) * RP(1,-3) * RP(1,-4) == RP(1,-10,35,-50,24)
    assert RP(2,-6,7) * RP(1,0,-3,-1) == RP(2,-6,1,16,-15,-7)
    assert RP(1,7,-8) * RF(1,2) == RP(RF(1,2),RF(7,2),-4)
    assert RP(RF(1,3),RF(7,3)) * 3 == RP(1,7)
    assert RP(RF(1,7)) * '1/7' == RP('1/49')

    # __truediv__ /
    assert RP() / 64 == RP()
    assert RP(1,6,9) / 3 == RP(RF(1,3),2,3)
    assert RP(6,7,8) / '14/3' == RP(RF(9,7),RF(3,2),RF(12,7))
    assert RP(7,3) / RF(3,2) == RP('14/3',2)

    DIV_TESTS: list[tuple[RP,RP,RP,RP]] = [
        (RP(),RP(5),RP(),RP()),
        (RP(),RP(1,0,0,-1),RP(),RP()),
        (RP(RF(6,7)),RP(RF(3,4)),RP(RF(8,7)),RP()),
        (RP(2,-7),RP(1,1),RP(2),RP(-9)),
        (RP(1,-11,-42),RP(1,3),RP(1,-14),RP()),
        (RP(1,0,0,1),RP(2,1,1,1),RP(RF(1,2)),RP('-1/2','-1/2','1/2')),
        (RP(1,1,5,4),RP(RF(1,1000),0,0,0,0),RP(),RP(1,1,5,4)),
        (RP(3,-12,0,-14,-51,6),RP(2,-8,1),RP('3/2',0,'-3/4',-10),RP('-521/4',16)),
        (RP(1,7,-27,-135,378),RP(1,-3),RP(1,10,3,-126),RP()),
        (RP(1,7,-27,-135,378),RP(1,-6,9),RP(1,13,42),RP()),
        (RP(1,-6,2,-80,17),RP(1,-6),RP(1,0,2,-68),RP(-391)),
        (RP(6,-7,18,-19,20),RP(1,-4,3,-2),RP(6,17),RP(68,-58,54)),
        (RP(12,15,-61,-90,11),RP(4,-11,1),RP(3,12,17),RP(85,-6))
    ]

    # __floordiv__ //
    assert raises(op.floordiv,RP(1,2),RP())
    assert raises(op.floordiv,RP(),RP())
    for a,b,c,_ in DIV_TESTS:
        assert a // b == c, f'{a//b}'

    # __mod__ %
    assert raises(op.mod,RP(1,2),RP())
    assert raises(op.mod,RP(),RP())
    for a,b,_,c in DIV_TESTS:
        assert a % b == c, f'{a%b}'

    # __divmod__
    assert raises(divmod,RP(1,2),RP())
    assert raises(divmod,RP(),RP())
    for a,b,c,d in DIV_TESTS:
        assert divmod(a,b) == (c,d)
        assert c*b + d == a

    # __pow__ **
    assert RP()**0 == RP(1)
    assert RP()**1 == RP(0)
    assert RP(6)**3 == RP(216)
    assert RP(RF(2,7))**2 == RP(RF(4,49))
    assert RP(1,-1)**0 == RP(1)
    assert RP(1,-1)**1 == RP(1,-1)
    assert RP(1,-1)**2 == RP(1,-2,1)
    assert RP(1,-1)**3 == RP(1,-3,3,-1)
    assert RP(2,3)**3 == RP(8,36,54,27)
    assert RP(2,-3)**4 == RP(16,-96,216,-216,81)
    assert RP(1,'-1/2')**7 == RP(1,'-7/2','21/4','-35/8','35/16','-21/32','7/64','-1/128')
    assert RP(5,-2,1)**2 == RP(25,-20,14,-4,1)
    assert RP(5,-2,1)**3 == RP(125,-150,135,-68,27,-6,1)
    assert RP(-3,1,1,-7)**2 == RP(9,-6,-5,44,-13,-14,49)

    # __radd__ +
    assert 3 + RP() == RP(3)
    assert '2/3' + RP(RF(-1,3)) == RP('1/3')
    assert RF(-1,5) + RP(1,0) == RP(1,RF(-1,5))

    # __rsub__ -
    assert 7 - RP(1,0) == RP(-1,7)
    assert '1/2' - RP(RF(1,3)) == RP(RF(1,6))
    assert RF(14,3) - RP(-1,2) == RP(1,RF(8,3))

    # __rmul__ *
    assert 2 * RP(1,-1,5) == RP(2,-2,10)
    assert '1/2' * RP(1,-1,5) == RP('1/2','-1/2','5/2')
    assert RF(-3) * RP(7,11) == RP(-21,-33)

    # eval
    assert RP().eval(0) == 0
    assert RP().eval('-18/7') == 0
    assert RP().eval(RF(5,12)) == 0
    assert RP(7).eval(586) == 7
    assert RP(2,-1).eval(5) == 9
    assert RP(2,-1).eval(16) == 31
    assert RP(2,-1).eval(0) == -1
    assert RP('1/2',4,RF(-2,3)).eval(0) == '-2/3'
    assert RP('1/2',4,RF(-2,3)).eval(1) == '23/6'
    assert RP('1/2',4,RF(-2,3)).eval('4/3') == '50/9'
    assert RP('1/2',4,RF(-2,3)).eval(RF(-1,2)) == '-61/24'
    assert RP(RF(1,3),0,-RF(1,3),1).eval(0) == RF(1)
    assert RP(RF(1,3),0,-RF(1,3),1).eval('-3/4') == RF('71/64')
    assert RP(RF(1,3),0,-RF(1,3),1).eval(RF(-3)) == -7

    # compose
    assert RP().compose(RP()) == RP()
    assert RP().compose(RP(1,1,1)) == RP()
    assert RP(RF(-32,7)).compose(RP(RF(16,17))) == RP(RF(-32,7))
    assert RP(1,4).compose(RP(1,3)) == RP(1,7)
    assert RP(1,0,1).compose(RP(1,0,0,-1)) == RP(1,0,0,-2,0,0,2)
    assert RP(1,2,3).compose(RP(-1,2)) == RP(1,-6,11)
    assert RP(RF(1,2),'-2/3').compose(RP()) == RP('-2/3')
    assert RP(RF(2,3),RF(-1,2)).compose(RP(1,'1/2','-1/4')) == RP('2/3','1/3','-2/3')
    assert RP(1,0,-4,5).compose(RP(1,3,2)) == RP(1,9,33,63,62,24,5)
    assert RP(1,0,-4,5).compose(RP(3)) == RP(20)
    assert RP(1,0,-4,5).compose(RP()) == RP(5)

    # __call__
    assert RP(2,-1)('3/4') == '1/2'
    assert RP(1,0,0)(RF(2,3)) == RF(4,9)
    assert RP(1,0,2,3)(5) == 138
    assert RP(1,0,2,-1,-1)(RF(1,2)) == RF(-15,16)
    assert RP(1,-7)(RP()) == RP(-7)
    assert RP(2,-4)(RP(6,12,13)) == RP(12,24,22)
    assert RP(3,2,1)(RP(RF(1,2))) == RP(RF(11,4))

    # ratroots
    assert RP().ratroots() == []
    assert RP('-103/6').ratroots() == []
    assert RP(3,-4).ratroots() == ['4/3']
    assert RP(2,4).ratroots() == [-2]
    assert RP(7,0).ratroots() == [0]
    assert RP(1,-2,1).ratroots() == [1]
    assert RP(1,-3,2).ratroots() == [1,2]
    assert RP(1,1,0).ratroots() == [-1,0]
    assert RP(1,1,1).ratroots() == []
    assert RP(1,-1,-1).ratroots() == []
    assert RP(1,0,0,1).ratroots() == [-1]
    assert RP(1,0,0,-1).ratroots() == [1]
    assert RP(1,0,RF(-9,4),0).ratroots() == ['-3/2',0,'3/2']
    assert RP(-1,0,0,2).ratroots() == []
    assert RP('1/6','-13/36','1/6').ratroots() == ['2/3','3/2']
    assert RP('7','-140/3','700/9').ratroots() == ['10/3']
    assert RP('7','-140/3','700').ratroots() == []
    assert RP(2,0,1,-1).ratroots() == []
    assert RP(1,0,-7,6).ratroots() == [-3,1,2]
    assert RP(3,-5,5,-2).ratroots() == [RF(2,3)]
    assert RP(1,-2,'1/3','-1/4','11/12').ratroots() == [1]
    assert RP(3,0,'-7/2',4,'-7/2').ratroots() == [1]
    assert RP(5,-8,6,4).ratroots() == [RF(-2,5)]
    assert RP('4/3',6,-3,'5/3').ratroots() == [-5]
    assert RP('4/5',-1,'-1/2','1/3','1/30').ratroots() == [RF(1,2)]
    assert RP(1,-2,'3/2','-11/2',-6,'99/1024').ratroots() == [RF(-3,4)]
    assert RP(1,4,0,-8,1,0,0).ratroots() == [0]
    assert RP(1,0,-3,3,-3,-8).ratroots() == [-1]
    assert RP(5,0,0,RF(40,27),0,0).ratroots() == [RF(-2,3),RF(0)]

    # derivative
    assert RP().derivative() == RP()
    assert RP(RF(3,7)).derivative() == RP()
    assert RP(5,-6).derivative() == RP(5)
    assert RP(RF(1,2),2,-7).derivative() == RP(1,2)
    assert RP(1,0,0,0).derivative() == RP(3,0,0)
    assert RP('-4/3','-5/3','9/7','3/2','-9000/173').derivative() == RP('-16/3',-5,RF(18,7),RF(3,2))

    # integral
    assert RP().integral() == RP()
    assert RP().integral('1/7') == RP('1/7')
    assert RP().integral(6) == RP(6)
    assert RP().integral(RF(-5,3)) == RP(RF(-5,3))
    assert RP(3).integral() == RP(3,0)
    assert RP(3).integral(-2) == RP(3,-2)
    assert RP(1,2).integral() == RP('1/2',2,0)
    assert RP(1,0,0).integral(-1) == RP(RF(1,3),0,0,-1)
    assert RP('1/3',-8,RF(1,4),-2).integral('5/10') == RP('1/12','-8/3','1/8',-2,'1/2')

    # discriminant
    # TODO need RatMat

    # interpolate
    # TODO need RatMat

    # parse_str
    # TODO


