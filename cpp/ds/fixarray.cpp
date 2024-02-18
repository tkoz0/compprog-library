/*
FixArray<T> - mutable fixed length array
- stores items as a contiguous block of memory
- good for storing things with known size that don't grow/shrink
  - for example, an input of known length
- for practical purposes, using DynArray<T> instead should be fine

Interface (instances):
FixArray() - empty array
FixArray(<siz>[,val=default]) - length <siz> array filled with val
FixArray({val0,val1,...}) - initializer list constructor
begin() - begin iterator (pointer)
end() - end iterator (pointer)
ptr() - pointer to data array
size() - array length
empty() - is array length 0
== and != - arrays equal if lengths and corresponding elements are equal
[<index>] - access by index in range [-size,size)
<array> + <array> - concatenate 2 arrays
<array>*<integer> or <integer>*<array> - construct a repeating array
slice(beg,end[,step=1])
- new array with indexes beg,beg+step,... (not including end)
- if beg,end are negative, they are converted to 0-indexing first
sliceFirst(n)
- first n elements of list, entire list if n > size, error if n < 0
sliceLast(n)
- last n elements of list, entire list if n > size, error if n < 0
reverse() - in place reverse list order
sort([comp]) - in place sort
stableSort([comp]) - in place stable sort

Interface (static):
fromFunc(n,func) - creates the array [func(0),func(1),...,func(n-1)]

Test command:
g++ -g -Wall -Wextra -Werror -std=c++11 fixarray.cpp && valgrind --leak-check=full --track-origins=yes ./a.out
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
class FixArray
{
private:
    T *_arr;
    size_t _len;
public:
    typedef T *itr_t;
    typedef const T *citr_t;
    FixArray() noexcept: _arr(nullptr), _len(0) {}
    ~FixArray()
    {
        delete[] _arr;
        _arr = nullptr;
    }
    FixArray(int64_t siz, const T& val = T())
    {
        CHECK_THROW(siz >= 0);
        CHECK_THROW(siz < (1LL<<48));
        _arr = new T[siz];
        _len = siz;
        std::fill(_arr,_arr+_len,val);
    }
    FixArray(std::initializer_list<T> vals)
    {
        _arr = new T[vals.size()];
        _len = vals.size();
        std::copy(vals.begin(),vals.end(),_arr);
    }
    FixArray(const FixArray<T>& arr)
    {
        _arr = new T[arr._len];
        _len = arr._len;
        std::copy(arr.begin(),arr.end(),_arr);
    }
    FixArray(FixArray<T>&& arr) noexcept
    {
        _arr = arr._arr;
        _len = arr._len;
        arr._arr = nullptr;
    }
    FixArray<T>& operator=(const FixArray<T>& arr)
    {
        delete[] _arr;
        _arr = new T[arr._len];
        _len = arr._len;
        std::copy(arr.begin(),arr.end(),_arr);
        return *this;
    }
    FixArray<T>& operator=(FixArray<T>&& arr)
    {
        delete[] _arr;
        _arr = arr._arr;
        _len = arr._len;
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
    // is length 0
    inline bool empty() const noexcept { return _len == 0; }
    inline bool operator==(const FixArray<T>& arr)
    {
        if (_len != arr._len)
            return false;
        for (size_t i = 0; i < _len; ++i)
            if (_arr[i] != arr._arr[i])
                return false;
        return true;
    }
    inline bool operator!=(const FixArray<T>& arr) { return !(*this == arr); }
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
    // concatenate
    friend FixArray<T> operator+(const FixArray<T>& arr1, const FixArray<T>& arr2)
    {
        FixArray<T> ret(arr1.size() + arr2.size());
        std::copy(arr1.begin(),arr1.end(),ret.begin());
        std::copy(arr2.begin(),arr2.end(),ret.begin()+arr1.size());
        return ret;
    }
    // repeated array
    friend FixArray<T> operator*(const FixArray<T>& arr, int64_t n)
    {
        CHECK_THROW(n >= 0);
        FixArray<T> ret(arr.size() * n);
        auto p = ret.begin();
        while (n--)
        {
            std::copy(arr.begin(),arr.end(),p);
            p += arr.size();
        }
        return ret;
    }
    // repeated array
    friend inline FixArray<T> operator*(int64_t n, const FixArray<T>& arr) { return arr * n; }
    friend std::ostream& operator<<(std::ostream& os, const FixArray<T>& arr)
    {
        os << "FixArray[";
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
    FixArray<T> slice(int64_t beg, int64_t end, int64_t step = 1) const
    {
        CHECK_THROW(step >= 1);
        beg = beg >= 0 ? beg : _len + beg;
        end = end >= 0 ? end : _len + end;
        if (beg < 0) beg = 0;
        if (end > (int64_t)_len) end = _len;
        FixArray<T> ret((end - beg + (step-1)) / step);
        T *p = ret._arr;
        while (beg < end)
        {
            *(p++) = _arr[beg];
            beg += step;
        }
        return ret;
    }
    // first n elements, or all if n >= size, error if negative
    inline FixArray<T> sliceFirst(int64_t n) const
    {
        CHECK_THROW(n >= 0);
        return slice(0,n);
    }
    // last n elements, or all if n >= size, error if negative
    inline FixArray<T> sliceLast(int64_t n) const
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
    static FixArray<T> fromFunc(size_t n, std::function<T(size_t)> func)
    {
        FixArray<T> ret(n);
        for (size_t i = 0; i < n; ++i)
            ret._arr[i] = func(i);
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
    FixArray<int> a1;
    assert(a1.size() == 0);
    assert(FixArray<std::string>().empty());
    // size
    FixArray<int> a2(0,64);
    assert(a2 == a1);
    FixArray<double> a3(5,1.3);
    assert(a3.size() == 5);
    assert(!a3.empty());
    assert_throw(FixArray<int>(-1));
    assert_throw(FixArray<float>(-1,-1.0));
    // initializer list
    FixArray<std::string> b1({"these","are","words"});
    FixArray<float> b2{1.1,1.2,1.3,1.4};
    FixArray<double> b3{1.3,1.3,1.3,1.3,1.3};
    FixArray<FixArray<char>> b4{{'a'},{'a','b'},{'a','b','c'}};
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
    auto c1(FixArray<float>{1.1,1.2,1.3,1.4});
    assert(c1 == b2);
    auto c2(FixArray<std::string>(0,"abc"));
    assert(c2 == FixArray<std::string>());
    // = copy
    FixArray<double> c3{1,2,3};
    c3 = a3;
    assert(c3 == a3);
    FixArray<std::string> c4 = b1;
    assert(c4 == b1);
    a4 = a2;
    assert(a4 == a2);
    // = move
    auto c5 = FixArray<std::string>{"here","are","some","more","words"};
    auto c6 = FixArray<short>(10,25);
    assert(c5 == FixArray<std::string>({"here","are","some","more","words"}));
    assert(c6.size() == 10);
    assert(c6 == FixArray<short>({25,25,25,25,25,25,25,25,25,25}));
    c5 = FixArray<std::string>(2,"repeat");
    assert(c5 == FixArray<std::string>({"repeat","repeat"}));
}

void test_comp()
{
    FixArray<float> a1{};
    FixArray<std::string> a2{};
    assert(a1 == FixArray<float>());
    assert(a2 == FixArray<std::string>(0,"string"));
    FixArray<double> a3{7.1,7.2,7.3};
    assert(a3 != FixArray<double>());
    assert(a3 != FixArray<double>({7.1,7.2}));
    assert(a3 == FixArray<double>({7.1,7.2,7.3}));
    assert(a3 != FixArray<double>({7.1,6.9,7.3}));
    assert(a3 != FixArray<double>({7.1,7.2,6.9}));
    assert(a3 != FixArray<double>({7.1,7.2,7.3,7.4}));
    a2 = {"s1","s2","s3","s4","s5","s6"};
    assert(a2 != FixArray<std::string>({"s1","s2","s3","s4","s5"}));
    assert(a2 == FixArray<std::string>({"s1","s2","s3","s4","s5","s6"}));
    assert(a2 != FixArray<std::string>({"s1","s2","s4","s3","s5","s6"}));
    assert(a2 != FixArray<std::string>({"s1","s2","s3","s4","s5","s6","s7"}));
}

void test_iter()
{
    FixArray<float> a1{};
    for (auto f : a1) // nothing should happen for empty array
        (void)f, assert(0);
    FixArray<std::string> a2{"9000"};
    for (auto s : a2)
        assert(s == "9000");
    FixArray<int> a3{1,4,9,16,25};
    for (size_t i = 0; i < a3.size(); ++i)
        assert(a3[i] == (int)((i+1)*(i+1)));
    FixArray<std::string> a4{"aishia","yue","tohru"};
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
    FixArray<std::string> a1;
    assert_throw(a1[0]);
    assert_throw(a1[-1]);
    assert_throw(a1[1]);
    FixArray<float> a2{-2.4,-1.2,0.0,1.2,2.4};
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
    assert(a2 == FixArray<float>({6.1,6.2,0.0,1.2,6.5}));
}

void test_rev()
{
    FixArray<int> a1;
    FixArray<int> a2;
    a2.reverse();
    assert(a1 == a2);
    FixArray<float> a3{1,2,3,4};
    FixArray<float> a4 = a3;
    a4.reverse();
    a4.reverse();
    assert(a3 == a4);
    a4.reverse();
    assert(a4 == FixArray<float>({4,3,2,1}));
    FixArray<std::string> a5(1,"no");
    FixArray<std::string> a6 = a5;
    a5.reverse();
    assert(a5 == a6);
    FixArray<char> a7 = {'1','2','3','4','5'};
    a7.reverse();
    assert(a7 == FixArray<char>({'5','4','3','2','1'}));
}

void test_plus()
{
    FixArray<int> a1(3,7);
    FixArray<int> a2(4,-1);
    assert(a1+a2 == FixArray<int>({7,7,7,-1,-1,-1,-1}));
    assert(FixArray<std::string>() + FixArray<std::string>() == FixArray<std::string>());
    assert(a1 + FixArray<int>() == a1);
    assert(FixArray<int>() + a2 == a2);
    FixArray<double> a3{-5,-6};
    FixArray<double> a4{17,18};
    assert(a3+a4 == FixArray<double>({-5,-6,17,18}));
}

void test_mult()
{
    FixArray<char> a1{};
    assert(a1*100 == FixArray<char>() && 1000*a1 == FixArray<char>());
    FixArray<int> a2{0,1,2};
    assert(a2*1 == a2 && 1*a2 == a2);
    assert(2*a2 == FixArray<int>({0,1,2,0,1,2}));
    assert(5*a2 == FixArray<int>({0,1,2,0,1,2,0,1,2,0,1,2,0,1,2}));
    assert(17*FixArray<double>(19,323.0) == FixArray<double>(323,323.0));
    assert(0*FixArray<char>(10,'a') == a1);
    assert_throw(-1 * a1);
    assert_throw(a1 * -2);
}

void test_print()
{
    std::stringstream ss;
    ss.str("");
    ss << FixArray<double>();
    assert(ss.str() == "FixArray[]");
    ss.str("");
    ss << FixArray<char>{'a','b','c','1','2','3'};
    assert(ss.str() == "FixArray[a,b,c,1,2,3]");
    ss.str("");
    ss << FixArray<int>{0,1,-1,2,-2,3,-3};
    assert(ss.str() == "FixArray[0,1,-1,2,-2,3,-3]");
    ss.str("");
    ss << FixArray<std::string>{"one",",","two"};
    assert(ss.str() == "FixArray[one,,,two]");
}

void test_slice()
{
    FixArray<int> a1{0,1,2,3,4,5,6,7,8,9};
    assert(a1.slice(0,3) == FixArray<int>({0,1,2}));
    assert(a1.slice(-3,-1) == FixArray<int>({7,8}));
    assert(a1.slice(7,15) == FixArray<int>({7,8,9}));
    assert(a1.slice(2,7) == FixArray<int>({2,3,4,5,6}));
    assert(a1.slice(2,15,3) == FixArray<int>({2,5,8}));
    assert(a1.slice(0,10,9) == FixArray<int>({0,9}));
    assert(a1.slice(5,7,3) == FixArray<int>({5}));
    assert(a1.slice(5,7,2) == FixArray<int>({5}));
    assert(a1.slice(0,a1.size()) == a1);
    assert_throw(a1.slice(0,10,0));
    assert_throw(a1.slice(-5,-3,-1));
    assert(a1.sliceFirst(20) == a1);
    assert(a1.sliceLast(21) == a1);
    assert(a1.sliceFirst(0) == FixArray<int>());
    assert(a1.sliceFirst(1) == FixArray<int>(1,0));
    assert(a1.sliceFirst(4) == FixArray<int>({0,1,2,3}));
    assert(a1.sliceFirst(9) == FixArray<int>({0,1,2,3,4,5,6,7,8}));
    assert(a1.sliceFirst(10) == a1);
    assert(a1.sliceLast(0) == FixArray<int>());
    assert(a1.sliceLast(1) == FixArray<int>(1,9));
    assert(a1.sliceLast(5) == FixArray<int>({5,6,7,8,9}));
    assert(a1.sliceLast(10) == a1);
    FixArray<std::string> a2;
    assert(a2.sliceFirst(0) == a2);
    assert(a2.sliceFirst(1) == a2);
    assert(a2.sliceLast(0) == a2);
    assert(a2.sliceLast(1) == a2);
    assert_throw(a2.sliceFirst(-1));
    assert_throw(a2.sliceLast(-1));
}

void test_sort()
{
    FixArray<float> a1{-1.5,-1.0,-0.001,0.5,3.14,42.0};
    FixArray<float> a2{42.0,-1.0,-1.5,3.14,-0.001,0.5};
    a2.sort();
    assert(a1 == a2);
    a1 = {-1.5,-1.0,-0.001,0.5,3.14,42.0};
    a2 = {42.0,-1.0,-1.5,3.14,-0.001,0.5};
    a2.sort([](float f1, float f2){return f1 > f2;});
    a1.reverse();
    assert(a1 == a2);
    FixArray<int> a3{10,12,11,22,28,24,20,26,31,39};
    FixArray<int> a4{22,10,31,28,24,39,12,20,11,26};
    a4.stableSort([](int a, int b){return a/10 < b/10;});
    assert(a3 == a4);
}

void test_func()
{
    auto a1 = FixArray<double>::fromFunc(5,[](size_t a){return 1.0/(a+1);});
    assert(a1 == FixArray<double>({1.0,0.5,1.0/3.0,0.25,0.2}));
    auto a2 = FixArray<int>::fromFunc(10,[](size_t i){return i*i;});
    assert(a2 == FixArray<int>({0,1,4,9,16,25,36,49,64,81}));
    auto a3 = FixArray<uint32_t>::fromFunc(8,[](size_t a){return a*a + 3*a + 6;});
    assert(a3 == FixArray<uint32_t>({6,10,16,24,34,46,60,76}));
    auto a4 = FixArray<bool>::fromFunc(6,[](size_t a){return a % 2 != 0;});
    assert(a4 == FixArray<bool>({0,1,0,1,0,1}));
    auto a5 = FixArray<bool>::fromFunc(a1.size(),[&a1](size_t i){return a1[i] < 0.5;});
    assert(a5 == FixArray<bool>({false,false,true,true,true}));
}

int main()
{
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
}
