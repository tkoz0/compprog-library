# helper test file for best fraction approximations with limited denominator

import math

#N,D = 3141592653589793,1000000000000000
N,D = 1,1000000
print(f'input fraction {N}/{D} with gcd {math.gcd(N,D)}')

limit = 1000

if N % D > D // 2:
    best_frac = (N//D+1,1)
    best_diff = (D-N%D,D)
else:
    best_frac = (N//D,1)
    best_diff = (N%D,D)

def frac_less(a,b,c,d):
    # a/b < c/d iff a*d < b*c
    return a*d < b*c

def frac_diff(a,b,c,d):
    # | a/b - c/d | = | a*d - b*c | / ( b*d )
    e,f = abs(a*d-b*c),b*d
    g = math.gcd(e,f)
    return (e//g,f//g)

for d in range(2,limit+1):
    # n/d ~= N/D
    # nD ~= Nd
    n,rem = divmod(N*d,D)
    if rem > D//2:
        n += 1
    diff = frac_diff(n,d,N,D)
    if frac_less(*diff,*best_diff):
        best_frac = (n,d)
        best_diff = diff
        print(f'found {best_frac} with difference {best_diff}')

print(f'result is {best_frac} with difference {best_diff}')
