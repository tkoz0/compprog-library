
from typing import Callable, Iterable, Sequence, Generator, TypeVar, Any

from supports_compare import SupportsCmpEq, SupportsCmpLt
from supports_op_self import SupportsSelfAdd, SupportsSelfMul

T_any = TypeVar('T_any')
U_any = TypeVar('U_any')
T_comp = TypeVar('T_comp',bound=SupportsCmpEq)
T_ord = TypeVar('T_ord',bound=SupportsCmpLt)
T_add = TypeVar('T_add',bound=SupportsSelfAdd)
T_mul = TypeVar('T_mul',bound=SupportsSelfMul)

def map_(func:Callable[[T_any],U_any],items:Iterable[T_any],/) \
        -> Generator[U_any,None,None]:
    '''
    (named map_ to avoid conflict with builtin map)
    apply func to every item in items
    [item1,item2,...] -> [func(item1),func(item2),...]
    '''
    for item in items:
        yield func(item)

def foldl0(func:Callable[[T_any,T_any],T_any],
           init:T_any,items:Iterable[T_any],/) -> T_any:
    '''
    left associative fold/reduce, requiring initialization element
    [item1,item2,...,itemn]
    -> func(...func(func(init,item1),item2)...,itemn)
    '''
    ret = init
    for item in items:
        ret = func(ret,item)
    return ret

def foldl1(func:Callable[[T_any,T_any],T_any],items:Iterable[T_any],/) -> T_any:
    '''
    left associative fold/reduce, requiring at least 1 element
    [item1,item2,item3,...,itemn]
    -> func(...func(func(item1,item2),item3)...,itemn)
    '''
    items_iter = iter(items)
    ret = next(items_iter)
    for item in items_iter:
        ret = func(ret,item)
    return ret

def foldr0(func:Callable[[T_any,T_any],T_any],
           init:T_any,items:Sequence[T_any],/) -> T_any:
    '''
    right associative fold/reduce, requiring initialization element
    [item1,item2,...,itemn]
    -> func(item1,func(item2,...func(itemn,init)...))
    '''
    ret = init
    for item in reversed(items):
        ret = func(item,ret)
    return ret

def foldr1(func:Callable[[T_any,T_any],T_any],items:Sequence[T_any],/) -> T_any:
    '''
    right associative fold/reduce, requiring at least 1 element
    [item1,item2,...,itemm,itemn]
    -> func(item1,func(item2,...func(itemm,itemn)...))
    '''
    items_iter = reversed(items)
    ret = next(items_iter)
    for item in items_iter:
        ret = func(item,ret)
    return ret

def filter_(cond:Callable[[T_any],bool],items:Iterable[T_any],/) \
        -> Generator[T_any,None,None]:
    '''
    (named filter_ to avoid conflict with builtin filter)
    select items matching a required condition
    '''
    for item in items:
        if cond(item):
            yield item

def foreach(func:Callable[[T_any],Any],items:Iterable[T_any],/):
    '''
    call a function for each item in order
    '''
    for item in items:
        func(item)

def any0(items:Iterable[bool],/) -> bool:
    '''
    check if any of the bools is true, stops once a true is found
    '''
    for item in items:
        if item:
            return True
    return False

def all0(items:Iterable[bool],/) -> bool:
    '''
    check if all of the bools are true, stops once a false is found
    '''
    for item in items:
        if not item:
            return False
    return True

def any1(cond:Callable[[T_any],bool],items:Iterable[T_any],/) -> bool:
    '''
    check if any item satisfies the condition
    '''
    return any0(map_(cond,items))

def all1(cond:Callable[[T_any],bool],items:Iterable[T_any],/) -> bool:
    '''
    check if all items satisfy the condition
    '''
    return all0(map_(cond,items))

def min0(items:Iterable[T_ord],init:T_ord,/) -> T_ord:
    '''
    returns minimum element
    first one if there are multiple
    initialized with init
    '''
    f = lambda a,b: (a if a < b else b)
    return foldl0(f,init,items)

