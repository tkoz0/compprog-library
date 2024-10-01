'''
integer math functions, including some that python already has
'''
import random

def gcd(a:int,b:int) -> int:
    ''' greatest commmon divisor '''
    # euclidean algorithm
    if a < 0:
        a = -a
    if b < 0:
        b = -b
    if a < b:
        a,b = b,a
    assert a != 0, 'gcd(0,0) undefined'
    while b != 0:
        a,b = b,a%b
    return a

def lcm(a:int,b:int) -> int:
    ''' lowest common multiple '''
    return abs(a*b)//gcd(a,b)

def perm(n:int,k:int) -> int:
    ''' permutations nPk '''
    # n * (n-1) * ... * (n-k+1)
    assert n >= 0 and k >= 0
    if k > n:
        return 0
    ret = 1
    for i in range(n,n-k,-1):
        ret *= i
    return ret

def comb(n:int,k:int) -> int:
    ''' combinations nCk (binomial coefficients) '''
    # n * (n-1) * ... * (n-k+1) over 1 * 2 * ... * k
    assert n >= 0 and k >= 0
    if k > n:
        return 0
    ret = 1
    for i in range(0,min(k,n-k)):
        ret *= n-i
        ret //= i+1
    return ret

def fact(n:int) -> int:
    ''' factorial '''
    assert n >= 0
    if n <= 1:
        return 1
    ret = 1
    for i in range(2,n+1):
        ret *= i
    return ret

