
from typing import Callable,Any

def cache_all(func:Callable) -> Callable:
    '''
    basic caching for all calls to the function
    only supports positional args
    all types must be hashable
    '''
    cache: dict[tuple,Any] = dict()

    # wrap func using the cache to access, or store if value is new
    def wrapped(*args):
        if args in cache:
            return cache[args]
        value = func(*args)
        cache[args] = value
        return value

    # cache clearing
    def cache_clear():
        nonlocal cache
        cache = dict()

    # get cache size
    def cache_size() -> int:
        return len(cache)

    wrapped.cache_clear = cache_clear
    wrapped.cache_size = cache_size
    return wrapped

def cache_lru(size:int):
    '''
    least recently used cache of given size
    only supports positional args
    all types must be hashable
    when full, value used longest ago is replaced
    when accessed, value found is set as most recently used
    recently used order is managed by a custom linked list
    requires size > 1 to avoid single node and empty linked list cases
    '''
    if size <= 1:
        raise ValueError('lru cache size must be > 1')

    # the annotator function
    def wrapper(func:Callable) -> Callable:
        # key -> (value,listindex)
        cache: dict[tuple,tuple[Any,int]] = dict()
        # list nodes are (key,prev,next) using indexes
        clist: list[tuple[tuple,int|None,int|None]] = []
        csize = head = tail = 0

        def wrapped(*args):
            nonlocal csize,head,tail
            if args in cache:
                # move to front and return
                value,index = cache[args]
                if csize == 1:
                    return value

                if index == tail:
                    # move tail 1 node back
                    targs,tprev,_ = clist[tail]
                    assert isinstance(tprev,int)
                    tail = tprev
                    # fix next pointer on new tail
                    targs,tprev,_ = clist[tail]
                    clist[tail] = (targs,tprev,None)
                    # set prev pointer on old head
                    hargs,_,hnext = clist[head]
                    clist[head] = (hargs,index,hnext)
                    # move head to selected node
                    clist[index] = (args,None,head)
                    head = index

                elif index != head:
                    # make pointers for neighbor nodes skip selected node
                    _,iprev,inext = clist[index]
                    assert isinstance(iprev,int)
                    assert isinstance(inext,int)
                    pargs,pprev,_ = clist[iprev]
                    nargs,_,nnext = clist[inext]
                    clist[iprev] = (pargs,pprev,inext)
                    clist[inext] = (nargs,iprev,nnext)
                    # set prev pointer on old head
                    hargs,_,hnext = clist[head]
                    clist[head] = (hargs,index,hnext)
                    # move head to selected node
                    clist[index] = (args,None,head)
                    head = index

                # (if selected node is head, no rearranging needed)
                return value

            # need to compute value and insert
            value = func(*args)

            if csize == 0:
                # insert first cached value
                cache[args] = (value,0)
                clist.append((args,None,None))
                csize += 1

            elif csize < size:
                # insert after first
                cache[args] = (value,csize)
                clist.append((args,None,head))
                hargs,_,hnext = clist[head]
                clist[head] = (hargs,csize,hnext)
                head = csize
                csize += 1

            else:
                # remove tail then insert
                oldtail = tail
                targs,tprev,_ = clist[tail]
                assert isinstance(tprev,int)
                tail = tprev
                del cache[targs]
                targs,tprev,_ = clist[tail]
                clist[tail] = (targs,tprev,None)
                cache[args] = (value,oldtail)
                clist[oldtail] = (args,None,head)
                hargs,_,hnext = clist[head]
                clist[head] = (hargs,oldtail,hnext)
                head = oldtail

            return value

        def cache_clear():
            nonlocal cache,clist,csize,head,tail
            cache = dict()
            clist = []
            csize = head = tail = 0
            pass

        def cache_size() -> int:
            assert len(cache) == csize
            return csize

        def _debug():
            print('cache =',cache)
            print('clist =',clist)
            print(f'csize = {csize}, head = {head}, tail = {tail}')
            if csize > 1:
                i = head
                assert clist[i][1] == None
                print(clist[i][0])
                j = clist[i][2]
                assert isinstance(j,int)
                print(clist[j][0])
                assert clist[i][2] == j
                assert clist[j][1] == i
                while clist[j][2] != None:
                    i = j
                    j = clist[j][2]
                    assert isinstance(j,int)
                    assert clist[i][2] == j
                    assert clist[j][1] == i
                    print(clist[j][0])

        wrapped.cache_clear = cache_clear
        wrapped.cache_size = cache_size
        wrapped._debug = _debug
        return wrapped

    return wrapper

if __name__ == '__main__':

    @cache_all
    def fib(n:int) -> int:
        return n if n < 2 else fib(n-1) + fib(n-2)

    assert fib.cache_size() == 0
    assert fib(30) == 832040
    assert fib(35) == 9227465
    assert fib(40) == 102334155
    assert fib.cache_size() == 41
    assert fib(45) == 1134903170
    assert fib(50) == 12586269025
    assert fib.cache_size() == 51
    fib.cache_clear()
    assert fib.cache_size() == 0

    @cache_lru(10)
    def double(n:int) -> int:
        return 2*n

    assert double(0) == 0
    assert double(0) == 0
    assert double(1) == 2
    assert double(2) == 4
    assert double(1) == 2
    assert double(0) == 0
    assert double.cache_size() == 3

    for z in range(100):
        r = (19*z + 3) % 14
        assert double(r) == 2*r
    assert double.cache_size() == 10
    assert double(10) == 20
    assert double(5) == 10
    double.cache_clear()

    assert double.cache_size() == 0
    assert double(2) == 4
    assert double.cache_size() == 1
    assert double(5) == 10
    assert double.cache_size() == 2