def max0(items:Iterable[T_ord],init:T_ord,/) -> T_ord:
    '''
    returns maximum element
    first one if there are multiple
    initialized with init
    '''
    f = lambda a,b: (b if a < b else a)
    return foldl0(f,init,items)

def min1(items:Iterable[T_ord],/) -> T_ord:
    '''
    return minumum of elements
    first one if there are multiple
    requires at least 1 element
    '''
    f = lambda a,b: (a if a < b else b)
    return foldl1(f,items)

def max1(items:Iterable[T_ord],/) -> T_ord:
    '''
    return maximum of elements
    first one if there are multiple
    requires at least 1 element
    '''
    f = lambda a,b: (b if a < b else a)
    return foldl1(f,items)

def sum0(items:Iterable[T_add],init:T_add,/) -> T_add:
    '''
    returns sum of elements (left associative)
    initialized with init
    '''
    f = lambda a,b: a + b
    return foldl0(f,init,items)

def prod0(items:Iterable[T_mul],init:T_mul,/) -> T_mul:
    '''
    returns product of elements (left associative)
    initialized with init
    '''
    f = lambda a,b: a * b
    return foldl0(f,init,items)

def sum1(items:Iterable[T_add],/) -> T_add:
    '''
    returns sum of elements (left associative)
    requires at least 1 element
    '''
    f = lambda a,b: a + b
    return foldl1(f,items)

def prod1(items:Iterable[T_mul],/) -> T_mul:
    '''
    returns product of elements (left associative)
    requires at least 1 element
    '''
    f = lambda a,b: a * b
    return foldl1(f,items)

def head(items:Iterable[T_any],/) -> T_any:
    '''
    returns first element of an iterable
    requires at least 1 element
    '''
    return next(iter(items))

def tail(items:Iterable[T_any],/) -> Iterable[T_any]:
    '''
    returns all elements after first in an iterable
    requires at least 1 element
    '''
    items_iter = iter(items)
    next(items_iter)
    return items_iter

def last(items:Iterable[T_any],/) -> T_any:
    '''
    returns last element of an iterable
    requires at least 1 element
    '''
    items_iter = iter(items)
    ret = next(items_iter)
    for item in items_iter:
        ret = item
    return ret

def contains(item:T_comp,items:Iterable[T_comp],/) -> bool:
    '''
    returns true if an item exists in the iterable
    '''
    f = lambda a : a == item
    return any1(f,items)

def zip_(*iterables:Iterable[T_any]) -> Generator[tuple[T_any,...],None,None]:
    '''
    (named zip_ to avoid conflict with builtin zip)
    combines corresponding elements into tuples
    stops with the shortest of the provided iterables
    ([a1,a2,...],[b1,b2,...],...) -> [(a1,b1,...),(a2,b2,...),...]
    '''
    item_iters = [iter(iterable) for iterable in iterables]
    if len(item_iters) == 0:
        return
    while True:
        try:
            yield tuple(next(item_iter) for item_iter in item_iters)
        except:
            break

def zipwith(func:Callable[...,U_any],*iterables:Iterable[T_any]) \
        -> Generator[U_any,None,None]:
    '''
    calls function with corresponding elements
    stops with the shortest of the provided iterables
    ([a1,a2,...],[b1,b2,...],...) -> [func(a1,b1,...),func(a2,b2,...),...]
    '''
    item_iters = [iter(iterable) for iterable in iterables]
    if len(item_iters) == 0:
        return
    while True:
        try:
            yield func(*(next(item_iter) for item_iter in item_iters))
        except:
            break

def headtail(head:T_any,tail:Iterable[T_any],/) -> Generator[T_any,None,None]:
    '''
    combine head and tail into an iterable
    '''
    yield head
    yield from tail

def unzipi(i:int,items:Sequence[tuple],/) -> Generator:
    '''
    extract sequence of ith elements from each tuple
    '''
    for item in items:
        yield item[i]

