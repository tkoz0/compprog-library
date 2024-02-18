/*
DLList<T> - doubly linked list
- stores items individually as list nodes
- supports bidirectional iteration and more than SLList<T>
- good for applications that require a lot of insert/erase in the middle

Interface (instances):
DLList() - empty list
DLList(siz[,val]) - length <siz> list, fill with <val>
DLList({val0,val1,...}) - initializer list
begin() - begin iterator (bidirectional, cyclic)
end() - end iterator
size() - number of nodes
empty() - is length 0
== and != - lists equal if same length and elements in same order
get(i)
- get from index i, negative index supported
- searches from the end to minimize iteration time
push_front(val) - append val to back
push_back(val) - append val to front
pop_front() - remove and return first element
pop_back() - remove and return last element
+= <val> - push_back
-= <val> - push_front
+= <list> - concatenate to end
reverse() - in place reverse order
sort([comp]) - in place stable sort
insert(itr,val) - insert before itr, return iterator to new node
erase(itr) - remove value at itr, return iterator to next node

Interface (static):
fromFunc(n,func) - makes list with values func(0),func(1),...,func(n-1)

Test command:
g++ -g -Wall -Wextra -Werror -std=c++11 dllist.cpp && valgrind --leak-check=full --track-origins=yes ./a.out
*/

#include <algorithm>
#include <exception>
#include <functional>
#include <initializer_list>
#include <iostream>
#include <string>

#define CHECK_THROW(expr) (static_cast<bool>(expr) ? void(0) : \
throw std::runtime_error(std::string(#expr) + " FILE=" \
+ std::string(__FILE__) + " LINE=" +  std::to_string(__LINE__)))

