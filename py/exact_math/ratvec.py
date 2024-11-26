from ratfrac import RatFrac

class RatVec:
    '''
    immutable vector with rational components
    @ operator is dot product
    '''
    def __init__(self,*comps:RatFrac|int|str):
        '''
        vector initialization
        '''
        self.v = tuple(RatFrac(c) for c in comps)

    def __repr__(self) -> str:
        return f'RatVec({','.join(repr(c) for c in self.v)})'

    def __str__(self) -> str:
        return f'({','.join(str(c) for c in self.v)})'

    def __len__(self) -> int:
        return len(self.v)

    def __eq__(self,o:'RatVec') -> bool:
        if isinstance(o,RatVec):
            return self.v == o.v
        return NotImplemented

    def __ne__(self,o:'RatVec') -> bool:
        if isinstance(o,RatVec):
            return self.v != o.v
        return NotImplemented

    def __hash__(self) -> int:
        return hash(self.v)

    def __bool__(self) -> bool:
        return any(a != 0 for a in self.v)

    def __add__(self,o:'RatVec') -> 'RatVec':
        if isinstance(o,RatVec):
            if len(self.v) != len(o.v):
                raise Exception('different vector sizes')
            return RatVec(*(self.v[i] + o.v[i] for i in range(len(o.v))))
        return NotImplemented

    def __sub__(self,o:'RatVec') -> 'RatVec':
        if isinstance(o,RatVec):
            if len(self.v) != len(o.v):
                raise Exception('different vector sizes')
            return RatVec(*(self.v[i] - o.v[i] for i in range(len(o.v))))
        return NotImplemented

    def __mul__(self,o:RatFrac|int|str) -> 'RatVec':
        if isinstance(o,(RatFrac,int,str)):
            o = RatFrac(o)
            return RatVec(*(a*o for a in self.v))
        return NotImplemented

    def __truediv__(self,o:RatFrac|int|str) -> 'RatVec':
        if isinstance(o,(RatFrac,int,str)):
            o = RatFrac(o)
            return RatVec(*(a/o for a in self.v))
        return NotImplemented

    def __rmul__(self,o:RatFrac|int|str) -> 'RatVec':
        return self*o

    def __neg__(self) -> 'RatVec':
        return RatVec(*(-a for a in self.v))

    def __pos__(self) -> 'RatVec':
        return self

    # TODO norms with exact value
    def norm(self,p:RatFrac|int|str) -> RatFrac:
        '''
        p-norm, 0 for infinity/max
        '''
        p = RatFrac(p)
        assert p >= 0
        if p == 0:
            return max(abs(a) for a in self.v)
        return sum((abs(a)**p for a in self.v), RatFrac())**(~p)

    def __abs__(self) -> RatFrac:
        return self.norm(2)

    def dot(self,v:'RatVec') -> RatFrac:
        if len(self.v) != len(v.v):
            raise Exception('different vector sizes')
        return sum((self.v[i]*v.v[i] for i in range(len(v.v))), RatFrac())

    def __matmul__(self,o:'RatVec') -> RatFrac:
        if isinstance(o,RatVec):
            return self.dot(o)
        return NotImplemented

    def proj(self,v:'RatVec') -> 'RatVec':
        '''
        project onto vector v
        '''
        return (self.dot(v) / v.dot(v)) * v

    def anglecos(self,v:'RatVec') -> RatFrac:
        return self.dot(v) / (abs(self)*abs(v))

    def unit(self) -> 'RatVec':
        return self / abs(self)

    @staticmethod
    def fill(n: int, v: int|str|RatFrac) -> 'RatVec':
        '''
        n dimensional vector with value v repeated
        '''
        return RatVec(*((v,)*n))

    @staticmethod
    def zeros(n: int) -> 'RatVec':
        '''
        n dimensional zero vector
        '''
        return RatVec.fill(n,0)

    @staticmethod
    def ones(n: int) -> 'RatVec':
        '''
        n dimensional vector of ones
        '''
        return RatVec.fill(n,1)

    @staticmethod
    def basis(n: int, i: int) -> 'RatVec':
        '''
        n dimensional basis vector e_i (length 1 on the ith axis)
        '''
        assert n > 0 and 0 <= i < n
        return RatVec(*(1 if i == j else 0 for j in range(n)))