def unzip(items:Sequence[tuple],/) -> tuple[Generator,...]:
    '''
    splits the tuples into separate corresponding sequences
    requires at least 1 item
    '''
    item = next(iter(items))
    l = len(item)
    return tuple(unzipi(i,items) for i in range(l))

def take(n:int,items:Iterable[T_any],/) -> Generator[T_any,None,None]:
    '''
    yield up to the first n items
    '''
    item_iter = iter(items)
    for _ in range(n):
        try:
            yield next(item_iter)
        except StopIteration:
            break

def drop(n:int,items:Iterable[T_any],/) -> Generator[T_any,None,None]:
    '''
    yield everything after the first n items
    '''
    item_iter = iter(items)
    for _ in range(n):
        try:
            next(item_iter)
        except StopIteration:
            break
    yield from item_iter

def takewhile(cond:Callable[[T_any],bool],items:Iterable[T_any],/) \
        -> Generator[T_any,None,None]:
    '''
    yield items until finding one that does not satisfy condition
    '''
    item_iter = iter(items)
    while True:
        try:
            item = next(item_iter)
            if cond(item):
                yield item
            else:
                break
        except StopIteration:
            break

def dropwhile(cond:Callable[[T_any],bool],items:Iterable[T_any],/) \
        -> Generator[T_any,None,None]:
    '''
    yield items starting with the first that does not satisfy condition
    '''
    item_iter = iter(items)
    while True:
        try:
            item = next(item_iter)
            if not cond(item):
                yield item
                break
        except StopIteration:
            break
    yield from item_iter

def concat(*iterables:Iterable[T_any]) -> Generator[T_any,None,None]:
    '''
    concatenate multiple iterators into a single one
    '''
    for iterable in iterables:
        yield from iterable

def repeat(item:T_any,/) -> Generator[T_any,None,None]:
    '''
    repeat a single item infinitely
    '''
    while True:
        yield item

def cycle(items:Sequence[T_any],/) -> Generator[T_any,None,None]:
    '''
    repeat an item sequence infinitely
    '''
    while True:
        yield from items

def countif(cond:Callable[[T_any],bool],items:Iterable[T_any],/) -> int:
    '''
    return howm any items satisfy condition
    '''
    f = lambda item: (1 if cond(item) else 0)
    return sum0(map_(f,items),0)

def sumif0(cond:Callable[[T_add],bool],items:Iterable[T_add],init:T_add,/) \
        -> T_add:
    '''
    sum items satisfying condition
    initialized with init
    '''
    return sum0(filter_(cond,items),init)

def sumif1(cond:Callable[[T_add],bool],items:Iterable[T_add],/) -> T_add:
    '''
    sum items satisfying condition
    at least 1 must satisfy the condition
    '''
    return sum1(filter_(cond,items))

def prodif0(cond:Callable[[T_mul],bool],items:Iterable[T_mul],init:T_mul,/) \
        -> T_mul:
    '''
    multiply items satisfying condition
    initialized with init
    '''
    return prod0(filter_(cond,items),init)

def prodif1(cond:Callable[[T_mul],bool],items:Iterable[T_mul],/) ->T_mul:
    '''
    multiply items satisfying condition
    at least 1 must satisfy the condition
    '''
    return prod1(filter_(cond,items))

def iterate(func:Callable[[T_any],T_any],init:T_any,/) -> Generator[T_any,None,None]:
    '''
    apply a function repeatedly to a starting value
    '''
    yield init
    while True:
        init = func(init)
        yield init

def until(cond:Callable[[T_any],bool],func:Callable[[T_any],T_any],
          init:T_any,/) -> T_any:
    '''
    apply a function to starting value and stop when condition is true
    '''
    while not cond(init):
        init = func(init)
    return init