template <typename T>
class DLList
{
private:
    struct _node
    {
        T _val;
        _node *_prev, *_next;
        inline _node(const T& val = T(), _node *prev = nullptr, _node *next = nullptr) noexcept:
            _val(val), _prev(prev), _next(next) {}
        inline _node(T&& val = T(), _node *prev = nullptr, _node *next = nullptr) noexcept:
            _val(val), _prev(prev), _next(next) {}
    };
    struct _iter
    {
        _node *_ptr;
        DLList<T> *_list;
        inline _iter(_node *ptr, DLList<T> *list) noexcept: _ptr(ptr), _list(list) {}
        inline T& operator*() { CHECK_THROW(_ptr); return _ptr->_val; }
        inline const T& operator*() const { CHECK_THROW(_ptr); return _ptr->_val; }
        inline T& operator->() { CHECK_THROW(_ptr); return _ptr->_val; }
        inline const T& operator->() const { CHECK_THROW(_ptr); return _ptr->_val; }
        inline _iter& operator++() { _ptr = _ptr ? _ptr->_next : _list->_head; return *this; } // pre
        inline _iter operator++(int) { _iter ret = *this; ++(*this); return ret; } // post
        inline _iter& operator--() { _ptr = _ptr ? _ptr->_prev : _list->_tail; return *this; } // pre
        inline _iter operator--(int) { _iter ret = *this; --(*this); return ret; } // post
        inline bool operator==(const _iter& i) const { return _ptr == i._ptr; }
        inline bool operator!=(const _iter& i) const { return _ptr != i._ptr; }
        inline operator bool() const { return _ptr; }
    };
    struct _citer
    {
        const _node *_ptr;
        const DLList<T> *_list;
        inline _citer(const _node *ptr, const DLList<T> *list) noexcept: _ptr(ptr), _list(list) {}
        inline const T& operator*() { CHECK_THROW(_ptr); return _ptr->_val; }
        inline const T& operator->() { CHECK_THROW(_ptr); return _ptr->_val; }
        inline _citer& operator++() { _ptr = _ptr ? _ptr->_next : _list->_head; return *this; } // pre
        inline _citer operator++(int) { _citer ret = *this; ++(*this); return ret; } // post
        inline _citer& operator--() { _ptr = _ptr ? _ptr->_prev : _list->_tail; return *this; } // pre
        inline _citer operator--(int) { _citer ret = *this; --(*this); return ret; } // post
        inline bool operator==(const _citer& i) const { return _ptr == i._ptr; }
        inline bool operator!=(const _citer& i) const { return _ptr != i._ptr; }
        inline operator bool() const { return _ptr; }
    };
    _node *_head, *_tail;
    size_t _size;
    // delete all nodes, does not touch _size
    inline void _clear()
    {
        while (_head)
        {
            _node *n = _head;
            _head = _head->_next;
            delete n;
        }
        _tail = nullptr;
    }
    // duplicate linked list, does no clear existing data
    inline void _copy_ll(_node *n)
    {
        if (!n)
            _head = _tail = nullptr;
        else
        {
            _head = _tail = new _node(n->_val);
            while (n->_next)
            {
                n = n->_next;
                _tail->_next = new _node(n->_val,_tail);
                _tail = _tail->_next;
            }
        }
    }
    // sort (in place merge sort, stable)
    template <typename F>
    static inline std::pair<_node*,_node*> _sort(_node *beg, _node *end, F comp)
    {
        if (beg == end) return {beg,end};
        _node *m1 = beg, *m2 = end;
        for (;;)
        {
            if (m1->_next == m2)
                break;
            m1 = m1->_next;
            if (m2->_prev == m1)
                break;
            m2 = m2->_prev;
        }
        m1->_next = nullptr;
        m2->_prev = nullptr;
        auto sorted_left = _sort(beg,m1,comp);
        auto sorted_right = _sort(m2,end,comp);
        _node *left = sorted_left.first, *right = sorted_right.first;
        _node *ret_head, *ret_tail;
        // first node, ensuring stable order
        if (comp(right->_val,left->_val))
        {
            ret_head = ret_tail = right;
            right = right->_next;
        }
        else
        {
            ret_head = ret_tail = left;
            left = left->_next;
        }
        while (left && right)
        {
            if (comp(right->_val,left->_val))
            {
                right->_prev = ret_tail;
                ret_tail->_next = right;
                right = right->_next;
            }
            else
            {
                left->_prev = ret_tail;
                ret_tail->_next = left;
                left = left->_next;
            }
            ret_tail = ret_tail->_next;
        }
        if (left)
        {
            left->_prev = ret_tail;
            ret_tail->_next = left;
            ret_tail = sorted_left.second;
        }
        else
        {
            right->_prev = ret_tail;
            ret_tail->_next = right;
            ret_tail = sorted_right.second;
        }
        return {ret_head,ret_tail};
    }
    // sort driver function
    template <typename F>
    inline void _sort_init(F comp)
    {
        auto sorted = _sort(_head,_tail,comp);
        _head = sorted.first;
        _tail = sorted.second;
    }
public:
    typedef _iter itr_t;
    typedef _citer citr_t;
    DLList() noexcept: _head(nullptr), _tail(nullptr), _size(0) {}
    ~DLList() { _clear(); }
    DLList(int64_t siz, const T& val = T())
    {
        CHECK_THROW(siz >= 0);
        CHECK_THROW(siz < (1LL << 48));
        _size = siz;
        if (siz == 0)
            _head = _tail = nullptr;
        else
        {
            _head = _tail = new _node(val);
            while (--siz)
            {
                _tail->_next = new _node(val,_tail);
                _tail = _tail->_next;
            }
        }
    }
    DLList(std::initializer_list<T> vals)
    {
        _head = _tail = nullptr;
        for (const T& val : vals)
        {
            if (_tail)
            {
                _tail->_next = new _node(val,_tail);
                _tail = _tail->_next;
            }
            else
                _head = _tail = new _node(val);
        }
        _size = vals.size();
    }
    DLList(const DLList<T>& list)
    {
        _copy_ll(list._head);
        _size = list._size;
    }
    DLList(DLList<T>&& list) noexcept
    {
        _head = list._head;
        _tail = list._tail;
        _size = list._size;
        list._head = list._tail = nullptr;
    }
    DLList<T>& operator=(const DLList<T>& list)
    {
        _clear();
        _copy_ll(list._head);
        _size = list._size;
        return *this;
    }
    DLList<T>& operator=(DLList<T>&& list)
    {
        _clear();
        _head = list._head;
        _tail = list._tail;
        _size = list._size;
        list._head = list._tail = nullptr;
        return *this;
    }
    inline itr_t begin() noexcept { return _iter(_head,this); }
    inline citr_t begin() const noexcept { return _citer(_head,this); }
    inline itr_t end() noexcept { return _iter(nullptr,this); }
    inline citr_t end() const noexcept { return _citer(nullptr,this); }
    inline size_t size() const noexcept { return _size; }
    inline bool empty() const noexcept { return _size == 0; }
    inline bool operator==(const DLList<T>& list)
    {
        if (_size != list._size)
            return false;
        _node *n1 = _head, *n2 = list._head;
        while (n1)
        {
            if (n1->_val != n2->_val)
                return false;
            n1 = n1->_next;
            n2 = n2->_next;
        }
        return true;
    }
    inline bool operator!=(const DLList<T>& list) { return !(*this == list); }
    inline T& get(int64_t i)
    {
        CHECK_THROW(i < (int64_t)_size && i >= -(int64_t)_size);
        size_t j = i >= 0 ? i : _size+i;
        if (j >= _size/2)
        {
            _node *n = _tail;
            while (++j < _size)
                n = n->_prev;
            return n->_val;
        }
        else
        {
            _node *n = _head;
            while (j--)
                n = n->_next;
            return n->_val;
        }
    }
    inline const T& get(int64_t i) const
    {
        CHECK_THROW(i < (int64_t)_size && i >= -(int64_t)_size);
        size_t j = i >= 0 ? i : _size+i;
        if (j >= _size/2)
        {
            _node *n = _tail;
            while (++j < _size)
                n = n->_prev;
            return n->_val;
        }
        else
        {
            _node *n = _head;
            while (j--)
                n = n->_next;
            return n->_val;
        }
    }
    friend std::ostream& operator<<(std::ostream& os, const DLList<T>& list)
    {
        os << "DLList[";
        if (list.size() > 0)
        {
            auto itr = list.begin();
            os << *itr;
            ++itr;
            while (itr != list.end())
            {
                os << "," << *itr;
                ++itr;
            }
        }
        os << "]";
        return os;
    }
    inline void push_front(const T& val)
    {
        if (!_head)
            _head = _tail = new _node(val);
        else
        {
            _head->_prev = new _node(val,nullptr,_head);
            _head = _head->_prev;
        }
        ++_size;
    }
    inline void push_front(T&& val)
    {
        if (!_head)
            _head = _tail = new _node(val);
        else
        {
            _head->_prev = new _node(val,nullptr,_head);
            _head = _head->_prev;
        }
        ++_size;
    }
    inline void push_back(const T& val)
    {
        if (!_head)
            _head = _tail = new _node(val);
        else
        {
            _tail->_next = new _node(val,_tail);
            _tail = _tail->_next;
        }
        ++_size;
    }
    inline void push_back(T&& val)
    {
        if (!_head)
            _head = _tail = new _node(val);
        else
        {
            _tail->_next = new _node(val,_tail);
            _tail = _tail->_next;
        }
        ++_size;
    }
    inline T pop_front()
    {
        CHECK_THROW(_head);
        T ret = std::move(_head->_val);
        _node *n = _head;
        _head = _head->_next;
        delete n;
        if (_head)
            _head->_prev = nullptr;
        else
            _tail = nullptr;
        --_size;
        return ret;
    }
    inline T pop_back()
    {
        CHECK_THROW(_tail);
        T ret = std::move(_tail->_val);
        _node *n = _tail;
        _tail = _tail->_prev;
        delete n;
        if (_tail)
            _tail->_next = nullptr;
        else
            _head = nullptr;
        --_size;
        return ret;
    }
    inline void clear() { _clear(); _size = 0; }
    inline DLList<T>& operator+=(const T& val) { push_back(val); return *this; }
    inline DLList<T>& operator+=(T&& val) { push_back(val); return *this; }
    inline DLList<T>& operator-=(const T& val) { push_front(val); return *this; }
    inline DLList<T>& operator-=(T&& val) { push_front(val); return *this; }
    inline DLList<T>& operator+=(const DLList<T>& list)
    {
        for (const T& val : list)
            *this += val;
        return *this;
    }
    inline DLList<T>& operator+=(DLList<T>&& list)
    {
        if (!_head) // this is empty so move
        {
            _head = list._head;
            _tail = list._tail;
            _size = list._size;
            list._head = list._tail = nullptr;
        }
        else if (list._head) // both nonempty
        {
            _tail->_next = list._head;
            list._head->_prev = _tail;
            _tail = list._tail;
            list._head = list._tail = nullptr;
            _size += list._size;
        }
        return *this;
    }
    inline void reverse()
    {
        std::swap(_head,_tail);
        _node *n = _head;
        while (n)
        {
            std::swap(n->_next,n->_prev);
            n = n->_next;
        }
    }
    static DLList<T> fromFunc(size_t n, std::function<T(size_t)> func)
    {
        DLList<T> ret;
        for (size_t i = 0; i < n; ++i)
            ret += func(i);
        return ret;
    }
    template <typename F>
    inline void sort(F comp) { if (_head) _sort_init(comp); }
    inline void sort() { sort([](const T& a, const T& b){ return a < b; }); }
    inline itr_t insert(itr_t itr, const T& val)
    {
        if (itr == begin())
        {
            push_front(val);
            return begin();
        }
        else if (itr == end())
        {
            push_back(val);
            return _iter(_tail,this);
        }
        else
        {
            ++_size;
            _node *n = new _node(val,itr._ptr->_prev,itr._ptr);
            itr._ptr->_prev->_next = n;
            itr._ptr->_prev = n;
            return _iter(n,this);
        }
    }
    inline itr_t insert(itr_t itr, T&& val)
    {
        if (itr == begin())
        {
            push_front(val);
            return begin();
        }
        else if (itr == end())
        {
            push_back(val);
            return _iter(_tail,this);
        }
        else
        {
            ++_size;
            _node *n = new _node(val,itr._ptr->_prev,itr._ptr);
            itr._ptr->_prev->_next = n;
            itr._ptr->_prev = n;
            return _iter(n,this);
        }
    }
    inline itr_t erase(itr_t itr)
    {
        CHECK_THROW(itr != end());
        if (itr == begin())
        {
            pop_front();
            return begin();
        }
        --_size;
        if (itr._ptr == _tail)
        {
            _tail = itr._ptr->_prev;
            _tail->_next = nullptr;
            delete itr._ptr;
            return end();
        }
        else
        {
            itr._ptr->_prev->_next = itr._ptr->_next;
            itr._ptr->_next->_prev = itr._ptr->_prev;
            auto ret = _iter(itr._ptr->_next,this);
            delete itr._ptr;
            return ret;
        }
    }
};