def isqrt(n:int) -> int:
    ''' integer square root '''
    # https://en.wikipedia.org/wiki/Integer_square_root
    #
    # newton's method x_{k+1} = (1/2) * (x_k+n/x_k)
    # if x_k >= sqrt(n) then x_{k+1} >= sqrt(x_k * n/x_k) = sqrt(n)
    # because arithmetic mean >= geometric mean
    #
    # with integer operations only
    # x_{k+1} = floor( (1/2) * (x_k + floor(n/x_k)) )
    #         = floor( (1/2) * (x_k + n/x_k) )
    # if x_k = isqrt(n) + m = floor(sqrt(n) + m) for some integer m > 0
    # we can show x_{k+1} <= isqrt(n) + floor(m/2)
    # which shows it must keep decreasing, reaching isqrt(n)
    # it also shows the number of iterations is bounded above by log2(m)
    #
    # upon reaching isqrt(n), another iteration will produce isqrt(n)+1
    # if n+1 is a perfect square, isqrt(n) otherwise (fixed point)
    assert n >= 0
    if n <= 1:
        return n
    x0 = n//2
    x1 = (x0+n//x0)//2
    while x1 < x0:
        x0 = x1
        x1 = (x0+n//x0)//2
    return x0

def icbrt(n:int) -> int:
    ''' integer cube root '''
    # binary method
    # find the largest p such that p^3 <= n
    # then for each following bit, select 1 if the resulting cube is <= n
    assert n >= 0
    if n <= 1:
        return n
    ret = 1
    while (ret<<1)**3 <= n:
        ret <<= 1
    bit = ret >> 1
    while bit:
        if (ret|bit)**3 <= n:
            ret |= bit
        bit >>= 1
    return ret

def iroot(r:int,n:int) -> int:
    ''' integer rth root of n '''
    # binary method similar to icbrt()
    assert r >= 1
    assert n >= 0
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
    return ret

def modpow(a:int,p:int,m:int) -> int:
    ''' a**p modulo m '''
    assert m > 0
    assert p >= 0
    if m == 1:
        return 0
    a %= m
    ret = 1
    while p:
        if p%2 == 1:
            ret = (ret*a)%m
        p >>= 1
        a = (a*a)%m
    return ret

def bezout(a:int,b:int) -> tuple[int,int,int]:
    ''' returns (s,t,g) where s*a+t*b = g = gcd(a,b), requires nonzero inputs '''
    assert a != 0 and b != 0
    # can be optimized to compute s or t from the other at the end
    r0,r1 = a,b
    s0,s1 = 1,0
    t0,t1 = 0,1
    while r1 != 0:
        q = r0//r1
        r0,r1 = r1,r0-q*r1
        s0,s1 = s1,s0-q*s1
        t0,t1 = t1,t0-q*t1
    # excluded but possibly useful: t1,s1 = a//g,b//g (where g is the gcd)
    return (s0,t0,r0) if r0 >= 0 else (-s0,-t0,-r0)

def modinv(n:int,m:int) -> int:
    ''' returns n^-1 mod m (requires gcd(n,m)=1) '''
    assert m > 1
    assert n % m != 0, '0 has no inverse'
    s,t,g = bezout(n,m) # s*n + t*m = 1
    assert g == 1, 'not invertible'
    return s%m

def is_prp(n:int,b:int) -> bool:
    ''' probable prime test n with base b, applies when n > 3 and 1 < b < n-1 '''
    if n < 2:
        return False
    if n < 4: # 2,3
        return True
    assert 1 < b < n-1, 'base out of range'
    return modpow(b,n-1,n) == 1

def is_sprp(n:int,b:int) -> bool:
    ''' strong pseudoprime test n with base b '''
    if n < 2:
        return False
    if n < 4: # 2,3
        return True
    assert 1 < b < n-1, 'base out of range'
    # n = d * 2^s + 1
    d = n-1
    s = 0
    while d % 2 == 0:
        d //= 2
        s += 1
    if s == 0: # n is even
        return False
    # b^d = 1 or b^(d * 2^r) = -1 (0 <= r < s)
    v = modpow(b,d,n)
    if v == 1 or v == n-1: # r=0
        return True
    for _ in range(s-1): # r=1,r=2,..,r=s-1
        v = (v*v)%n
        if v == n-1:
            return True
    return False

def miller_rabin(n:int,t:int) -> bool:
    ''' perform t miller rabin tests on n (applies for odd n > 4) '''
    assert t > 0
    if n < 2:
        return False
    if n < 4: # 2,3
        return True
    if n % 2 == 0:
        return False
    # choose bases 1 < b < n-1
    return all(is_sprp(n,random.randint(2,n-2)) for _ in range(t))

def factorization(n:int) -> list[int]:
    ''' computes prime factorization with trial division
    (increasing order with correct multiplicity) '''
    assert n > 0
    ret: list[int] = []
    while n % 2 == 0:
        ret.append(2)
        n //= 2
    d = 3
    while d*d <= n: # odd factors up to floor(sqrt(n))
        while n % d == 0:
            ret.append(d)
            n //= d
        d += 2
    if n != 1:
        ret.append(n)
    return ret

def list_factors(n:int) -> list[int]:
    return _list_factors2(n)

def _list_factors1(n:int) -> list[int]:
    ''' lists factors by looping up to floor(sqrt(n)) '''
    assert n > 0
    lo: list[int] = []
    hi: list[int] = []
    m = isqrt(n)
    for d in range(1,m+1):
        if n % d == 0:
            lo.append(d)
            hi.append(n//d)
    if lo[-1] == hi[-1]:
        hi.pop()
    return lo + hi[::-1]

def _list_factors2_recur(ret:list[int],factors:list[int],mults:list[int],i:int,p:int):
    # i = index, p = product
    if i == len(factors):
        ret.append(p)
    else:
        _list_factors2_recur(ret,factors,mults,i+1,p)
        for _ in range(mults[i]):
            p *= factors[i]
            _list_factors2_recur(ret,factors,mults,i+1,p)

def _list_factors2(n:int) -> list[int]:
    ''' lists factors by using prime factorization, returns sorted list '''
    assert n > 0
    factor_list = factorization(n)
    # make multiplicity map
    factors: list[int] = []
    mults: list[int] = []
    prev_factor = 0
    for f in factor_list:
        if f == prev_factor:
            mults[-1] += 1
        else:
            factors.append(f)
            mults.append(1)
            prev_factor = f
    ret: list[int] = []
    _list_factors2_recur(ret,factors,mults,0,1)
    return sorted(ret)

def totient(n:int) -> int:
    ''' euler totient function by using trial division to factor '''
    assert n > 0
    ret = n
    if n % 2 == 0:
        ret //= 2
        n //= 2
        while n % 2 == 0:
            n //= 2
    d = 3
    while d*d <= n: # odd factors up to floor(sqrt(n))
        if n % d == 0:
            ret = (ret//d)*(d-1)
            n //= d
            while n % d == 0:
                n //= d
        d += 2
    if n != 1:
        ret = (ret//n)*(n-1)
    return ret

def list_primes(n:int) -> list[int]:
    ''' returns a list of primes below n '''
    if n < 2:
        return []
    sieve: list[bool] = [True]*(n//2) # odd sieve, index i -> 2*i+1
    i = 1
    while True:
        v = 2*i+1
        # if 2*i+1 is prime, cross out multiples
        j0 = v*v//2
        if j0 >= len(sieve): # would start crossing out beyond end of sieve
            break
        if sieve[i]: # if 2*i+1 is prime, cross out multiples
            # odd multiples starting at (2i+1)^2
            for j in range(j0,len(sieve),v):
                sieve[j] = False
        i += 1
    ret: list[int] = [2]
    for i in range(1,len(sieve)):
        if sieve[i]:
            ret.append(2*i+1)
    return ret

### tests

if __name__ == '__main__':

    def raises(func,*args) -> bool:
        ''' returns true if func(*args) raises an exception '''
        try:
            func(*args)
            return False
        except:
            return True

    # gcd
    assert raises(gcd,0,0)
    assert gcd(0,5) == 5
    assert gcd(5,0) == 5
    assert gcd(1,2) == 1
    assert gcd(3,1) == 1
    assert gcd(9,72) == 9
    assert gcd(48,32) == 16
    assert gcd(-27,36) == 9
    assert gcd(-14,-18) == 2
    assert gcd(-91,126) == 7
    assert gcd(85,-51) == 17
    assert gcd(13,13) == 13

    # lcm
    assert raises(lcm,0,0)
    assert lcm(5,0) == 0
    assert lcm(6,1) == 6
    assert lcm(-7,-3) == 21
    assert lcm(24,48) == 48
    assert lcm(-34,-85) == 170
    assert lcm(140,-35) == 140
    assert lcm(14,14) == 14
    assert lcm(72,100) == 1800

    # perm
    assert raises(perm,0,-1)
    assert raises(perm,-1,0)
    assert raises(perm,-1,-1)
    assert perm(0,0) == 1
    assert perm(0,1) == 0
    assert perm(1,0) == 1
    assert perm(1,1) == 1
    assert perm(2,0) == 1
    assert perm(2,1) == 2
    assert perm(2,2) == 2
    assert [perm(3,i) for i in range(3+1)] == [1,3,6,6]
    assert [perm(4,i) for i in range(4+1)] == [1,4,12,24,24]
    assert [perm(5,i) for i in range(5+1)] == [1,5,20,60,120,120]
    assert [perm(6,i) for i in range(6+1)] == [1,6,30,120,360,720,720]
    assert [perm(7,i) for i in range(7+1)] == [1,7,42,210,840,2520,5040,5040]

    # comb
    assert raises(comb,0,-1)
    assert raises(comb,-1,0)
    assert raises(comb,-1,-1)
    assert comb(0,0) == 1
    assert comb(0,1) == 0
    assert comb(1,0) == 1
    assert comb(1,1) == 1
    assert comb(2,0) == 1
    assert comb(2,1) == 2
    assert comb(2,2) == 1
    assert [comb(3,i) for i in range(3+1)] == [1,3,3,1]
    assert [comb(4,i) for i in range(4+1)] == [1,4,6,4,1]
    assert [comb(5,i) for i in range(5+1)] == [1,5,10,10,5,1]
    assert [comb(6,i) for i in range(6+1)] == [1,6,15,20,15,6,1]
    assert [comb(7,i) for i in range(7+1)] == [1,7,21,35,35,21,7,1]

    # fact
    assert raises(fact,-1)
    assert fact(0) == 1
    assert fact(1) == 1
    assert fact(2) == 2
    assert fact(3) == 6
    assert fact(4) == 24
    assert fact(5) == 120
    assert fact(6) == 720
    assert fact(7) == 5040
    assert fact(8) == 40320
    assert fact(9) == 362880

    # isqrt
    assert raises(isqrt,-1)
    assert isqrt(0) == 0
    assert isqrt(1) == 1
    assert isqrt(2) == 1
    assert isqrt(3) == 1
    assert all(isqrt(n) == 2 for n in range(4,9))
    assert all(isqrt(n) == 3 for n in range(9,16))
    assert all(isqrt(n) == 4 for n in range(16,25))
    assert all(all(isqrt(n) == r for n in range(r*r,(r+1)*(r+1))) for r in range(5,100))

    # icbrt
    assert raises(icbrt,-1)
    assert icbrt(0) == 0
    assert all(icbrt(n) == 1 for n in range(1,8))
    assert all(icbrt(n) == 2 for n in range(8,27))
    assert all(icbrt(n) == 3 for n in range(27,64))
    assert all(all(icbrt(n) == r for n in range(r**3,(r+1)**3)) for r in range(4,20))

    # iroot
    assert raises(iroot,0,0)
    assert raises(iroot,-1,0)
    assert raises(iroot,1,-1)
    assert all(iroot(1,n) == n for n in range(100))
    assert all(iroot(2,n) == isqrt(n) for n in range(100))
    assert all(iroot(3,n) == icbrt(n) for n in range(100))

    # modpow
    assert raises(modpow,10,100,0)
    assert raises(modpow,10,100,-1)
    assert raises(modpow,10,-1,13)
    assert modpow(0,140,12) == 0
    assert all(modpow(2,p-1,p) == 1 for p in [3,5,7,11,13,17,19,23,29])
    assert all(modpow(3,p-1,p) == 1 for p in [2,5,7,11,13,17,19,23,29])
    assert modpow(7,66,21) == 7
    assert modpow(56,56467,467) == 265
    assert modpow(10,100,23) == 13
    assert modpow(9,0,89) == 1
    assert modpow(9,1,89) == 9
    assert modpow(9,2,89) == 81
    assert modpow(9,3,89) == 17

    # bezout
    assert raises(bezout,0,0)
    assert raises(bezout,5,0)
    assert raises(bezout,0,5)
    assert bezout(2,3) == (-1,1,1)
    assert bezout(3,2) == (1,-1,1)
    assert bezout(-2,3) == (1,1,1)
    assert bezout(2,-3) == (-1,-1,1)
    assert bezout(-2,-3) == (1,-1,1)
    assert bezout(2,6) == (1,0,2)
    assert bezout(8,2) == (0,1,2)
    assert bezout(5,7) == (3,-2,1)
    assert bezout(12,5) == (-2,5,1)
    assert bezout(24,16) == (1,-1,8)
    assert bezout(45,60) == (-1,1,15)
    assert bezout(160,90) == (4,-7,10)
    assert bezout(2352,1035) == (-11,25,3)

    # modinv
    assert raises(modinv,0,0)
    assert raises(modinv,0,2)
    assert raises(modinv,5,0)
    assert raises(modinv,0,1)
    assert raises(modinv,0,3)
    assert raises(modinv,1,1)
    assert raises(modinv,0,16)
    assert raises(modinv,0,17)
    assert modinv(1,2) == 1
    assert modinv(1,3) == 1
    assert modinv(2,3) == 2
    assert modinv(4,3) == 1
    assert modinv(5,3) == 2
    assert modinv(-2,3) == 1
    assert modinv(-1,3) == 2
    assert [modinv(i,7) for i in range(1,7)] == [1,4,5,2,3,6]
    assert raises(modinv,0,7)
    assert [modinv(i,10) for i in [1,3,7,9]] == [1,7,3,9]
    assert all(raises(modinv,i,10) for i in [0,2,4,5,6,8])

    # is_prp
    assert not any(is_prp(i,2) for i in range(-2,2))
    assert is_prp(2,2) and is_prp(3,2)
    assert all(is_prp(n,2) for n in [3,5,7,11,13,17,19,23,29,31,37,41,43,47,53,59,61,67,71,73,79,83,89,97])
    assert all(is_prp(n,3) for n in [3,5,7,11,13,17,19,23,29,31,37,41,43,47,53,59,61,67,71,73,79,83,89,97])
    assert is_prp(341,2) # 341 = 11*31
    assert is_prp(2047,2) # 2047 = 23*89
    assert all(is_prp(561,b) for b in range(2,560) if gcd(b,561) == 1) # carmichael
    assert raises(is_prp,7,0)
    assert raises(is_prp,7,1)
    assert raises(is_prp,7,6)
    assert raises(is_prp,7,7)

    # is_sprp
    assert not any(is_sprp(i,2) for i in range(-2,2))
    assert is_sprp(2,2) and is_sprp(3,2)
    assert all(is_sprp(n,2) for n in [3,5,7,11,13,17,19,23,29,31,37,41,43,47,53,59,61,67,71,73,79,83,89,97])
    assert all(is_sprp(n,3) for n in [3,5,7,11,13,17,19,23,29,31,37,41,43,47,53,59,61,67,71,73,79,83,89,97])
    assert not is_sprp(341,2)
    assert is_sprp(2047,2) # 2047 = 23*89
    assert not is_sprp(561,2)
    assert not is_sprp(561,3)
    assert raises(is_sprp,7,0)
    assert raises(is_sprp,7,1)
    assert raises(is_sprp,7,6)
    assert raises(is_sprp,7,7)

    # miller_rabin
    # in theory there is a very small chance these may fail
    # for testing it should be alright to assume miller_rabin correctly determines primality
    assert all(miller_rabin(n,5) for n in [3331,9343,1447,6271,7193,6299,7331,1663,5387,5413])
    assert not any(miller_rabin(n,5) for n in [3862,5537,5320,4383,3434,5532,9409,9798,2850,6548])

    # factorization
    assert raises(factorization,-1)
    assert raises(factorization,0)
    assert factorization(1) == []
    assert all(factorization(p) == [p] for p in [2,3,5,7,23,41,59,73,97])
    assert all(factorization(2**i) == [2]*i for i in range(10))
    assert all(factorization(3**i) == [3]*i for i in range(10))
    assert all(factorization(2**i*3**j) == [2]*i+[3]*j for i in range(10) for j in range(10))
    assert factorization(15) == [3,5]
    assert factorization(72) == [2,2,2,3,3]
    assert factorization(1260) == [2,2,3,3,5,7]
    assert factorization(6) == [2,3]
    assert factorization(30) == [2,3,5]
    assert factorization(210) == [2,3,5,7]
    assert factorization(13435741) == [11,31,31,31,41]
    assert factorization(76998691) == [7,11,999983]
    assert factorization(1000000000001) == [73,137,99990001]
    assert factorization(6335291110119413) == [13,13,61,71,89,89,103,103,103]
    assert factorization(66049) == [257,257]
    assert factorization(141420761) == [521,521,521]
    assert factorization(1000003) == [1000003]
    assert factorization(1000000007) == [1000000007]
    assert factorization(1000000000039) == [1000000000039]

    # list_factors
    assert raises(list_factors,-1)
    assert raises(list_factors,0)
    assert list_factors(1) == [1]
    assert all(list_factors(p) == [1,p] for p in [2,3,5,7,11,13,17,19,47,79,97])
    assert list_factors(9) == [1,3,9]
    assert list_factors(27) == [1,3,9,27]
    assert list_factors(12) == [1,2,3,4,6,12]
    assert list_factors(15) == [1,3,5,15]
    assert list_factors(120) == [1,2,3,4,5,6,8,10,12,15,20,24,30,40,60,120]
    assert list_factors(36) == [1,2,3,4,6,9,12,18,36]
    assert list_factors(10201) == [1,101,10201]
    assert list_factors(1000000000001) == [1,73,137,10001,99990001,7299270073,13698630137,1000000000001]

    # totient
    assert raises(totient,-1)
    assert raises(totient,0)
    assert totient(1) == 1
    assert all(totient(p) == p-1 for p in [2,3,5,7,11,19,29,59,79])
    assert totient(6) == 2
    assert totient(15) == 8
    assert totient(49) == 42
    assert totient(64) == 32
    assert totient(72) == 24
    assert totient(100) == 40
    assert totient(25769263) == 21209472
    assert totient(1000000000001) == 979102080000

    # list_primes
    assert list_primes(-1) == []
    assert list_primes(0) == []
    assert list_primes(1) == []
    assert list_primes(2) == [2]
    assert list_primes(10) == [2,3,5,7]
    assert list_primes(11) == [2,3,5,7]
    assert list_primes(12) == [2,3,5,7,11]
    assert list_primes(100) == [2,3,5,7,11,13,17,19,23,29,31,37,41,43,47,53,59,61,67,71,73,79,83,89,97]
    assert list_primes(101) == [2,3,5,7,11,13,17,19,23,29,31,37,41,43,47,53,59,61,67,71,73,79,83,89,97]
    assert list_primes(102) == [2,3,5,7,11,13,17,19,23,29,31,37,41,43,47,53,59,61,67,71,73,79,83,89,97,101]
    assert len(list_primes(1000)) == 168
    assert sum(list_primes(1000)) == 76127
    assert len(list_primes(10000)) == 1229
    assert sum(list_primes(10000)) == 5736396
