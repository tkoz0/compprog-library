#include <cstdint>

template <uint64_t n> struct factorial { static constexpr uint64_t value = n * factorial<n-1>::value; };
template <> struct factorial<0> { static constexpr uint64_t value = 1; };
template <uint64_t n> static constexpr uint64_t factorial_v = factorial<n>::value;

static_assert(factorial_v<0> == 1ull);
static_assert(factorial_v<1> == 1ull);
static_assert(factorial_v<2> == 2ull);
static_assert(factorial_v<3> == 6ull);
static_assert(factorial_v<4> == 24ull);
static_assert(factorial_v<5> == 120ull);
static_assert(factorial_v<6> == 720ull);
static_assert(factorial_v<7> == 5040ull);
static_assert(factorial_v<8> == 40320ull);
static_assert(factorial_v<9> == 362880ull);
static_assert(factorial_v<10> == 3628800ull);
static_assert(factorial_v<11> == 39916800ull);
static_assert(factorial_v<12> == 479001600ull);
static_assert(factorial_v<13> == 6227020800ull);
static_assert(factorial_v<14> == 87178291200ull);
static_assert(factorial_v<15> == 1307674368000ull);
static_assert(factorial_v<16> == 20922789888000ull);
static_assert(factorial_v<17> == 355687428096000ull);
static_assert(factorial_v<18> == 6402373705728000ull);
static_assert(factorial_v<19> == 121645100408832000ull);
static_assert(factorial_v<20> == 2432902008176640000ull);