/*  ****************************************************************************
test code
****************************************************************************  */

#include <cassert>
#include <sstream>

#define assert_throw(expr) \
do { try { expr; assert(0); } \
catch (...) {} } while(0)

void test_ctor()
{
    // default
    DLList<float> a1;
    assert(a1.size() == 0);
    assert(a1.empty());
    assert(a1.begin() == a1.end());
    // size
    DLList<int> a2(5,-1);
    assert(a2.size() == 5);
    assert(!a2.empty());
    assert(a2.begin() != a2.end());
    assert_throw(DLList<std::string>(-1,""));
    // initializer list
    DLList<float> a3{1.5,-2.2};
    assert(a3.size() == 2);
    assert(*a3.begin() == 1.5);
    assert(++(++a3.begin()) == a3.end());
    assert_throw(*a3.end());
    DLList<char> a4({'[',']','(',')','{','}'});
    assert(a4.size() == 6);
    assert(*a4.begin() == '[');
    assert(*(++a4.begin()) == ']');
    assert(++(++(++(++(++(++a4.begin()))))) == a4.end());
    assert(a4.begin());
    assert(!(++(++(++(++(++(++a4.begin())))))));
    assert(++(++(++(++(++(++(++a4.begin())))))) == a4.begin());
    // copy
    DLList<char> a5(a4);
    assert(a5 == a4);
    DLList<int> a6(a2);
    assert(a6 == a2);
    // move
    DLList<std::string> b1(DLList<std::string>(7,"seven"));
    assert(b1 == DLList<std::string>({"seven","seven","seven","seven","seven","seven","seven"}));
    DLList<int> b2(DLList<int>{});
    assert(b2 == DLList<int>());
    // = copy
    auto b3 = b1;
    assert(b3 == b1);
    auto b4 = a4;
    assert(b4 == a4);
    // = move
    auto b5 = DLList<float>{1.5,-2.2};
    assert(b5 == a3);
    auto b6 = DLList<char>{'[',']','(',')','{','}'};
    assert(b6 == a4);
}

