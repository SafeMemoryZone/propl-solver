# propl-solver

Simple propositioal logic solver that outputs a truth table for terms.

## Quickstart

```sh
python3 solver.py [-h] [--ast] <file>
     -h     : Print usage and exit.
     --ast  : Print parsed abstract syntax tree (AST).
     <file> : Parses and solves linked boolean algebra expressions from each line of the specified file.
```

## Syntax

```
- variable                    letters, numbers and special symbols
- not                         !
- and                         &
- xor                         ^
- or                          |
- implication                 >
- nor                         nor
- nand                        nand
- if and only if (equals)     =
- 0                           false
- 1                           true
```

## Example

Example for an input file:
```
a > b > c > d
a ^ d
g = c
```
Note: All terms are interconnected.
