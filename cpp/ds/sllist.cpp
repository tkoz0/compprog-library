/*
SLList<T> - singly linked list
- stores items individually as list nodes
- good for applications that require a lot of insert/erase in the middle

Interface (instances):
SLList() - empty list
SLList(siz[,val]) - length <siz> list where each node contains <val>
SLList({val0,val1,...}) - list from initializer list
begin() - begin iterator (only supports ++)
end() - end iterator (cannot modify)
size() - number of nodes in list
empty() - is list length 0
== and != - lists equal if same length and same elements in same order
get(i)
- lookup index i (negative supported for counting from end)
- not using [] to discourage use since this is a slow operation for linked list
push_front(val) - create new beginning node
push_back(val) - add new node to end
pop_front() - get node and front and remove, list must be nonempty
clear() - delete all nodes
+= <val> - push_back
-= <val> - push_front
+= <list> - concatenate list to end
reverse() - in place reverse of list node order
sort([comp]) - in place stable sort of the list nodes
insert(iter,val)
- insert before iter, iter becomes invalid, returns iterator to inserted value
erase(iter)
- erase iter value, iter becomes invalid, returns iterator to next value

Interface (static):
fromFunc(n,func) - makes list with nodes func(0),func(1),...,func(n-1)

Test command:
g++ -g -Wall -Wextra -Werror -std=c++11 sllist.cpp && valgrind --leak-check=full --track-origins=yes ./a.out
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
class SLList
{
private:
    // linked list node
    struct _node
    {
        // value stored
        T _val;
        // pointer to next
        _node *_next;
        // copy construction
        inline _node(const T& val = T(), _node *next = nullptr): _val(val), _next(next) {}
        // move construction
        inline _node(T&& val = T(), _node *next = nullptr): _val(val), _next(next) {}
    };
    // iterator
    struct _iter
    {
        // pointer to previous and current
        // previous pointer is needed for insert and erase operations
        _node *_prev, *_ptr;
        inline _iter(_node *prev, _node *ptr) noexcept: _prev(prev), _ptr(ptr) {}
        inline T& operator*() { CHECK_THROW(_ptr); return _ptr->_val; }
        inline const T& operator*() const { CHECK_THROW(_ptr); return _ptr->_val; }
        inline T& operator->() { CHECK_THROW(_ptr); return _ptr->_val; }
        inline const T& operator->() const { CHECK_THROW(_ptr); return _ptr->_val; }
        inline _iter& operator++() { CHECK_THROW(_ptr); _prev = _ptr; _ptr = _ptr->_next; return *this; } // pre
        inline _iter operator++(int) { _iter ret = *this; ++(*this); return ret; } // post
        inline bool operator==(const _iter& i) const { return _ptr == i._ptr; }
        inline bool operator!=(const _iter& i) const { return _ptr != i._ptr; }
        inline operator bool() const { return _ptr; }
    };
    // const iterator
    struct _citer
    {
        // pointer to node
        const _node *_ptr;
        inline _citer(const _node *ptr) noexcept: _ptr(ptr) {}
        inline const T& operator*() { CHECK_THROW(_ptr); return _ptr->_val; }
        inline const T& operator->() const { CHECK_THROW(_ptr); return _ptr->_val; }
        inline _citer& operator++() { CHECK_THROW(_ptr); _ptr = _ptr->_next; return *this; } // pre
        inline _citer operator++(int) { _citer ret = *this; ++(*this); return ret; } // post
        inline bool operator==(const _citer& i) const { return _ptr == i._ptr; }
        inline bool operator!=(const _citer& i) const { return _ptr != i._ptr; }
        inline operator bool() const { return _ptr; }
    };
    // pointers for start and end of list
    _node *_head, *_tail;
    // number of nodes in list
    size_t _size;
    // delete all nodes, does not modify _size
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
    // duplicate linked list into this list
    // does not clear existing values, does not touch _size
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
                _tail->_next = new _node(n->_val);
                _tail = _tail->_next;
            }
        }
    }
    // sort (in place merge sort, stable)
    template <typename F>
    static inline std::pair<_node*,_node*> _sort(_node *beg, _node *end, size_t len, F comp)
    {
        if (len == 1) return {beg,end};
        // find m1 (end of first half) and m2 (begin of second half)
        _node *m1 = nullptr, *m2 = beg;
        for (size_t i = 0; i < len/2; ++i)
        {
            m1 = m2;
            m2 = m2->_next;
        }
        m1->_next = nullptr;
        auto sorted_left = _sort(beg,m1,len/2,comp);
        auto sorted_right = _sort(m2,end,len-len/2,comp);
        _node *left = sorted_left.first, *right = sorted_right.first;
        _node *ret_head, *ret_tail;
        // first node, ensure order stays same if equal
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
        while (left && right) // take while both halves have more items
        {
            if (comp(right->_val,left->_val))
            {
                ret_tail->_next = right;
                right = right->_next;
            }
            else
            {
                ret_tail->_next = left;
                left = left->_next;
            }
            ret_tail = ret_tail->_next;
        }
        if (left) // put remaining items at end of list
        {
            ret_tail->_next = left;
            ret_tail = sorted_left.second;
        }
        else
        {
            ret_tail->_next = right;
            ret_tail = sorted_right.second;
        }
        return {ret_head,ret_tail};
    }
    // sort driver function
    template <typename F>
    inline void _sort_init(F comp)
    {
        auto sorted = _sort(_head,_tail,_size,comp);
        _head = sorted.first;
        _tail = sorted.second;
    }
    // swap contents with other
    inline void _swap(SLList<T>& list) noexcept
    {
        std::swap(_head,list._head);
        std::swap(_tail,list._tail);
        std::swap(_size,list._size);
    }
public:
    // iterator
    typedef _iter itr_t;
    // const iterator
    typedef _citer citr_t;
    // default constructor (empty)
    SLList() noexcept: _head(nullptr), _tail(nullptr), _size(0) {}
    // destructor
    ~SLList() { _clear(); }
    // size with fill value
    SLList(int64_t siz, const T& val = T())
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
                _tail->_next = new _node(val);
                _tail = _tail->_next;
            }
        }
    }
    // initializer list
    SLList(std::initializer_list<T> vals)
    {
        _head = _tail = nullptr;
        for (const T& val : vals)
        {
            if (_tail)
            {
                _tail->_next = new _node(val);
                _tail = _tail->_next;
            }
            else
                _head = _tail = new _node(val);
        }
        _size = vals.size();
    }
    // copy constructor
    SLList(const SLList<T>& list)
    {
        _copy_ll(list._head);
        _size = list._size;
    }
    // move constructor
    SLList(SLList<T>&& list) noexcept: SLList() { _swap(list); }
    // copy assignment
    SLList<T>& operator=(const SLList<T>& list)
    { SLList<T> tmp(list); _swap(tmp); return *this; }
    // move assignment
    SLList<T>& operator=(SLList<T>&& list) noexcept
    { _swap(list); return *this; }
    // begin iterator
    inline itr_t begin() noexcept { return _iter(nullptr,_head); }
    // begin const iterator
    inline citr_t begin() const noexcept { return _citer(_head); }
    // end iterator
    inline itr_t end() noexcept { return _iter(_tail,nullptr); }
    // end const iterator
    inline citr_t end() const noexcept { return _citer(nullptr); }
    // number of list nodes
    inline size_t size() const noexcept { return _size; }
    // is list empty
    inline bool empty() const noexcept { return _size == 0; }
    // compare equality (same size and same elements in same order)
    inline bool operator==(const SLList<T>& list)
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
    // compare inequality
    inline bool operator!=(const SLList<T>& list) { return !(*this == list); }
    // element access by index (slow)
    inline T& get(int64_t i)
    {
        return const_cast<T&>(const_cast<const SLList<T>*>(this)->get(i));
    }
    // const element access by index (slow)
    inline const T& get(int64_t i) const
    {
        CHECK_THROW(i < (int64_t)_size && i >= -(int64_t)_size);
        size_t j = i >= 0 ? i : _size+i;
        _node *n = _head;
        while (j--)
            n = n->_next;
        return n->_val;
    }
    // text representation
    friend std::ostream& operator<<(std::ostream& os, const SLList<T>& list)
    {
        os << "SLList[";
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
    // append at front
    inline void push_front(const T& val)
    {
        T tmp = val;
        push_front(std::move(tmp));
    }
    // append at front
    inline void push_front(T&& val)
    {
        if (!_head) _head = _tail = new _node(val);
        else _head = new _node(val,_head);
        ++_size;
    }
    // append at back
    inline void push_back(const T& val)
    {
        T tmp = val;
        push_back(std::move(tmp));
    }
    // append at back
    inline void push_back(T&& val)
    {
        if (!_head) _head = _tail = new _node(val);
        else
        {
            _tail->_next = new _node(val);
            _tail = _tail->_next;
        }
        ++_size;
    }
    // remove from front
    inline T pop_front()
    {
        CHECK_THROW(_head);
        T ret = std::move(_head->_val);
        _node *n = _head;
        _head = _head->_next;
        delete n;
        if (!_head) _tail = nullptr;
        --_size;
        return ret;
    }
    // empty container
    inline void clear() { _clear(); _size = 0; }
    // append at back
    inline SLList<T>& operator+=(const T& val) { push_back(val); return *this; }
    // append at back
    inline SLList<T>& operator+=(T&& val) { push_back(val); return *this; }
    // append at front
    inline SLList<T>& operator-=(const T& val) { push_front(val); return *this; }
    // append at front
    inline SLList<T>& operator-=(T&& val) { push_front(val); return *this; }
    // append list at back
    inline SLList<T>& operator+=(const SLList<T>& list)
    {
        for (const T& val : list)
            *this += val;
        return *this;
    }
    // append list at back
    inline SLList<T>& operator+=(SLList<T>&& list)
    {
        if (!_head) // this is empty, move from list
        {
            _head = list._head;
            _tail = list._tail;
            _size = list._size;
            list._head = list._tail = nullptr;
        }
        else if (list._head) // this is nonempty and list is nonempty
        {
            _tail->_next = list._head;
            _tail = list._tail;
            list._head = list._tail = nullptr;
            _size += list._size;
        }
        return *this;
    }
    // reverse order of nodes
    inline void reverse()
    {
        if (!_head)
            return;
        _node *_head_new, *_tail_new;
        _head_new = _tail_new = _head;
        _head = _head->_next;
        _tail_new->_next = nullptr;
        while (_head)
        {
            _node *tmp = _head;
            _head = _head->_next;
            tmp->_next = _head_new;
            _head_new = tmp;
        }
        _head = _head_new;
        _tail = _tail_new;
    }
    // create list from func(0),func(1),...,func(n-1)
    static SLList<T> fromFunc(size_t n, std::function<T(size_t)> func)
    {
        SLList<T> ret;
        for (size_t i = 0; i < n; ++i)
            ret += func(i);
        return ret;
    }
    // (stable) sort with custom comparator
    template <typename F>
    inline void sort(F comp) { if (_head) _sort_init(comp); }
    // (stable) sort with default comparator
    inline void sort() { sort([](const T& a, const T& b){ return a < b; }); }
    // insert before itr, return iterator to new node
    inline itr_t insert(itr_t itr, const T& val)
    {
        T tmp = val;
        return insert(itr,std::move(tmp));
    }
    // insert before itr, return iterator to new node
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
            return _iter(itr._prev,_tail);
        }
        else
        {
            itr._prev->_next = new _node(val,itr._ptr);
            ++_size;
            return _iter(itr._prev,itr._prev->_next);
        }
    }
    // erase itr and return iterator to next node
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
            _tail = itr._prev;
            _tail->_next = nullptr;
            delete itr._ptr;
            return end();
        }
        else
        {
            itr._prev->_next = itr._ptr->_next;
            auto ret = _iter(itr._prev,itr._ptr->_next);
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
    SLList<double> a1;
    assert(a1.size() == 0);
    assert(a1.empty());
    assert(a1.begin() == a1.end());
    // size
    SLList<double> a2(1);
    assert(a2.size() == 1);
    assert(!a2.empty());
    assert(a2.begin() != a2.end());
    assert(++a2.begin() == a2.end());
    assert_throw(SLList<int>(-1));
    // initializer list
    SLList<std::string> a3{"tkoz","was","here"};
    assert(a3.size() == 3);
    assert(*a3.begin() == "tkoz");
    assert(++(++(++a3.begin())) == a3.end());
    assert_throw(*a3.end());
    SLList<int> a4{-1,-2,-3,-4,-5};
    assert(a4.size() == 5);
    assert(*a4.begin() == -1);
    assert(++(++(++(++(++a4.begin())))) == a4.end());
    // copy
    SLList<std::string> a5(a3);
    assert(a5 == a3);
    SLList<int> a6(a4);
    assert(a6 == a4);
    SLList<double> c1(a1);
    assert(a1 == c1);
    // move
    SLList<std::string> a7(SLList<std::string>(4,"words"));
    assert(a7 == SLList<std::string>({"words","words","words","words"}));
    SLList<float> a8(SLList<float>({2.1,2.2}));
    assert(a8 == SLList<float>({2.1,2.2}));
    SLList<double> c2(SLList<double>{});
    assert(c2 == a1);
    // = copy
    SLList<std::string> b1 = a3;
    assert(b1 == SLList<std::string>({"tkoz","was","here"}));
    auto b2 = a1;
    assert(b2 == a1);
    // = move
    auto b3 = SLList<std::string>({"tkoz","was","here"});
    assert(b3 == SLList<std::string>({"tkoz","was","here"}));
    auto b4 = SLList<int>{4,5,6};
    assert(b4 == SLList<int>({4,5,6}));
}

void test_comp()
{
    SLList<std::string> a1{};
    assert(a1 == SLList<std::string>());
    assert(a1 != SLList<std::string>({""}));
    a1 = {"a","b","c","d","e","f","g","h"};
    assert(a1 == SLList<std::string>({"a","b","c","d","e","f","g","h"}));
    assert(a1 != SLList<std::string>({"a","b","c","d","","f","g","h"}));
    assert(a1 != SLList<std::string>({"b","c","d","e","f","g","h"}));
    assert(a1 != SLList<std::string>({"a","b","c","d","e","f","g"}));
    assert(a1 != SLList<std::string>({"","a","b","c","d","e","f","g","h"}));
    assert(a1 != SLList<std::string>({"a","b","c","d","e","f","g","h",""}));
}

void test_iter()
{
    SLList<double> a1{};
    for (auto d : a1)
        (void)d, assert(0);
    SLList<int> a2{69};
    for (auto i : a2)
        assert(i == 69);
    size_t c = 0;
    a2 = SLList<int>(42,69);
    for (auto i : a2)
    {
        assert(i == 69);
        c += 1;
    }
    assert(c == 42);
    SLList<std::string> a3{"this","was","a","bad","idea"};
    auto iter = a3.begin();
    assert(*iter == "this");
    ++iter;
    assert(*iter == "was");
    ++iter;
    assert(*iter == "a");
    ++iter;
    assert(*iter == "bad");
    ++iter;
    assert(*iter == "idea");
    ++iter;
    assert(iter == a3.end());
    // const iteration
    const SLList<std::string>& a3c = a3;
    SLList<std::string>::citr_t iter2 = a3c.begin();
    assert(*iter2 == "this");
    ++iter2;
    assert(*iter2 == "was");
    ++iter2;
    assert(*iter2 == "a");
    ++iter2;
    assert(*iter2 == "bad");
    ++iter2;
    assert(*iter2 == "idea");
    ++iter2;
    assert(iter2 == a3c.end());
}

void test_get()
{
    SLList<std::string> a1{"this","was","a","bad","idea"};
    assert(a1.get(0) == "this");
    assert(a1.get(1) == "was");
    assert(a1.get(2) == "a");
    assert(a1.get(3) == "bad");
    assert(a1.get(4) == "idea");
    assert_throw(a1.get(5));
    assert(a1.get(-1) == "idea");
    assert(a1.get(-2) == "bad");
    assert(a1.get(-3) == "a");
    assert(a1.get(-4) == "was");
    assert(a1.get(-5) == "this");
    assert_throw(a1.get(-6));
    SLList<int> a2;
    assert_throw(a2.get(0));
    assert_throw(a2.get(1));
    assert_throw(a2.get(-1));
    a1.get(3) = "good";
    assert(a1 == SLList<std::string>({"this","was","a","good","idea"}));
    a1.get(0) = "that";
    assert(a1 == SLList<std::string>({"that","was","a","good","idea"}));
    a1.get(-4) = "is";
    assert(a1 == SLList<std::string>({"that","is","a","good","idea"}));
}

void test_print()
{
    std::stringstream ss;
    ss.str("");
    ss << SLList<int>();
    assert(ss.str() == "SLList[]");
    ss.str("");
    ss << SLList<std::string>{"","string",""};
    assert(ss.str() == "SLList[,string,]");
    ss.str("");
    ss << SLList<double>{3.14};
    assert(ss.str() == "SLList[3.14]");
    ss.str("");
    ss << SLList<int64_t>{-5,-1,0,1,5};
    assert(ss.str() == "SLList[-5,-1,0,1,5]");
}

void test_push_pop()
{
    SLList<float> a1;
    a1.push_front(5.1);
    assert(a1 == SLList<float>({5.1}));
    a1.push_back(5.2);
    assert(a1 == SLList<float>({5.1,5.2}));
    a1.push_back(5.3);
    assert(a1 == SLList<float>({5.1,5.2,5.3}));
    a1.push_back(5.4);
    SLList<float> a2({5.1,5.2,5.3,5.4});
    assert(a1 == a2);
    a1 = {};
    assert(a1.empty());
    a1.push_back(5.3);
    assert(a1 == SLList<float>({5.3}));
    a1.push_back(5.4);
    assert(a1 == SLList<float>({5.3,5.4}));
    a1.push_front(5.2);
    assert(a1 == SLList<float>({5.2,5.3,5.4}));
    a1.push_front(5.1);
    assert(a1 == a2);
    SLList<int> a3 = {7,12,-6};
    int a3i = a3.pop_front();
    assert(a3i == 7);
    assert(a3 == SLList<int>({12,-6}));
    a3.push_back(a3i);
    assert(a3 == SLList<int>({12,-6,7}));
    a3i = a3.pop_front();
    assert(a3i == 12);
    assert(a3 == SLList<int>({-6,7}));
    a3i = a3.pop_front();
    assert(a3i == -6);
    assert(a3 == SLList<int>(1,7));
    a3i = a3.pop_front();
    assert(a3i == 7);
    assert(a3.empty());
    a3 += 0;
    a3 += 1;
    a3 -= -1;
    a3 += 2;
    a3 -= -2;
    assert(a3 == SLList<int>({-2,-1,0,1,2}));
    SLList<int> a4 = {-5,-4,-3};
    a4 += a3;
    a4 += {3,4,5};
    assert(a4 == SLList<int>({-5,-4,-3,-2,-1,0,1,2,3,4,5}));
    SLList<int> a5;
    a5 += a4;
    assert(a5 == a4);
    a5.clear();
    assert(a5 == SLList<int>());
}

void test_rev()
{
    SLList<std::string> a1;
    a1.reverse();
    assert(a1 == SLList<std::string>());
    a1 = {"some string"};
    a1.reverse();
    assert(a1 == SLList<std::string>({"some string"}));
    a1 = {"some","string"};
    a1.reverse();
    assert(a1 == SLList<std::string>({"string","some"}));
    SLList<int> a2{-5,-4,-3,-2,-1,0,1,2,3,4,5};
    a2.reverse();
    assert(a2 == SLList<int>({5,4,3,2,1,0,-1,-2,-3,-4,-5}));
}

void test_func()
{
    auto a1 = SLList<int>::fromFunc(0,[](size_t i){return i;});
    assert(a1 == SLList<int>({}));
    a1 = SLList<int>::fromFunc(10,[](size_t i){return i%2==0 ? i/2 : -i/2;});
    assert(a1 == SLList<int>({0,-1,1,-2,2,-3,3,-4,4,-5}));
    auto a2 = SLList<std::string>::fromFunc(5,[](size_t i)
        {
            return std::to_string(i) + std::to_string(i) + std::to_string(i);
        });
    assert(a2 == SLList<std::string>({"000","111","222","333","444"}));
}

void test_sort()
{
    SLList<uint32_t> a1{};
    a1.sort();
    assert(a1 == SLList<uint32_t>({}));
    a1 = {1};
    a1.sort();
    assert(a1 == SLList<uint32_t>({1}));
    a1 = {1,2};
    a1.sort();
    assert(a1 == SLList<uint32_t>({1,2}));
    a1 = {2,1};
    a1.sort();
    assert(a1 == SLList<uint32_t>({1,2}));
    a1 = {103,102,101};
    a1.sort();
    assert(a1 == SLList<uint32_t>({101,102,103}));
    a1 = {611,723,125,216,84,80,401,999};
    a1.sort();
    assert(a1 == SLList<uint32_t>({80,84,125,216,401,611,723,999}));
    a1 = {3,14,8,7,11,6,12,10,19,17,16,18,9,2,1,15,5,4,13,20};
    a1.sort();
    uint32_t a1i = 0;
    for (auto i : a1)
        assert(i == ++a1i);
    // stable sort test
    auto tenscomp = [](uint32_t a, uint32_t b){return a/10 < b/10;};
    SLList<int> b1 = {10,12,11,22,28,24,20,26,31,39};
    SLList<int> b2 = {22,10,31,28,24,39,12,20,11,26};
    b2.sort(tenscomp);
    assert(b1 == b2);
    SLList<std::string> b3 = {"art","ant","apple","bats","bat","bark","center","coat","curve"};
    SLList<std::string> b4 = {"art","center","bats","coat","ant","curve","apple","bat","bark"};
    b4.sort([](const std::string& a, const std::string& b)
    {
        return a[0] < b[0]; // compare first letter only
    });
    assert(b3 == b4);
    // primitive root (42) test (mod 1103)
    a1 = {};
    a1i = 1;
    for (uint32_t i = 1; i < 1103; ++i)
    {
        a1i = (a1i*42) % 1103;
        a1.push_back(a1i);
    }
    SLList<uint32_t> a2 = a1;
    a1.sort();
    a2.sort([](uint32_t a, uint32_t b){return a > b;});
    auto iter1 = a1.begin(), iter2 = a2.begin();
    for (uint32_t i = 1; i < 1103; ++i)
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
    SLList<std::string> a1;
    auto a1iter = a1.begin();
    assert_throw(*a1iter);
    a1iter = a1.insert(a1.begin(),"last");
    assert(*a1iter == "last");
    assert(a1iter == a1.begin());
    a1iter = a1.insert(a1.begin(),"middle");
    assert(*a1iter == "middle");
    assert(a1iter == a1.begin());
    a1iter = a1.insert(a1.begin(),"first");
    assert(*a1iter == "first");
    assert(a1iter == a1.begin());
    assert(a1 == SLList<std::string>({"first","middle","last"}));
    assert_throw(a1.erase(a1.end()));
    assert(a1 == SLList<std::string>({"first","middle","last"}));
    a1iter = a1.begin();
    ++a1iter;
    ++a1iter;
    assert(*a1iter == "last");
    a1iter = a1.erase(a1iter);
    assert(a1iter == a1.end());
    assert_throw(++a1iter);
    assert_throw(a1iter++);
    assert(a1 == SLList<std::string>({"first","middle"}));
    a1iter = a1.erase(a1.begin());
    assert(*a1iter == "middle");
    assert(a1 == SLList<std::string>({"middle"}));
    a1iter = a1.erase(a1.begin());
    assert_throw(*a1iter);
    assert(a1.empty());
    assert(a1 == SLList<std::string>({}));
    SLList<uint32_t> a2{0,2,4,6,10};
    auto a2iter = a2.begin();
    while (a2iter != a2.end() && *a2iter < 4)
        ++a2iter;
    assert(a2iter != a2.end() && *a2iter == 4);
    a2iter = a2.insert(a2iter,3);
    assert(*a2iter == 3);
    ++a2iter;
    ++a2iter;
    assert(*a2iter == 6);
    a2iter = a2.insert(a2iter,5);
    assert(*a2iter == 5);
    assert(a2 == SLList<uint32_t>({0,2,3,4,5,6,10}));
    a2.insert(a2.end(),11);
    a2.insert(a2.begin(),0);
    assert(a2 == SLList<uint32_t>({0,0,2,3,4,5,6,10,11}));
    a2iter = a2.begin();
    ++a2iter;
    a2iter = a2.erase(a2iter);
    assert(*a2iter == 2);
    assert(a2 == SLList<uint32_t>({0,2,3,4,5,6,10,11}));
    assert_throw(a2.erase(a2.end()));
    a2iter = a2.begin();
    for (;;)
    {
        auto tmp = a2iter;
        ++tmp;
        if (tmp == a2.end())
            break;
        else
            a2iter = tmp;
    }
    assert(*a2iter == 11);
    a2iter = a2.erase(a2iter);
    assert(a2iter == a2.end());
    assert(a2 == SLList<uint32_t>({0,2,3,4,5,6,10}));
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