void test_comp()
{
    DLList<short> a1;
    assert(a1 == DLList<short>({}));
    assert(a1 != DLList<short>(1));
    a1 = {6,8,10,12,14};
    assert(a1 == DLList<short>({6,8,10,12,14}));
    assert(a1 != DLList<short>({8,10,12,14}));
    assert(a1 != DLList<short>({6,8,10,12}));
    assert(a1 != DLList<short>({6,8,10,12,14,16}));
    assert(a1 != DLList<short>({6,8,100,12,14}));
}

void test_iter()
{
    DLList<std::string> a1;
    for (auto s : a1)
        (void)s, assert(0);
    assert(a1.begin() == a1.end());
    DLList<int> a2(12,-53);
    for (auto i : a2)
        assert(i == -53);
    assert(--a2.begin() == a2.end());
    DLList<uint64_t> a3{3,7,31,127,8191,131071,524287};
    auto iter = a3.begin();
    assert(*iter == 3);
    ++iter;
    assert(*iter == 7);
    ++iter;
    assert(*iter == 31);
    ++iter;
    assert(*iter == 127);
    ++iter;
    assert(*iter == 8191);
    ++iter;
    assert(*iter == 131071);
    ++iter;
    assert(*iter == 524287);
    ++iter;
    assert_throw(*iter);
    assert(iter == a3.end());
    ++iter;
    assert(iter == a3.begin());
    assert(*iter == 3);
    --iter;
    assert(iter == a3.end());
    assert_throw(*iter);
    --iter;
    assert(*iter == 524287);
    --iter;
    assert(*iter == 131071);
    // const iterator
    const DLList<uint64_t> a3c = a3;
    auto iter2 = a3c.begin();
    assert(*iter2 == 3);
    ++iter2;
    assert(*iter2 == 7);
    while (iter2 != a3c.end())
        ++iter2;
    assert(iter2 == a3c.end());
    --iter2;
    assert(*iter2 == 524287);
    --iter2;
    assert(*iter2 == 131071);
    ++iter2;
    ++iter2;
    ++iter2;
    assert(iter2 == a3c.begin());
}