if __name__ == '__main__':

    def raises(func:Callable[...,Any],*args,**kwargs) -> bool:
        '''
        check that calling the function with the given args raises an exception
        '''
        try:
            func(*args,**kwargs)
            return False
        except:
            return True

    def assert_se(items1:Iterable[T_any],items2:Iterable[T_any],
                  lim:None|int=None):
        '''
        check that 2 iterables are equal by items they contain
        optional limit which is useful for infinite iterables
        '''
        iter1 = iter(items1)
        iter2 = iter(items2)
        i = -1
        for i,item1 in enumerate(iter1):
            if isinstance(lim,int) and i >= lim:
                break
            try:
                item2 = next(iter2)
            except StopIteration:
                assert 0, f'len(items1) > len(items2) == {i}'
            assert item1 == item2, f'items1[{i}] != items2[{i}] ' \
                                   f'({repr(item1)} != {repr(item2)})'
        if lim is None:
            try:
                item2 = next(iter2)
                assert 0, f'len(items2) > len(items1) == {i+1}'
            except StopIteration:
                pass

    sq = lambda x : x*x
    cb = lambda x : x*x*x
    inc = lambda x : x+1
    dec = lambda x : x-1
    double = lambda x : 2*x
    triple = lambda x : 3*x

    even = lambda x : x%2 == 0
    odd = lambda x : x%2 == 1

    add = lambda a,b: a+b
    sub = lambda a,b: a-b
    mul = lambda a,b: a*b
    tdiv = lambda a,b: a/b
    fdiv = lambda a,b: a//b

    def above(x):
        return lambda y : y > x
    def below(x):
        return lambda y : y < x
    def between(x,y):
        return lambda z : x < z and z < y
    def eqto(x):
        return lambda y : x == y

    f_true = lambda _ : True
    f_false = lambda _ : False

    # assert_se
    assert_se((),())
    assert_se((1,2,3,4),(1,2,3,4))
    assert_se((1,2,3,4,5),(1,2,3,4,5,6),3)
    assert_se((5,10,15,20),(6,12,18,24),0)

    # map_
    assert_se(map_(sq,range(10)),(0,1,4,9,16,25,36,49,64,81))
    assert_se(map_(double,range(0)),())
    assert_se(map_(double,map_(triple,range(1,4))),(6,12,18))
    assert_se(map_(even,range(5)),(True,False,True,False,True))
    assert_se(map_(dec,range(1,101)),range(100))

    # foldl0
    assert foldl0(add,0,()) == 0
    assert foldl0(add,5,()) == 5
    assert foldl0(mul,4,(2,)) == 8
    assert foldl0(sub,3,(5,)) == -2
    assert foldl0(add,-3,(1,2,3)) == 3
    assert foldl0(sub,0,(1,2,3)) == -6
    assert foldl0(mul,0,(1,2,3,4)) == 0
    assert foldl0(mul,1,(1,2,3,4)) == 24

    # foldr0
    assert foldr0(add,0,()) == 0
    assert foldr0(add,5,()) == 5
    assert foldr0(mul,2,(4,)) == 8
    assert foldr0(sub,3,(5,)) == 2
    assert foldr0(add,-3,(1,2,3)) == 3
    assert foldr0(sub,0,(1,2,3)) == 2
    assert foldr0(sub,-6,(3,4,5)) == 10

    # foldl1
    assert raises(foldl1,add,())
    assert foldl1(add,(1,)) == 1
    assert foldl1(add,(10,20,30,40)) == 100
    assert foldl1(sub,(1,2,3)) == -4
    assert foldl1(mul,(2,3,5,7)) == 210
    assert foldl1(mul,(1,2,0,2,1)) == 0

    # foldr1
    assert raises(foldr1,add,())
    assert foldr1(add,(-1,)) == -1
    assert foldr1(add,(40,30,20,10)) == 100
    assert foldr1(sub,(1,2,3)) == 2
    assert foldr1(mul,(2,3,5,7)) == 210
    assert foldr1(mul,(7,8,9,0,9,8,7)) == 0

    # filter_
    assert_se(filter_(even,range(12)),(0,2,4,6,8,10))
    assert_se(filter_(odd,range(12)),(1,3,5,7,9,11))
    assert_se(filter_(lambda x : x > 7, range(5)),())
    assert_se(filter_(lambda x : x < 7, range(5)),range(5))
    assert_se(filter_(lambda x : x == 5, range(10)),[5])
    assert_se(filter_(lambda x : x != 5, range(10)),[0,1,2,3,4,6,7,8,9])

    # foreach
    l1 = []
    foreach(l1.append,(11,22,33))
    assert l1 == [11,22,33]
    foreach(l1.pop,(0,0,0))
    assert l1 == []
    def l1_ins(n:int):
        for i in range(n):
            l1.append(i)
    foreach(l1_ins,(0,0,1,5,3))
    assert l1 == [0,0,1,2,3,4,0,1,2]
    s1 = 'words'
    def s1_append(s:str):
        global s1
        s1 += ' ' + s
    foreach(s1_append,('apple','banana'))
    assert s1 == 'words apple banana'

    # any0
    assert not any0(())
    assert any0((True,True))
    assert any0((True,False,False,False,False))
    assert any0((False,False,False,False,True,False,False))
    assert not any0((False,False,False))

    # all0
    assert all0(())
    assert all0((True,True,True))
    assert not all0((True,False,True))
    assert not all0((True,True,False,True,True,True))
    assert all0((True,True,True,True))

    # any1
    assert any1(even,range(5))
    assert not any1(even,range(1,10,2))

    # all1
    assert not all1(odd,range(5))
    assert all1(odd,range(1,10,2))

    #min0
    assert min0((),0) == 0
    assert min0((1,),2) == 1
    assert min0((1,2,3),-1) == -1
    assert min0((5,8,-1,3,0,-9,6,7),0) == -9

    #max0
    assert max0((),0) == 0
    assert max0((3,),5) == 5
    assert max0((5,8,-1),3) == 8
    assert max0((5,9,12,-1,3,-7,14,6,-1,2,-3),0) == 14

    #min1
    assert raises(min1,())
    assert min1((-1,)) == -1
    assert min1((5,-2,3,-4,6)) == -4

    #max1
    assert raises(max1,())
    assert max1((-2,)) == -2
    assert max1((6,-7,-12,8,10,-1)) == 10

    #sum0
    assert sum0((),5) == 5
    assert sum0((1,2,3),5) == 11
    assert sum0(range(10),0) == 45

    #prod0
    assert prod0((),10) == 10
    assert prod0((1,2,3),-6) == -36
    assert prod0(range(1,10),2) == 725760

    #sum1
    assert raises(sum1,())
    assert sum1((5,)) == 5
    assert sum1((7,-3,-1)) == 3
    assert sum1((6,-3,-3,5,10,-2)) == 13

    #prod1
    assert raises(prod1,())
    assert prod1((7,)) == 7
    assert prod1((5,8,3)) == 120
    assert prod1((2,-3,-4,8,-5)) == -960

    #head
    assert raises(head,())
    assert head((1,2,3)) == 1
    assert head('string') == 's'

    #tail
    assert raises(tail,())
    assert_se(tail((1,)),())
    assert_se(tail(range(2,6)),(3,4,5))

    #last
    assert raises(last,())
    assert last('string') == 'g'
    assert last(range(10)) == 9

    #contains
    assert not contains('e','abcd')
    assert contains('e','abcdef')
    assert not contains(20,range(0,100,3))
    assert contains(30,range(0,100,3))

    #zip_
    assert_se(zip_(),())
    assert_se(zip_(range(100),()),())
    assert_se(zip_('string'),(('s',),('t',),('r',),('i',),('n',),('g',)))
    assert_se(zip_('string',range(3)),(('s',0),('t',1),('r',2)))
    assert_se(zip_(range(3),range(1,5),range(2,7)),((0,1,2),(1,2,3),(2,3,4)))

    #zipwith
    assert_se(zipwith(mul,range(3),(),range(5)),())
    assert_se(zipwith(add,(range(6)),(-2,-4,-6,-8)),(-2,-3,-4,-5))
    assert_se(zipwith(mul,(2,4,6,8),(1,3,5,7)),(2,12,30,56))
    assert_se(zipwith(sub,(5,9,0),(6,3,4,0)),(-1,6,-4))

    #headtail
    assert_se(headtail(3,()),(3,))
    assert_se(headtail('s','tring'),'string')
    assert_se(headtail(9,(8,7,6,5)),(9,8,7,6,5))

    #unzip
    a,b = unzip(((0,'s'),(1,'t'),(2,'r')))
    assert_se(a,range(3))
    assert_se(b,'str')
    a,b,c = unzip(((-1,0,1),))
    assert_se(a,(-1,))
    assert_se(b,(0,))
    assert_se(c,(1,))
    assert unzip(((),(),())) == ()

    #take
    assert_se(take(5,range(100)),range(5))
    assert_se(take(0,()),())
    assert_se(take(6,range(3)),range(3))
    assert_se(take(10,range(10)),range(10))

    #drop
    assert_se(drop(6,range(30)),range(6,30))
    assert_se(drop(3,()),())
    assert_se(drop(16,range(12)),())
    assert_se(drop(0,range(5)),range(5))

    #takewhile
    assert_se(takewhile(even,range(10)),(0,))
    assert_se(takewhile(odd,range(10)),())
    assert_se(takewhile(between(2,7),(5,3,1,4,4)),(5,3))
    assert_se(takewhile(below(3),range(5)),range(3))

    #dropwhile
    assert_se(dropwhile(even,range(8)),range(1,8))
    assert_se(dropwhile(odd,range(8)),range(8))
    assert_se(dropwhile(below(5),range(10)),range(5,10))
    assert_se(dropwhile(above(4),range(5,10)),())

    #concat
    assert_se(concat(range(3),'abc'),(0,1,2,'a','b','c'))
    assert_se(concat((),range(5),()),range(5))
    assert_se(concat(range(5),range(5,10)),range(10))
    assert_se(concat(),())

    #repeat
    assert_se(repeat(5),(5,5,5,5,5),5)
    assert_se(repeat('z'),'zzz',3)
    assert_se(repeat(-1),(-1,),1)

    #cycle
    assert_se(cycle(range(5)),concat(range(5),range(5),range(5)),15)
    assert_se(cycle(range(10)),concat(range(10),range(10)),20)
    assert_se(cycle((0,)),(0,0,0),3)

    #countif
    assert countif(even,range(10)) == 5
    assert countif(odd,range(10)) == 5
    assert countif(between(3,7),range(0,10,2)) == 2
    assert countif(eqto(12),range(0,100,5)) == 0

    #sumif0
    assert sumif0(even,range(1,10),0) == 20
    assert sumif0(odd,range(3),-1) == 0
    assert sumif0(eqto(5),(-1,6,5,5,0,10,5,-2,-3),0) == 15

    #prodif0
    assert prodif0(even,range(1,10),1) == 384
    assert prodif0(below(5),range(10),1) == 0
    assert prodif0(above(7),range(10),3) == 216

    #sumif1
    assert raises(sumif1,even,range(1,10,2))
    assert sumif1(even,range(10)) == 20
    assert sumif1(f_true,(1,)) == 1

    #prodif1
    assert raises(prodif1,odd,range(0,10,2))
    assert prodif1(odd,range(10)) == 945
    assert prodif1(f_true,(7,)) == 7

    #iterate
    assert_se(iterate(inc,0),range(100),100)
    assert_se(iterate(sq,2),(2,4,16,256,65536),5)
    assert_se(iterate(triple,1),(1,3,9,27,81),5)

    #until
    assert until(even,inc,0) == 0
    assert until(even,inc,1) == 2
    assert until(above(100),double,1) == 128
    assert until(below(12),triple,3) == 3
