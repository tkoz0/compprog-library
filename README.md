# compprog-library

# goals

- make it "almost as easy" to write C++ as it is to write Python for solving
programming problems (this goal is probably not realistic)
- provide useful code snippets to copy and paste for programming problems
- provide robust and memory safe data structures with tests
- provide a good balance of performance and memory efficiency
- provide some more obscure data structures not in standard libraries
  - 2d or 3d arrays
  - triangular 2d arrays
  - binary heap with element lookup
  - graphs (adjacency list, adjacency matrix)
- provide type generic algorithm code for copy and pasting

# cpp

The goal for now is to make all the code compatible with C++11.

Data structures
- `FixArary<T>` fixed length array
- `DynArray<T>` dynamically resizing array like `std::vector<T>`
- `SLList<T>` singly linked list
- `DLList<T>` doubly linked list similar to `std::list<T>`

TODOS
- rewrite `operator=` to use copy and swap (this handles self assignment)
- reduce some code duplication

# python3

Not really planned yet since I like C++ more than Python3.

# java

Even lower priority than Python3 due to my language preferences.