void test_get()
{
    DLList<double> a1{0.785,1.57,3.14,6.28};
    assert(a1.get(0) == 0.785);
    assert(a1.get(1) == 1.57);
    assert(a1.get(2) == 3.14);
    assert(a1.get(3) == 6.28);
    assert_throw(a1.get(4));
    assert(a1.get(-1) == 6.28);
    assert(a1.get(-2) == 3.14);
    assert(a1.get(-3) == 1.57);
    assert(a1.get(-4) == 0.785);
    assert_throw(a1.get(-5));
    DLList<std::string> a2;
    assert_throw(a2.get(0));
    assert_throw(a2.get(1));
    assert_throw(a2.get(-1));
}

void test_print()
{
    std::stringstream ss;
    ss.str("");
    ss << DLList<float>();
    assert(ss.str() == "DLList[]");
    ss.str("");
    ss << DLList<int>(6,-19);
    assert(ss.str() == "DLList[-19,-19,-19,-19,-19,-19]");
    ss.str("");
    ss << DLList<std::string>{"umi","honoka","kotori"};
    assert(ss.str() == "DLList[umi,honoka,kotori]");
}

void test_push_pop()
{
    DLList<char> a1;
    a1.push_back('a');
    assert(a1 == DLList<char>({'a'}));
    a1 += ('b');
    assert(a1 == DLList<char>({'a','b'}));
    a1.push_back('c');
    assert(a1 == DLList<char>({'a','b','c'}));
    char c;
    c = a1.pop_back();
    assert(c == 'c');
    assert(a1 == DLList<char>({'a','b'}));
    c = a1.pop_back();
    assert(c == 'b');
    assert(a1 == DLList<char>({'a'}));
    c = a1.pop_back();
    assert(c == 'a');
    assert(a1.empty());
    assert_throw(a1.pop_back());
    DLList<short> a2;
    a2.push_front(6);
    assert(a2 == DLList<short>({6}));
    a2 -= -6;
    assert(a2 == DLList<short>({-6,6}));
    a2.push_front(-90);
    assert(a2 == DLList<short>({-90,-6,6}));
    short s;
    s = a2.pop_front();
    assert(s == -90);
    assert(a2 == DLList<short>({-6,6}));
    s = a2.pop_front();
    assert(s == -6);
    assert(a2 == DLList<short>({6}));
    s = a2.pop_front();
    assert(s == 6);
    assert(a2.empty());
    assert_throw(a1.pop_front());
    DLList<std::string> a3 = {"sunshine","superstar"};
    a3.clear();
    assert(a3 == DLList<std::string>());
}

