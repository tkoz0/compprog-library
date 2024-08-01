/*
Functional programming tools
*/

#include <functional>

// basic operators
template <typename T, typename U = T>
auto f_plus(const T& a, const U& b) { return a+b; }
template <typename T, typename U = T>
auto f_minus(const T& a, const U& b) { return a-b; }
template <typename T, typename U = T>
auto f_mult(const T& a, const U& b) { return a*b; }
template <typename T, typename U = T>
auto f_div(const T& a, const U& b) { return a/b; }
template <typename T, typename U = T>
auto f_mod(const T& a, const U& b) { return a%b; }
template <typename T, typename U = T>
auto f_and(const T& a, const U& b) { return a&b; }
template <typename T, typename U = T>
auto f_or(const T& a, const U& b) { return a|b; }
template <typename T, typename U = T>
auto f_andl(const T& a, const U& b) { return a&&b; }
template <typename T, typename U = T>
auto f_orl(const T& a, const U& b) { return a||b; }
template <typename T, typename U = T>
auto f_xor(const T& a, const U& b) { return a^b; }
template <typename T, typename U = T>
auto f_lt(const T& a, const U& b) { return a<b; }
template <typename T, typename U = T>
auto f_gt(const T& a, const U& b) { return a>b; }
template <typename T, typename U = T>
auto f_leq(const T& a, const U& b) { return a<=b; }
template <typename T, typename U = T>
auto f_geq(const T& a, const U& b) { return a>=b; }
template <typename T, typename U = T>
auto f_eq(const T& a, const T& b) { return a==b; }
template <typename T, typename U = T>
auto f_neq(const T& a, const T& b) { return a!=b; }
template <typename T, typename U = T>
auto f_shr(const T& a, const T& b) { return a>>b; }
template <typename T, typename U = T>
auto f_shl(const T& a, const T& b) { return a<<b; }
template <typename T>
auto f_neg(const T& a) { return -a; }
template <typename T>
auto f_not(const T& a) { return !a; }
template <typename T>
auto f_inv(const T& a) { return ~a; }

int main()
{
    ;
}
