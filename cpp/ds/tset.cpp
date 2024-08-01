/*
TSet<T> - binary search tree set
- on average supports efficient search, insertion, removal
- maintains sorted order at all times
- basic binary search tree, no automatic balancing done
- iteration is cyclic
- requires that operator< is defined for T

Interface (instances):

Test command:
g++ -g -Wall -Wextra -Werror -std=c++11 tset.cpp && valgrind --leak-check=full --track-origins=yes ./a.out
*/

#include <exception>
#include <functional>
#include <initializer_list>
#include <iostream>
#include <string>

#define CHECK_THROW(expr) (static_cast<bool>(expr) ? void(0) : \
throw std::runtime_error(std::string(#expr) + " FILE=" \
+ std::string(__FILE__) + " LINE=" +  std::to_string(__LINE__)))

// less than operator for default comparator
template <typename T, typename U>
bool operatorLess(T a, U b)
{
    return a < b;
}

template <typename T, bool (*_comp)(const T&,const T&) = operatorLess<const T&,const T&>>
class TSet
{
private:
    // tree node
    struct _node
    {
        // value stored
        T _val;
        // pointers to parent and children
        _node *_par, *_left, *_right;
        inline _node(const T& val = T(), _node *par = nullptr, _node *left = nullptr, _node *right = nullptr) noexcept:
            _val(val), _par(par), _left(left), _right(right) {}
        inline _node(T&& val = T(), _node *par = nullptr, _node *left = nullptr, _node *right = nullptr) noexcept:
            _val(val), _par(par), _left(left), _right(right) {}
    };
    // helper function for iterator increment
    static inline _node *_inc(_node *n, _node *r)
    {
        if (!n) // go to begin
        {
            if (r)
                while (r->_left)
                    r = r->_left;
            return r;
        }
        else if (n->_right) // to min in right subtree
        {
            n = n->_right;
            while (n->_left)
                n = n->_left;
        }
        else // up along right edge of subtree
        {
            while (n->_par && n->_par->_right == n)
                n = n->_par;
            n = n->_par;
        }
        return n;
    }
    // helper function for iterator decrement
    static inline _node *_dec(_node *n, _node *r)
    {
        if (!n) // go to end
        {
            if (r)
                while (r->_right)
                    r = r->_right;
            return r;
        }
        else if (n->_left) // to max in left subtree
        {
            n = n->_left;
            while (n->_right)
                n = n->_right;
        }
        else // up along left edge of subtree
        {
            while (n->_par && n->_par->_left == n)
                n = n->_par;
            n = n->_par;
        }
        return n;
    }
    // iterator
    struct _iter
    {
        // pointer to tree node
        _node *_ptr;
        // access to set object
        TSet<T> *_set;
        inline _iter(_node *ptr, TSet<T> *set) noexcept: _ptr(ptr), _set(set) {}
        inline T& operator*() { CHECK_THROW(_ptr); return _ptr->_val; }
        inline const T& operator*() const { CHECK_THROW(_ptr); return _ptr->_val; }
        inline T& operator->() { CHECK_THROW(_ptr); return _ptr->_val; }
        inline const T& operator->() const { CHECK_THROW(_ptr); return _ptr->_val; }
        inline _iter& operator++() { _ptr = _inc(_ptr,_set->_root); return *this; } // pre
        inline _iter& operator--() { _ptr = _dec(_ptr,_set->_root); return *this; } // pre
        inline _iter operator++(int) { _iter ret = *this; ++(*this); return ret; } // post
        inline _iter operator--(int) { _iter ret = *this; ++(*this); return ret; } // post
        inline bool operator==(const _iter& i) const { return _ptr == i._ptr; }
        inline bool operator!=(const _iter& i) const { return _ptr != i._ptr; }
        inline operator bool() const { return _ptr; }
    };
    // const iterator
    struct _citer
    {
        // pointer to tree node
        _node *_ptr;
        // access to set object
        TSet<T> *_set;
        inline _citer(_node *ptr, TSet<T> *set) noexcept: _ptr(ptr), _set(set) {}
        inline const T& operator*() const { CHECK_THROW(_ptr); return _ptr->_val; }
        inline const T& operator->() const { CHECK_THROW(_ptr); return _ptr->_val; }
        inline _citer& operator++() { _ptr = _inc(_ptr,_set->_root); return *this; } // pre
        inline _citer& operator--() { _ptr = _dec(_ptr,_set->_root); return *this; } // pre
        inline _citer operator++(int) { _citer ret = *this; ++(*this); return ret; } // post
        inline _citer operator--(int) { _citer ret = *this; ++(*this); return ret; } // pre
        inline bool operator==(const _citer& i) const { return _ptr == i._ptr; }
        inline bool operator!=(const _citer& i) const { return _ptr != i._ptr; }
        inline operator bool() const { return _ptr; }
    };
    // pointer to root onde
    _node *_root;
    // number of nodes in tree
    size_t _size;
    // delete all nodes given a root
    inline void _delete_tree(_node *r)
    {
        if (!r) return;
        _delete_tree(r->_left);
        _delete_tree(r->_right);
        delete r;
    }
    // duplicate tree, return pointer to root
    inline _node *_copy_tree(_node *n, _node *par = nullptr)
    {
        if (n)
        {
            _node *ret = new _node(n->_val,par);
            ret->_left = _copy_tree(n->_left,ret);
            ret->_right = _copy_tree(n->_right,ret);
            return ret;
        }
        return nullptr;
    }
    // make tree from sorted bidirectional iterator range without random access
    template <typename ITER>
    inline _node *_make_tree(ITER begin, ITER end, _node *par = nullptr)
    {
        if (begin == end) return nullptr;
        ITER m1 = begin, m2 = end;
        for (;;)
        {
            if (--m2 == m1) break;
            if (++m1 == m2) break;
        }
        _node *ret = new _node(std::move(*m1));
        ++m2;
        ret->_left = _make_tree(begin,m1,ret);
        ret->_right = _make_tree(m2,end,ret);
        return ret;
    }
    // make a tree from sorted array and index range [lo,hi)
    inline _node *_make_tree(T *arr, size_t lo, size_t hi, _node *par = nullptr)
    {
        if (lo == hi) return nullptr;
        size_t mid = (lo+hi)/2;
        _node *ret = new _node(std::move(arr[mid]),par);
        ret->_left = _make_tree(arr,lo,mid,ret);
        ret->_right = _make_tree(arr,mid+1,hi,ret);
        return ret;
    }
    // rebalance the tree
    inline void _rebalance()
    {
        if (_size == 0) return;
        T *tmp = new T[_size];
        size_t i = 0;
        for (T&& val : *this)
            tmp[i++] = val;
        _root = _make_tree(tmp,0,_size);
        delete[] tmp;
    }
    // erase a node from the tree (must be valid node)
    template <bool _use_right = false>
    inline void _erase(_node *n)
    {
        _node *p = n->_par;
        if (!n->_left) // no left subtree, adjust pointers to remove n
        {
            if (n->_right)
                n->_right->_par = p;
            if (p)
            {
                if (p->_left == n)
                    p->_left = n->_right;
                else
                    p->_right = n->_right;
            }
            else // n was root
                _root = n->_right;
        }
        else if (!n->_right) // only has left subtree (and is nonempty)
        {
            n->_left->_par = p;
            if (p)
            {
                if (p->_left == n)
                    p->_left = n->_left;
                else
                    p->_right = n->_left;
            }
            else // n was root
                _root = n->_left;
        }
        else // both subtrees nonempty
        {
            _node *m;
            if (_use_right)
            {
                // find replacement value in right subtree
                m = n->_right;
                while (m->_left)
                    m = m->_left;
                // adjust pointers to remove m
                if (m->_par == n)
                    n->_right = m->_right;
                else
                    m->_par->_left = m->_right;
                if (m->_right)
                    m->_right->_par = m->_par;
            }
            else
            {
                // find replacement value in left subtree
                m = n->_left;
                while (m->_right)
                    m = m->_right;
                // adjust pointers to remove m
                if (m->_par == n)
                    n->_left = m->_left;
                else
                    m->_par->_right = m->_left;
                if (m->_left)
                    m->_left->_par = m->_par;
            }
            // replace n with m in tree
            m->_par = p;
            m->_left = n->_left;
            m->_right = n->_right;
            n->_left->_par = m;
            n->_right->_par = m;
            if (p)
            {
                if (p->_left == n)
                    p->_left = m;
                else
                    p->_right = m;
            }
            else // n was root
                _root = m;
        }
        delete n;
        --_size;
    }
    // check if is subset
    inline bool _subset(const TSet<T>& set) const
    {
        if ((_size < 16 && _size*_size >= set._size) || _size > set._size/16)
        {
            // pass over all (better if *this is almost as big as set)
            auto itr1 = begin(), itr2 = set.begin();
            while (itr1 != end())
            {
                while (itr2 != set.end() && _comp(*itr2,*itr1))
                    ++itr2;
                if (itr2 == set.end() || _comp(*itr1,*itr2))
                    return false;
                ++itr1;
            }
        }
        else
        {
            // search individually (better if *this is very small)
            for (const T& val : *this)
                if (!set.contains(val))
                    return false;
        }
        return true;
    }
    // swap with other
    inline void _swap(TSet<T>& set) noexcept
    {
        std::swap(_root,set._root);
        std::swap(_size,set._size);
    }
public:
    // iterator
    typedef _iter itr_t;
    // const iterator
    typedef _citer citr_t;
    // default constructor (empty)
    TSet() noexcept: _root(nullptr), _size(0) {}
    // destructor
    ~TSet() { _delete_tree(_root); _root = nullptr; }
    // initializer list
    TSet(std::initializer_list<T> vals)
    {
        _root = _make_tree(vals.begin(),vals.end());
        _size = vals.size();
    }
    // copy constructor
    TSet(const TSet<T>& set)
    {
        _root = _copy_tree(set._root);
        _size = set._size;
    }
    // move constructor
    TSet(TSet<T>&& set) noexcept: TSet() { _swap(set); }
    // copy assignment
    TSet<T>& operator=(const TSet<T>& set) { TSet<T> tmp(set); _swap(tmp); return *this; }
    // move assignment
    TSet<T>& operator=(TSet<T>&& set) noexcept { _swap(set); return *this; }
    // begin iterator
    inline itr_t begin() noexcept { return ++_iter(nullptr,this); }
    // begin const iterator
    inline citr_t begin() const noexcept { return ++_citer(nullptr,this); }
    // end iterator
    inline itr_t end() noexcept { return _iter(nullptr,this); }
    // end const iterator
    inline citr_t end() const noexcept { return _citer(nullptr,this); }
    // size of set
    inline size_t size() const noexcept { return _size; }
    // is set empty
    inline bool empty() const noexcept { return _size == 0; }
    // set equality
    inline bool operator==(const TSet<T>& set) const
    {
        if (_size != set._size) return false;
        auto itr1 = begin(), itr2 = set.begin();
        while (itr1 != end())
        {
            if (*itr1 != *itr2)
                return false;
            ++itr1, ++itr2;
        }
        return true;
    }
    // sets not equal
    inline bool operator!=(const TSet<T>& set) const { return !(*this == set); }
    // proper subset
    inline bool operator<(const TSet<T>& set) const
    { return _size < set._size && _subset(set); }
    // prpoer superset
    inline bool operator>(const TSet<T>& set) const { return set < *this; }
    // subset
    inline bool operator<=(const TSet<T>& set) const
    { return _size <= set._size && _subset(set); }
    // superset
    inline bool operator>=(const TSet<T>& set) const { return set <= *this; }
    // clear contents
    void clear() { _delete_tree(_root); _root = nullptr; _size = 0; }
    // insert into set, returns iterator to it and true if it was inserted
    inline std::pair<itr_t,bool> insert(const T& val)
    {
        T tmp = val;
        return insert(std::move(tmp));
    }
    // insert into set, returns iterator to it and true if it was inserted
    inline std::pair<itr_t,bool> insert(T&& val)
    {
        if (!_root)
        {
            _root = new _node(val);
            ++_size;
            return {_iter(_root,this),true};
        }
        else
        {
            _node *n = _root;
            for (;;)
            {
                if (_comp(val,n->_val))
                {
                    if (n->_left) n = n->_left;
                    else
                    {
                        n->_left = new _node(val,n);
                        ++_size;
                        return {_iter(n->_left,this),true};
                    }
                }
                else if (_comp(n->_val,val))
                {
                    if (n->_right) n = n->_right;
                    else
                    {
                        n->_right = new _node(val,n);
                        ++_size;
                        return {_iter(n->_right,this),true};
                    }
                }
                else
                    return {_iter(n,this),false};
            }
        }
    }
    // erase from set, returns false if element did not exist
    inline bool erase(const T& val)
    {
        itr_t itr = find(val);
        if (itr == end()) return false;
        _erase(itr._ptr);
        return true;
    }
    // erase from set, return iterator to next element
    inline itr_t erase(itr_t itr)
    {
        CHECK_THROW(itr != end());
        _node *n = itr._ptr;
        ++itr;
        _erase(n);
        return itr;
    }
    // check if set contains element
    inline bool contains(const T& val) const { return find(val) != end(); }
    // return iterator if element is found, end iterator if not contained
    inline itr_t find(const T& val)
    {
        _node *n = _root;
        while (n)
        {
            if (_comp(val,n->_val))
                n = n->_left;
            else if (_comp(n->_val,val))
                n = n->_right;
            else
                return _iter(n,this);
        }
        return _iter(nullptr,this);
    }
    // return iterator if element is found, end iterator if not contained
    inline citr_t find(const T& val) const
    {
        _node *n = _root;
        while (n)
        {
            if (_comp(val,n->_val))
                n = n->_left;
            else if (_comp(n->_val,val))
                n = n->_right;
            else
                return _citer(n,this);
        }
        return _citer(nullptr,this);
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
    ;
}

int main()
{
    test_ctor();
}