void test_rev()
{
    DLList<short> a1;
    a1.reverse();
    assert(a1 == DLList<short>());
    DLList<int> a2{1};
    a2.reverse();
    assert(a2 == DLList<int>({1}));
    a2.push_back(2);
    a2.reverse();
    assert(a2 == DLList<int>({2,1}));
    a2.push_front(3);
    a2.reverse();
    assert(a2 == DLList<int>({1,2,3}));
    DLList<std::string> a3 = {"this","sentence","has","five","words"};
    a3.reverse();
    assert(a3 == DLList<std::string>({"words","five","has","sentence","this"}));
    a3.reverse();
    assert(a3 == DLList<std::string>({"this","sentence","has","five","words"}));
}

void test_func()
{
    auto a1 = DLList<uint64_t>::fromFunc(6,[](size_t i){return 1uLL<<(10*i);});
    assert(a1 == DLList<uint64_t>({1,1024,1048576,1073741824,1099511627776uLL,1125899906842624uLL}));
    auto a2 = DLList<double>::fromFunc(32,[](size_t i){return 1.0/(i+1);});
    assert(a2.get(-1) == 1.0/32);
    assert(a2.get(-17) == 1.0/16);
    assert(a2.get(-25) == 1.0/8);
}

void test_sort()
{
    DLList<long> a1;
    a1.sort();
    assert(a1 == DLList<long>());
    a1 = {7};
    a1.sort();
    assert(a1 == DLList<long>({7}));
    a1 = {7,6};
    a1.sort();
    assert(a1 == DLList<long>({6,7}));
    a1 = {6,7,1,5,3,2,4};
    a1.sort();
    assert(a1 == DLList<long>({1,2,3,4,5,6,7}));
    // stable sort test
    auto tenscomp = [](uint32_t a, uint32_t b){return a/10 < b/10;};
    DLList<int> b1 = {10,12,11,22,28,24,20,26,31,39};
    DLList<int> b2 = {22,10,31,28,24,39,12,20,11,26};
    b2.sort(tenscomp);
    assert(b1 == b2);
    DLList<std::string> b3 = {"art","ant","apple","bats","bat","bark","center","coat","curve"};
    DLList<std::string> b4 = {"art","center","bats","coat","ant","curve","apple","bat","bark"};
    b4.sort([](const std::string& a, const std::string& b)
    {
        return a[0] < b[0]; // compare first letter only
    });
    assert(b3 == b4);
    // primitive root (42) test (mod 1103)
    a1 = {};
    long a1i = 1;
    for (long i = 1; i < 1103; ++i)
    {
        a1i = (a1i*42) % 1103;
        a1.push_back(a1i);
    }
    DLList<long> a2 = a1;
    a1.sort();
    a2.sort([](uint32_t a, uint32_t b){return a > b;});
    auto iter1 = a1.begin(), iter2 = a2.begin();
    for (long i = 1; i < 1103; ++i)
    {
        assert(*iter1 == i);
        assert(*iter2 == 1103-i);
        ++iter1, ++iter2;
    }
    assert(iter1 == a1.end());
    assert(iter2 == a2.end());
}