if __name__ == '__main__':

    import operator as op

    def raises(func,*args) -> bool:
        ''' returns true if func(*args) raises an exception '''
        try:
            func(*args)
            return False
        except:
            return True

    RF = RatFrac
    RV = RatVec

    # __init__
    assert RV().v == ()
    assert RV(5).v == (5,)
    assert RV(-RF(1,2),'-1/2').v == ('-1/2','-1/2')
    assert RV(0,0,0).v == (0,0,0)
    assert RV(1,'3/2',RF(2)).v == (RF(1),RF(3,2),RF(2))
    assert RV(-5,-6,RF(-7),'-8').v == (-5,-6,-7,-8)

    # __str__
    assert str(RV()) == '()'
    assert str(RV(-5)) == '(-5)'
    assert str(RV(RF(1,2),-RF(1,2))) == '(1/2,-1/2)'
    assert str(RV(3,'4/3',4)) == '(3,4/3,4)'

    # __len__
    assert len(RV()) == 0
    assert len(RV(1)) == 1
    assert len(RV(1,2)) == 2
    assert len(RV(-1,-2,-3)) == 3

    # __eq__ ==
    assert RV() == RV()
    assert RV('1/2',4) == RV(RF(1,2),RF(4))
    assert RV(6) == RV(6)

    # __ne__ !=
    assert RV() != RV(1)
    assert RV('1/2') != RV('1/3')
    assert RV(5,6,7) != RV(7,6,5)
    assert RV(0,0,0,1) != RV(0,0,0,2)

    # __bool__
    assert not bool(RV())
    assert not bool(RV(0))
    assert bool(RV('-1/12'))
    assert bool(RV(0,9))
    assert bool(RV(1,0))
    assert not bool(RV(0,0,0))
    assert bool(RV(0,0,'1/5'))

    # __add__ +
    assert raises(op.add,RV(),RV(1))
    assert raises(op.add,RV(5,6),RV(7,8,9))
    assert RV(6) + RV(-5) == RV(1)
    assert RV('5/2','3/2') + RV('-1/3','-1/3') == RV('13/6','7/6')
    assert RV(1,2,3,4) + RV(0,0,0,0) == RV(1,2,3,4)
    assert RV(1,6,-3,-2) + RV(-2,7,-2,9) == RV(-1,13,-5,7)

    # __sub__ -
    assert raises(op.sub,RV(-1),RV())
    assert raises(op.sub,RV(1,2,3),RV(4,5))
    assert RV(-7) - RV(-9) == RV(2)
    assert RV('1/3','7/3') - RV('1/3','-2/3') == RV(0,3)
    assert RV(8,7,6) - RV(0,0,0) == RV(8,7,6)
    assert RV(-1,-2,3,4) - RV(-6,7,-8,9) == RV(5,-9,11,-5)

    # __mul__ *
    assert RV() * 0 == RV()
    assert RV() * 123456789 == RV()
    assert RV(6) * '1/2' == RV(3)
    assert RV(5,7) * RF(1,2) == RV(RF(5,2),RF(7,2))
    assert RV(-6,8,-10) * RF(-1,3) == RV(2,'-8/3','10/3')

    # __truediv__ /
    assert raises(op.truediv,RV(1),0)
    assert RV() / 0 == RV()
    assert RV(5) / '2' == RV('5/2')
    assert RV(3) / RF(1,2) == RV(6)
    assert RV(6,-9) / -1 == RV(-6,9)
    assert RV(5,6,7) / RF(6) == RV('5/6',1,'7/6')

    # __rmul__ *
    assert 0 * RV() == RV()
    assert 987654321 * RV() == RV()
    assert '7' * RV(2,3) == RV(14,21)
    assert RF(3,2) * RV('2/3',RF(4,3)) == RV(1,2)

    # __neg__ -
    assert -RV() == RV()
    assert -RV(-2) == RV(2)
    assert -RV(2,-3) == RV(-2,3)

    # __pos__ +
    assert +RV() == RV()
    assert +RV('5/7') == RV('5/7')
    assert +RV(1,2,3,4) == RV(1,2,3,4)

    # norm
    assert RV(3,4).norm(0) == 4
    assert RV(3,4).norm(1) == 7
    assert RV(3,4).norm(2) == 5
    assert raises(RV(2,3).norm,2)
    assert RV(2,2,2,1,1,1).norm(3) == 3
    assert RV('5/91','-12/91').norm(2) == RF(1,7)
    assert RV('5/91','-12/91').norm(0) == RF(12,91)
    assert RV('2/7','3/7','6/7').norm(2) == 1

    # __abs__
    assert abs(RV(3,4)) == 5
    assert abs(RV(-5,-12)) == 13
    assert abs(RV('-3/10','2/5')) == '1/2'
    assert abs(RV('2/6','3/6','6/6')) == RF(7,6)

    # dot
    assert raises(RV(3).dot,RV())
    assert raises(RV(-1,-2).dot,RV(3,4,5))
    assert RV(1,-5).dot(RV(3,6)) == -27
    assert RV('3/5','4/5').dot(RV(1,7)) == RF(31,5)
    assert RV(3).dot(RV(-5)) == -15
    assert RV().dot(RV()) == 0
    assert RV(5,1,-1).dot(RV(-1,3,-3)) == 1

    # __matmul__ @
    assert RV() @ RV() == 0
    assert RV(2,3,6) @ RV(2,3,6) == 49
    assert RV(-5,6) @ RV(6,5) == 0

    # proj
    assert raises(RV().proj,RV())
    assert raises(RV(5).proj,RV(6,7))
    assert RV(7).proj(RV(-3)) == RV(7)
    assert RV(-3).proj(RV(7)) == RV(-3)
    assert RV(3,-3).proj(RV(2,2)) == RV(0,0)
    assert RV(3,-3).proj(RV(1,'6/5')) == RV(-15,-18)/61
    assert RV(4,'3/2','7/3').proj(RV(0,1,0)) == RV(0,'3/2',0)
    assert RV('-12/5','14/3','11/2').proj(RV('1/2','1/3','1/5')) == RV('655/361','1310/1083','262/361')

    # anglecos
    assert raises(RV().anglecos,RV())
    assert raises(RV(0).anglecos,RV(5))
    assert RV(3).anglecos(RV(6)) == 1
    assert RV(2).anglecos(RV('-1/2')) == -1
    assert RV(0,1).anglecos(RV('3/5','4/5')) == RF(4,5)
    assert RV('-25/13','-60/13').anglecos(RV(8,15)) == RF(-220,221)

    # unit
    assert RV().unit() == RV()
    assert RV(5).unit() == RV(1)
    assert RV(-3).unit() == RV(-1)
    assert RV(-3,4).unit() == RV('-3/5','4/5')
    assert RV(3,-6,-2).unit() == RV('3/7','-6/7','-2/7')

    # fill
    assert RV.fill(5,RF(-5,12)) == RV('-5/12','-5/12','-5/12','-5/12','-5/12')
    assert RV.fill(1,1) == RV(1)
    assert RV.fill(0,-1) == RV()
    assert RV.fill(3,'6/2') == RV(3,3,3)

    # zeros
    assert RV.zeros(0) == RV()
    assert RV.zeros(1) == RV(0)
    assert RV.zeros(2) == RV(0,0)
    assert RV.zeros(3) == RV(0,0,0)

    # ones
    assert RV.ones(0) == RV()
    assert RV.ones(1) == RV(1)
    assert RV.ones(2) == RV(1,1)
    assert RV.ones(3) == RV(1,1,1)

    # basis
    assert raises(RV.basis,0,0)
    assert raises(RV.basis,1,1)
    assert raises(RV.basis,2,2)
    assert raises(RV.basis,2,-1)
    assert RV.basis(1,0) == RV(1)
    assert RV.basis(2,0) == RV(1,0)
    assert RV.basis(2,1) == RV(0,1)
    assert RV.basis(3,0) == RV(1,0,0)
    assert RV.basis(3,1) == RV(0,1,0)
    assert RV.basis(3,2) == RV(0,0,1)
