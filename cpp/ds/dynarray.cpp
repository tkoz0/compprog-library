/*
DynArray<T> - mutable dynamically resizable array
- stores items as contiguous block of memory
- good for arrays that grow, fast amortized append
- good for applications requiring fast access
- similar to std::vector
- default growth factor is 1.125

Interface (instances):
DynArray() - empty array, no allocated space
DynArray(<siz>[,val=default])
- length <siz> array filled with val, exact space allocated
DynArray({val0,val1,...}) - initializer list, exact space allocated
begin() - begin iterator (pointer)
end() - end iterator (pointer)
ptr() - pointer to data array
size() - length of data stored
alloc() - length of array allocated
empty() - is array length 0
full() - is all the allocated space used
== and != - arrays equal if lengths and corresponding elements are equal
[<index>] - access by index in range [-size,size)
reverse() - in place reverse order of array
<array> + <array> - concatenate arrays, exact space allocated
<array>*<integer> or <integer>*<array> - repeated array, exact space allocated
slice(beg,end[,step=1])
- new array from beg,beg+step,... (not including end)
- negative beg,end are converted to 0-indexing
sliceFirst(n) - first n elements, error if n < 0, entire array if n > size
sliceLast(n) - last n elements, error if n < 0, entire array if n > size
sort([comp]) - in place sort
stableSort([comp]) - in place stable sort
push(val) - append to end of array, growing if necessary
pop() - remove and return the last element, error if array is empty
clear() - deletes everything in the array and deallocates the memory
shrink() - removes extra space, resizing allocated space to exactly fit
realloc(siz) - change allocated space, size decreases if param is smaller
resize(siz[,val=default])
- change length, filling new spaces with val if increasing length
- realloc occurs only if necessary
+=<val> - append val, same as push(val)
+=<array> - concatenate array to end
insert(i,val) - insert at index i, shifting to right, appends if i=size
erase(i) - remove and return value at index i, shifts to left

Interface (static):
fromFunc(n,func) - creates array from [func(0),func(1),...,func(n-1)]

Test command:
g++ -g -Wall -Wextra -Werror -std=c++11 dynarray.cpp && valgrind --leak-check=full --track-origins=yes ./a.out
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

// a resizing function for growing array length exponentially
// uses an approximate growth ratio of n/d
template <size_t n, size_t d>
size_t resizerRatio(size_t l)
{
    static_assert(n >= d && d > 0);
    return ((1+l)*n)/d;
}

template <typename T, size_t (*_resizer)(size_t) = resizerRatio<9,8>>
class DynArray
{
private:
    T *_arr;
    size_t _len, _alloc;
    // grow to larger size, need _alloc_new > _alloc
    inline void _grow(size_t _alloc_new)
    {
        CHECK_THROW(_alloc_new > _alloc);
        T *_arr_new = new T[_alloc_new];
        std::move(_arr,_arr+_len,_arr_new);
        delete[] _arr;
        _arr = _arr_new;
        _alloc = _alloc_new;
    }
    // default grow to larger size, uses _resizer
    inline void _grow() { _grow(_resizer(_alloc)); }
    // resize allocated space to exact length
    // array value does not change unless param is smaller than size
    inline void _resize(size_t _alloc_new)
    {
        if (_alloc_new == 0) // clear contents
        {
            delete[] _arr;
            _arr = nullptr;
            _len = _alloc = 0;
        }
        else if (_alloc_new < _alloc) // must shrink
        {
            _len = std::min(_len,_alloc_new);
            T *_arr_new = new T[_alloc_new];
            std::move(_arr,_arr+_len,_arr_new);
            delete[] _arr;
            _arr = _arr_new;
            _alloc = _alloc_new;
        }
        else if (_alloc_new > _alloc) // must grow
            _grow(_alloc_new);
    }
public:
    typedef T *itr_t;
    typedef const T *citr_t;
    DynArray() noexcept: _arr(nullptr), _len(0), _alloc(0) {}
    ~DynArray()
    {
        delete[] _arr;
        _arr = nullptr;
    }
    DynArray(int64_t siz, const T& val = T())
    {
        CHECK_THROW(siz >= 0);
        CHECK_THROW(siz < (1LL << 48));
        _arr = new T[siz];
        _len = _alloc = siz;
        std::fill(_arr,_arr+_len,val);
    }
    DynArray(std::initializer_list<T> vals)
    {
        _arr = new T[vals.size()];
        _len = _alloc = vals.size();
        std::copy(vals.begin(),vals.end(),_arr);
    }
    DynArray(const DynArray<T>& arr)
    {
        _arr = new T[arr._len];
        _len = _alloc = arr._len;
        std::copy(arr._arr,arr._arr+_len,_arr);
    }
    DynArray(DynArray<T>&& arr) noexcept
    {
        _arr = arr._arr;
        _len = arr._len;
        _alloc = arr._alloc;
        arr._arr = nullptr;
    }
    DynArray<T>& operator=(const DynArray<T>& arr)
    {
        delete[] _arr;
        _arr = new T[arr._len];
        _len = _alloc = arr._len;
        std::copy(arr._arr,arr._arr+_len,_arr);
        return *this;
    }
    DynArray<T>& operator=(DynArray<T>&& arr)
    {
        delete[] _arr;
        _arr = arr._arr;
        _len = arr._len;
        _alloc = arr._alloc;
        arr._arr = nullptr;
        return *this;
    }
    inline itr_t begin() noexcept { return _arr; }
    inline citr_t begin() const noexcept { return _arr; }
    inline itr_t end() noexcept { return _arr + _len; }
    inline citr_t end() const noexcept { return _arr + _len; }
    inline T *ptr() noexcept { return _arr; }
    inline const T *ptr() const noexcept { return _arr; }
    inline size_t size() const noexcept { return _len; }
    inline size_t alloc() const noexcept { return _alloc; }
    // is length 0
    inline bool empty() const noexcept { return _len == 0; }
    // is all the allocated space used
    inline bool full() const noexcept { return _len == _alloc; }
    inline bool operator==(const DynArray<T>& arr)
    {
        if (_len != arr._len)
            return false;
        for (size_t i = 0; i < _len; ++i)
            if (_arr[i] != arr._arr[i])
                return false;
        return true;
    }
    inline bool operator!=(const DynArray<T>& arr) { return !(*this == arr); }
    inline T& operator[](int64_t i)
    {
        CHECK_THROW(i < (int64_t)_len && i >= -(int64_t)_len);
        return i >= 0 ? _arr[i] : _arr[_len + i];
    }
    inline const T& operator[](int64_t i) const
    {
        CHECK_THROW(i < (int64_t)_len && i >= -(int64_t)_len);
        return i >= 0 ? _arr[i] : _arr[_len + i];
    }
    void reverse() { std::reverse(begin(),end()); }
    // concatenate (makes allocated space exact size)
    friend DynArray<T> operator+(const DynArray<T>& arr1, const DynArray<T>& arr2)
    {
        DynArray<T> ret(arr1.size() + arr2.size());
        std::copy(arr1.begin(),arr1.end(),ret.begin());
        std::copy(arr2.begin(),arr2.end(),ret.begin()+arr1.size());
        return ret;
    }
    // repeated array (exact space allocated)
    friend DynArray<T> operator*(const DynArray<T>& arr, int64_t n)
    {
        CHECK_THROW(n >= 0);
        DynArray<T> ret(arr.size() * n);
        auto p = ret.begin();
        while (n--)
        {
            std::copy(arr.begin(),arr.end(),p);
            p += arr.size();
        }
        return ret;
    }
    // repeated array (exact space allocated)
    friend inline DynArray<T> operator*(int64_t n, const DynArray<T>& arr) { return arr * n; }
    friend std::ostream& operator<<(std::ostream& os, const DynArray<T>& arr)
    {
        os << "DynArray[";
        if (arr.size() > 0)
        {
            os << arr[0];
            for (size_t i = 1; i < arr.size(); ++i)
                os << "," << arr[i];
        }
        os << "]";
        return os;
    }
    // elements at indexes beg,beg+step,... in range [beg,end)
    // step must be positive
    // (after converting negative indexes if necessary)
    DynArray<T> slice(int64_t beg, int64_t end, int64_t step = 1) const
    {
        CHECK_THROW(step >= 1);
        beg = beg >= 0 ? beg : _len + beg;
        end = end >= 0 ? end : _len + end;
        if (beg < 0) beg = 0;
        if (end > (int64_t)_len) end = _len;
        DynArray<T> ret((end - beg + (step-1)) / step);
        T *p = ret._arr;
        while (beg < end)
        {
            *(p++) = _arr[beg];
            beg += step;
        }
        return ret;
    }
    // first n elements, or all if n >= size, error if negative
    inline DynArray<T> sliceFirst(int64_t n) const
    {
        CHECK_THROW(n >= 0);
        return slice(0,n);
    }
    // last n elements, or all if n >= size, error if negative
    inline DynArray<T> sliceLast(int64_t n) const
    {
        CHECK_THROW(n >= 0);
        return slice(std::max((int64_t)0,(int64_t)_len-n),_len);
    }
    void sort() { std::sort(begin(),end()); }
    template <typename F>
    void sort(F comp) { std::sort(begin(),end(),comp); }
    void stableSort() { std::stable_sort(begin(),end()); }
    template <typename F>
    void stableSort(F comp) { std::stable_sort(begin(),end(),comp); }
    // array from func(0),func(1),...,func(n-1)
    static DynArray<T> fromFunc(size_t n, std::function<T(size_t)> func)
    {
        DynArray<T> ret(n);
        for (size_t i = 0; i < n; ++i)
            ret._arr[i] = func(i);
        return ret;
    }
    // append to end
    inline void push(const T& val)
    {
        if (_len == _alloc) _grow();
        _arr[_len++] = val;
    }
    // append to end
    inline void push(T&& val)
    {
        if (_len == _alloc) _grow();
        _arr[_len++] = val;
    }
    // remove from end
    inline T pop()
    {
        CHECK_THROW(_len > 0);
        return std::move(_arr[--_len]);
    }
    // empty container
    void clear() { _resize(0); }
    // remove extra space to save memory
    void shrink() { _resize(_len); }
    // resize the allocated space
    // size changes if param is smaller than size
    void realloc(int64_t siz)
    {
        CHECK_THROW(siz >= 0);
        _resize(siz);
    }
    // change the length of the array, fill new spaces with val
    // realloc occurs only if bigger than current alloc size
    void resize(int64_t siz, const T& val = T())
    {
        CHECK_THROW(siz >= 0);
        if (siz < (int64_t)_len)
        {
            while ((int64_t)_len > siz)
                _arr[--_len].~T();
        }
        else
        {
            if (siz > (int64_t)_alloc)
                _resize(siz);
            while ((int64_t)_len < siz)
                _arr[_len++] = val;
        }
    }
    // append to end
    inline DynArray<T>& operator+=(const T& val) { push(val); return *this; }
    // append to end
    inline DynArray<T>& operator+=(T&& val) { push(val); return *this; }
    // append array to end
    inline DynArray<T>& operator+=(const DynArray<T>& arr)
    {
        size_t _len_new = _len + arr._len;
        size_t _alloc_new = _alloc;
        while (_alloc_new < _len_new)
            _alloc_new = _resizer(_alloc_new);
        if (_alloc_new > _alloc)
            _grow(_alloc_new);
        std::copy(arr.begin(),arr.end(),_arr+_len);
        _len = _len_new;
        return *this;
    }
    // append array to end
    inline DynArray<T>& operator+=(DynArray<T>&& arr)
    {
        size_t _len_new = _len + arr._len;
        size_t _alloc_new = _alloc;
        while (_alloc_new < _len_new)
            _alloc_new = _resizer(_alloc_new);
        if (_alloc_new > _alloc)
            _grow(_alloc_new);
        std::move(arr.begin(),arr.end(),_arr+_len);
        _len = _len_new;
        return *this;
    }
    // insert element at position
    inline void insert(int64_t i, const T& val)
    {
        CHECK_THROW(i >= -(int64_t)_len && i <= (int64_t)_len);
        size_t j = i >= 0 ? i : _len + i;
        if (_len == _alloc) _grow();
        size_t k = _len++;
        while (k > j) // shift right
        {
            _arr[k] = std::move(_arr[k-1]);
            --k;
        }
        _arr[k] = val;
    }
    // insert element at position
    inline void insert(int64_t i, T&& val)
    {
        CHECK_THROW(i >= -(int64_t)_len && i <= (int64_t)_len);
        size_t j = i >= 0 ? i : _len + i;
        if (_len == _alloc) _grow();
        size_t k = _len++;
        while (k > j) // shift right
        {
            _arr[k] = std::move(_arr[k-1]);
            --k;
        }
        _arr[k] = val;
    }
    // erase an element
    inline T erase(int64_t i)
    {
        CHECK_THROW(i >= -(int64_t)_len && i < (int64_t)_len);
        size_t j = i >= 0 ? i : _len + i;
        T ret = std::move(_arr[j]);
        --_len;
        while (j < _len) // shift left
        {
            _arr[j] = std::move(_arr[j+1]);
            ++j;
        }
        return ret;
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
    DynArray<int> a1;
    assert(a1.size() == 0);
    assert(DynArray<std::string>().empty());
    // size
    DynArray<int> a2(0,64);
    assert(a2 == a1);
    DynArray<double> a3(5,1.3);
    assert(a3.size() == 5);
    assert(!a3.empty());
    assert_throw(DynArray<int>(-1));
    assert_throw(DynArray<float>(-1,-1.0));
    // initializer list
    DynArray<std::string> b1({"these","are","words"});
    DynArray<float> b2{1.1,1.2,1.3,1.4};
    DynArray<double> b3{1.3,1.3,1.3,1.3,1.3};
    DynArray<DynArray<char>> b4{{'a'},{'a','b'},{'a','b','c'}};
    assert(b1.size() == 3);
    assert(b2.size() == 4);
    assert(b3 == a3);
    assert(b4.size() == 3);
    // copy
    auto a4(a2);
    auto a5(a3);
    assert(a4 == a2);
    assert(a5 == a3);
    // move
    auto c1(DynArray<float>{1.1,1.2,1.3,1.4});
    assert(c1 == b2);
    auto c2(DynArray<std::string>(0,"abc"));
    assert(c2 == DynArray<std::string>());
    // = copy
    DynArray<double> c3{1,2,3};
    c3 = a3;
    assert(c3 == a3);
    DynArray<std::string> c4 = b1;
    assert(c4 == b1);
    a4 = a2;
    assert(a4 == a2);
    // = move
    auto c5 = DynArray<std::string>{"here","are","some","more","words"};
    auto c6 = DynArray<short>(10,25);
    assert(c5 == DynArray<std::string>({"here","are","some","more","words"}));
    assert(c6.size() == 10);
    assert(c6 == DynArray<short>({25,25,25,25,25,25,25,25,25,25}));
    c5 = DynArray<std::string>(2,"repeat");
    assert(c5 == DynArray<std::string>({"repeat","repeat"}));
}

void test_comp()
{
    DynArray<float> a1{};
    DynArray<std::string> a2{};
    assert(a1 == DynArray<float>());
    assert(a2 == DynArray<std::string>(0,"string"));
    DynArray<double> a3{7.1,7.2,7.3};
    assert(a3 != DynArray<double>());
    assert(a3 != DynArray<double>({7.1,7.2}));
    assert(a3 == DynArray<double>({7.1,7.2,7.3}));
    assert(a3 != DynArray<double>({7.1,6.9,7.3}));
    assert(a3 != DynArray<double>({7.1,7.2,6.9}));
    assert(a3 != DynArray<double>({7.1,7.2,7.3,7.4}));
    a2 = {"s1","s2","s3","s4","s5","s6"};
    assert(a2 != DynArray<std::string>({"s1","s2","s3","s4","s5"}));
    assert(a2 == DynArray<std::string>({"s1","s2","s3","s4","s5","s6"}));
    assert(a2 != DynArray<std::string>({"s1","s2","s4","s3","s5","s6"}));
    assert(a2 != DynArray<std::string>({"s1","s2","s3","s4","s5","s6","s7"}));
}

void test_iter()
{
    DynArray<float> a1{};
    for (auto f : a1) // nothing should happen for empty array
        (void)f, assert(0);
    DynArray<std::string> a2{"9000"};
    for (auto s : a2)
        assert(s == "9000");
    DynArray<int> a3{1,4,9,16,25};
    for (size_t i = 0; i < a3.size(); ++i)
        assert(a3[i] == (int)((i+1)*(i+1)));
    DynArray<std::string> a4{"aishia","yue","tohru"};
    auto a4it = a4.begin();
    assert(*a4it == "aishia");
    ++a4it;
    assert(*a4it == "yue");
    ++a4it;
    assert(*a4it == "tohru");
    ++a4it;
    assert(a4it == a4.end());
    --a4it;
    assert(*a4it == "tohru");
    --a4it;
    assert(*a4it == "yue");
    --a4it;
    assert(*a4it == "aishia");
    assert(a4it == a4.begin());
}

void test_subscript()
{
    DynArray<std::string> a1;
    assert_throw(a1[0]);
    assert_throw(a1[-1]);
    assert_throw(a1[1]);
    DynArray<float> a2{-2.4,-1.2,0.0,1.2,2.4};
    assert(a2[-5] == -a2[4]);
    assert(a2[-4] == -a2[3]);
    assert(a2[-3] == a2[2]);
    assert(&a2[-1] == &a2[4]);
    assert(&a2[-2] == &a2[3]);
    assert(&a2[-3] == &a2[2]);
    assert(&a2[-4] == &a2[1]);
    assert(&a2[-5] == &a2[0]);
    assert_throw(a2[-6]);
    assert_throw(a2[5]);
    assert_throw(a2[-7]);
    assert_throw(a2[6]);
    a2[-5] = 6.1;
    a2[1] = 6.2;
    a2[-1] = 6.5;
    assert(a2 == DynArray<float>({6.1,6.2,0.0,1.2,6.5}));
}

void test_rev()
{
    DynArray<int> a1;
    DynArray<int> a2;
    a2.reverse();
    assert(a1 == a2);
    DynArray<float> a3{1,2,3,4};
    DynArray<float> a4 = a3;
    a4.reverse();
    a4.reverse();
    assert(a3 == a4);
    a4.reverse();
    assert(a4 == DynArray<float>({4,3,2,1}));
    DynArray<std::string> a5(1,"no");
    DynArray<std::string> a6 = a5;
    a5.reverse();
    assert(a5 == a6);
    DynArray<char> a7 = {'1','2','3','4','5'};
    a7.reverse();
    assert(a7 == DynArray<char>({'5','4','3','2','1'}));
}

void test_plus()
{
    DynArray<int> a1(3,7);
    DynArray<int> a2(4,-1);
    assert(a1+a2 == DynArray<int>({7,7,7,-1,-1,-1,-1}));
    assert(DynArray<std::string>() + DynArray<std::string>() == DynArray<std::string>());
    assert(a1 + DynArray<int>() == a1);
    assert(DynArray<int>() + a2 == a2);
    DynArray<double> a3{-5,-6};
    DynArray<double> a4{17,18};
    assert(a3+a4 == DynArray<double>({-5,-6,17,18}));
}

void test_mult()
{
    DynArray<char> a1{};
    assert(a1*100 == DynArray<char>() && 1000*a1 == DynArray<char>());
    DynArray<int> a2{0,1,2};
    assert(a2*1 == a2 && 1*a2 == a2);
    assert(2*a2 == DynArray<int>({0,1,2,0,1,2}));
    assert(5*a2 == DynArray<int>({0,1,2,0,1,2,0,1,2,0,1,2,0,1,2}));
    assert(17*DynArray<double>(19,323.0) == DynArray<double>(323,323.0));
    assert(0*DynArray<char>(10,'a') == a1);
    assert_throw(-1 * a1);
    assert_throw(a1 * -2);
}

void test_print()
{
    std::stringstream ss;
    ss.str("");
    ss << DynArray<double>();
    assert(ss.str() == "DynArray[]");
    ss.str("");
    ss << DynArray<char>{'a','b','c','1','2','3'};
    assert(ss.str() == "DynArray[a,b,c,1,2,3]");
    ss.str("");
    ss << DynArray<int>{0,1,-1,2,-2,3,-3};
    assert(ss.str() == "DynArray[0,1,-1,2,-2,3,-3]");
    ss.str("");
    ss << DynArray<std::string>{"one",",","two"};
    assert(ss.str() == "DynArray[one,,,two]");
}

void test_slice()
{
    DynArray<int> a1{0,1,2,3,4,5,6,7,8,9};
    assert(a1.slice(0,3) == DynArray<int>({0,1,2}));
    assert(a1.slice(-3,-1) == DynArray<int>({7,8}));
    assert(a1.slice(7,15) == DynArray<int>({7,8,9}));
    assert(a1.slice(2,7) == DynArray<int>({2,3,4,5,6}));
    assert(a1.slice(2,15,3) == DynArray<int>({2,5,8}));
    assert(a1.slice(0,10,9) == DynArray<int>({0,9}));
    assert(a1.slice(5,7,3) == DynArray<int>({5}));
    assert(a1.slice(5,7,2) == DynArray<int>({5}));
    assert(a1.slice(0,a1.size()) == a1);
    assert_throw(a1.slice(0,10,0));
    assert_throw(a1.slice(-5,-3,-1));
    assert(a1.sliceFirst(20) == a1);
    assert(a1.sliceLast(21) == a1);
    assert(a1.sliceFirst(0) == DynArray<int>());
    assert(a1.sliceFirst(1) == DynArray<int>(1,0));
    assert(a1.sliceFirst(4) == DynArray<int>({0,1,2,3}));
    assert(a1.sliceFirst(9) == DynArray<int>({0,1,2,3,4,5,6,7,8}));
    assert(a1.sliceFirst(10) == a1);
    assert(a1.sliceLast(0) == DynArray<int>());
    assert(a1.sliceLast(1) == DynArray<int>(1,9));
    assert(a1.sliceLast(5) == DynArray<int>({5,6,7,8,9}));
    assert(a1.sliceLast(10) == a1);
    DynArray<std::string> a2;
    assert(a2.sliceFirst(0) == a2);
    assert(a2.sliceFirst(1) == a2);
    assert(a2.sliceLast(0) == a2);
    assert(a2.sliceLast(1) == a2);
    assert_throw(a2.sliceFirst(-1));
    assert_throw(a2.sliceLast(-1));
}

void test_sort()
{
    DynArray<float> a1{-1.5,-1.0,-0.001,0.5,3.14,42.0};
    DynArray<float> a2{42.0,-1.0,-1.5,3.14,-0.001,0.5};
    a2.sort();
    assert(a1 == a2);
    a1 = {-1.5,-1.0,-0.001,0.5,3.14,42.0};
    a2 = {42.0,-1.0,-1.5,3.14,-0.001,0.5};
    a2.sort([](float f1, float f2){return f1 > f2;});
    a1.reverse();
    assert(a1 == a2);
    DynArray<int> a3{10,12,11,22,28,24,20,26,31,39};
    DynArray<int> a4{22,10,31,28,24,39,12,20,11,26};
    a4.stableSort([](int a, int b){return a/10 < b/10;});
    assert(a3 == a4);
}

void test_func()
{
    auto a1 = DynArray<double>::fromFunc(5,[](size_t a){return 1.0/(a+1);});
    assert(a1 == DynArray<double>({1.0,0.5,1.0/3.0,0.25,0.2}));
    auto a2 = DynArray<int>::fromFunc(10,[](size_t i){return i*i;});
    assert(a2 == DynArray<int>({0,1,4,9,16,25,36,49,64,81}));
    auto a3 = DynArray<uint32_t>::fromFunc(8,[](size_t a){return a*a + 3*a + 6;});
    assert(a3 == DynArray<uint32_t>({6,10,16,24,34,46,60,76}));
    auto a4 = DynArray<bool>::fromFunc(6,[](size_t a){return a % 2 != 0;});
    assert(a4 == DynArray<bool>({0,1,0,1,0,1}));
    auto a5 = DynArray<bool>::fromFunc(a1.size(),[&a1](size_t i){return a1[i] < 0.5;});
    assert(a5 == DynArray<bool>({false,false,true,true,true}));
}

void test_push_pop()
{
    DynArray<DynArray<std::string>> a1;
    a1.push({});
    a1.push({});
    assert(a1.size() == 2);
    a1[0].push("1");
    a1[0].push("3");
    a1[1].push("no");
    assert(a1 == DynArray<DynArray<std::string>>({{"1","3"},{"no"}}));
    std::string s;
    s = a1[1].pop();
    assert(s == "no");
    assert_throw(a1[1].pop());
    s = a1[0].pop();
    assert(s == "3");
    s = a1[0].pop();
    assert(s == "1");
    assert_throw(a1[0].pop());
    DynArray<std::string> a2;
    a2 = a1.pop();
    assert(a2 == DynArray<std::string>());
    a2 = a1.pop();
    assert(a2 == DynArray<std::string>());
    assert_throw(a1.pop());
    DynArray<int> a3;
    for (int i = 0; i < 100; ++i)
        a3 += i;
    assert(a3.size() == 100);
    assert(a3.alloc() >= a3.size());
    size_t a3a = a3.alloc();
    for (int i = 0; i < 50; ++i)
    {
        int p = a3.pop();
        assert(p == 99-i);
    }
    assert(a3.size() == 50);
    assert(a3.alloc() == a3a);
}

void test_size_stuff()
{
    DynArray<float> a1;
    assert(a1.size() == 0);
    assert(a1.alloc() == 0);
    assert(a1.empty());
    assert(a1.full());
    for (int i = 0; i < 100; ++i)
    {
        a1 += i/4.0;
        assert(a1.size() == (size_t)(i+1));
        assert(a1.alloc() >= a1.size());
    }
    size_t a1a = a1.alloc();
    for (int i = 0; i < 50; ++i)
        a1.pop();
    assert(a1.size() == 50);
    assert(a1.alloc() == a1a);
    a1.shrink();
    assert(a1.size() == 50);
    assert(a1.alloc() == 50);
    a1.resize(25);
    assert(a1.size() == 25);
    assert(a1.alloc() == 50);
    a1.resize(50,-1);
    assert(a1.size() == 50);
    assert(a1.alloc() == 50);
    a1.resize(55,-2);
    assert(a1.size() == 55);
    assert(a1.alloc() == 55);
    for (int i = 0; i < 55; ++i)
    {
        if (i < 25)
            assert(a1[i] == i/4.0);
        else if (i < 50)
            assert(a1[i] == -1);
        else
            assert(a1[i] == -2);
    }
    a1.realloc(60);
    assert(a1.size() == 55);
    assert(a1.alloc() == 60);
    a1.realloc(50);
    assert(a1.size() == 50);
    assert(a1.alloc() == 50);
    a1.realloc(0);
    assert(a1.empty());
    assert(a1.alloc() == 0);
}

void test_insert_erase()
{
    DynArray<int> a1;
    a1.insert(0,3);
    a1.insert(0,5);
    a1.insert(0,7);
    assert(a1 == DynArray<int>({7,5,3}));
    a1.clear();
    a1.insert(0,3);
    a1.insert(1,5);
    a1.insert(2,7);
    assert_throw(a1.insert(4,11));
    assert_throw(a1.insert(-4,11));
    assert(a1 == DynArray<int>({3,5,7}));
    a1.insert(0,2);
    assert(a1 == DynArray<int>({2,3,5,7}));
    a1.insert(2,4);
    assert(a1 == DynArray<int>({2,3,4,5,7}));
    a1.insert(-1,6);
    assert(a1 == DynArray<int>({2,3,4,5,6,7}));
    int a1e;
    a1e = a1.erase(-5);
    assert(a1e == 3);
    assert(a1 == DynArray<int>({2,4,5,6,7}));
    a1e = a1.erase(2);
    assert(a1e == 5);
    assert(a1 == DynArray<int>({2,4,6,7}));
    a1e = a1.erase(-1);
    assert(a1e == 7);
    assert(a1 == DynArray<int>({2,4,6}));
}

int main()
{
    // these tests are (almost) copy pasted from FixArray
    test_ctor();
    test_comp();
    test_iter();
    test_subscript();
    test_rev();
    test_plus();
    test_mult();
    test_print();
    test_slice();
    test_sort();
    test_func();
    // tests for DynArray stuff that is not in FixArray
    test_push_pop();
    test_size_stuff();
    test_insert_erase();
}