void test_insert_erase()
{
    DLList<int> a1;
    assert_throw(*a1.begin());
    auto a1iter = a1.begin();
    a1iter = a1.insert(a1iter,999);
    assert(a1iter == a1.begin());
    a1iter = a1.insert(a1iter,99);
    assert(a1iter == a1.begin());
    a1iter = a1.insert(a1iter,9);
    assert(a1iter == a1.begin());
    assert(a1 == DLList<int>({9,99,999}));
    DLList<int> a2;
    auto a2iter = a2.end();
    a2iter = a2.insert(a2iter,9);
    ++a2iter;
    assert(a2iter == a2.end());
    a2iter = a2.insert(a2iter,99);
    ++a2iter;
    assert(a2iter == a2.end());
    a2iter = a2.insert(a2iter,999);
    ++a2iter;
    assert(a2iter == a2.end());
    assert(a2 == a1);
    a1iter = a1.begin();
    assert(*a1iter == 9);
    a1iter = a1.erase(a1iter);
    assert(*a1iter == 99);
    assert(a1 == DLList<int>({99,999}));
    a1iter = a1.erase(a1iter);
    assert(*a1iter == 999);
    assert(a1 == DLList<int>({999}));
    assert(a1iter == a1.begin());
    a1iter = a1.erase(a1iter);
    assert_throw(*a1iter);
    assert(a1iter == a1.end());
    assert(a1 == DLList<int>());
    a2iter = a2.begin();
    ++a2iter;
    ++a2iter;
    assert(*a2iter == 999);
    a2iter = a2.erase(a2iter);
    assert(a2iter == a2.end());
    --a2iter;
    assert(*a2iter == 99);
    assert(a2 == DLList<int>({9,99}));
    a2iter = a2.erase(a2iter);
    assert(a2iter == a2.end());
    --a2iter;
    assert(*a2iter == 9);
    assert(a2 == DLList<int>({9}));
    a2iter = a2.erase(a2iter);
    assert(a2iter == a2.begin());
    assert(a2iter == a2.end());
    assert(a2 == a1);
    DLList<int> a3{10,15,20,25,30,35,40};
    auto a3iter = a3.begin();
    while (a3iter != a3.end())
    {
        auto a3iter2 = a3iter;
        if (*a3iter % 10 == 0)
            a3iter = a3.insert(++a3iter2,*a3iter+1);
        ++a3iter;
    }
    assert(a3 == DLList<int>({10,11,15,20,21,25,30,31,35,40,41}));
}

int main()
{
    test_ctor();
    test_comp();
    test_iter();
    test_get();
    test_print();
    test_push_pop();
    test_rev();
    test_func();
    test_sort();
    test_insert_erase();
}
