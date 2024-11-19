# Copyright (c) 2024 Viliam Holly
# Basic boolean algebra terms solver using propositional logic.

# Operations:
#   not                         !
#   and                         &
#   xor                         ^
#   or                          |
#   implication                 >
#   nor                         nor
#   nand                        nand
#   if and only if (equals)     =

# Precedences:
#   not                         very high
#   and                         high
#   xor                         high
#   or                          medium
#   implication                 medium
#   nor                         medium
#   nand                        medium
#   if and only if (equals)     low

import sys
import re

class Node:
    def __init__(self, left_val, right_val, ty):
        self.left_val = left_val
        self.right_val = right_val
        self.ty = ty

    def print(self, indent=0):
        print("  " * indent + f"- node: {self.ty}")

        if isinstance(self.left_val, Node):
            self.left_val.print(indent + 1)
        else:
            print("  " * (indent + 1) + f"- value: {self.left_val}")

        if isinstance(self.right_val, Node):
            self.right_val.print(indent + 1)
        else:
            if self.right_val is not None:
                print("  " * (indent + 1) + f"- value: {self.right_val}")

class Parser:
    def __init__(self, toks):
        self._toks = toks
        self._curr_pos = 0
        self._lookahead = toks[0].lower()

    def _consume(self, tok):
        if self._curr_pos >= len(self._toks):
            print_err(f"[Error] Expected '{tok}' but got None instead")

        consumed = self._toks[self._curr_pos]
        if consumed != tok:
            print_err(f"[Error] Expected '{tok}' but got '{consumed}' instead")

        self._curr_pos += 1
        self._lookahead = self._toks[self._curr_pos] if self._curr_pos < len(self._toks) else None
        return consumed

    def _is_keyword(self, tok):
        return tok in {"&", "|", "!", "nor", "nand", "^", "=", ">", None}

    def _parse_primary_expr(self):
        if self._lookahead == "!":
            self._consume("!")
            return Node(self._parse_primary_expr(), None, "!")

        elif self._lookahead == "(":
            self._consume("(")
            expr = self._parse_low_prec_expr()
            self._consume(")")
            return expr

        elif not self._is_keyword(self._lookahead):
            return Node(self._consume(self._lookahead), None, "var")

        print_err(f"[Error] Expected primary expression but got {self._lookahead}")

    def _parse_high_prec_expr(self):
        tree = self._parse_primary_expr()
        while self._lookahead == "&" or self._lookahead == "^":
            junction = self._lookahead
            self._consume(junction)
            tree = Node(tree, self._parse_primary_expr(), junction) 
            
        return tree

    def _parse_med_prec_expr(self):
        tree = self._parse_high_prec_expr()
        while self._lookahead in {"|", "nor", "nand", ">"}:
            junction = self._lookahead
            self._consume(junction)
            tree = Node(tree, self._parse_high_prec_expr(), junction) 

        return tree

    def _parse_low_prec_expr(self):
        tree = self._parse_med_prec_expr()
        while self._lookahead == "=":
            self._consume("=")
            tree = Node(tree, self._parse_med_prec_expr(), "=") 

        return tree

    def parse(self):
        expr = self._parse_low_prec_expr()
        if self._lookahead is not None:
            print_err("[Error] Parser stopped (likely due to a missing junction)")
        return expr

class Solver:
    def __init__(self, exprs):
        self.exprs = exprs
        self.vars = list(get_vars_expr_list(exprs))
        self.vars.sort()
        self.values = [False] * len(self.vars)

    def _next_combination(self, curr_idx=0):
        if curr_idx >= len(self.values):
            return

        if not self.values[curr_idx]:
            self.values[curr_idx] = True
            return

        self.values[curr_idx] = False
        self._next_combination(curr_idx + 1)

    def _solve_expr(self, expr):
        if expr.ty == "var":
            if expr.left_val == "0":
                return False
            if expr.left_val == "1":
                return True
            return self.values[self.vars.index(expr.left_val)]
        if expr.ty == "!":
            return not self._solve_expr(expr.left_val)
        if expr.ty == "&":
            return self._solve_expr(expr.left_val) and self._solve_expr(expr.right_val)
        if expr.ty == "|":
            return self._solve_expr(expr.left_val) or self._solve_expr(expr.right_val)
        if expr.ty == "^":
            return self._solve_expr(expr.left_val) != self._solve_expr(expr.right_val)
        if expr.ty == "=":
            return self._solve_expr(expr.left_val) == self._solve_expr(expr.right_val)
        if expr.ty == "nand":
            return not (self._solve_expr(expr.left_val) and self._solve_expr(expr.right_val))
        if expr.ty == "nor":
            return not (self._solve_expr(expr.left_val) or self._solve_expr(expr.right_val))
        if expr.ty == ">":
            return not self._solve_expr(expr.left_val) or self._solve_expr(expr.right_val)

    def solve(self):
        solution_count = 0
        for _ in range(2 ** len(self.vars)):
            is_true = True
            for expr in self.exprs:
                if not self._solve_expr(expr):
                    is_true = False
                    break
            if is_true:
                solution_count += 1
                print("[Info] Found a solution: ", end="")
                for idx, var in enumerate(self.vars):
                    print(f"{var}={self.values[idx]}", end=" ")
                print()
            self._next_combination()

        print(f"[Info] {solution_count} out of {2 ** len(self.vars)} possible results are solutions.")

def tokenize_expr(expr):
    return re.findall(r"\w+|\S", expr.strip())

def print_err(*args):
    print(*args)
    exit(1)

def print_usage():
    print(f"Usage: python3 {sys.argv[0]} [-h] [--ast] <file>")
    print("     -h     : Print usage and exit.")
    print("     --ast  : Print parsed abstract syntax tree (AST).")
    print("     <file> : Parses and solves linked boolean algebra expressions from each line of the specified file.")
    print_err()

def print_exprs(exprs):
    for idx, expr in enumerate(exprs):
        print(f"Expression {idx + 1}:")
        expr.print()
        print()

def get_vars_expr(expr, curr_vars):
    if isinstance(expr, Node):
        # 0 and 1 are used as constants
        if expr.ty == "var" and expr.left_val != "0" and expr.left_val != "1":
            curr_vars.add(expr.left_val)
        else:
            get_vars_expr(expr.left_val, curr_vars)
            get_vars_expr(expr.right_val, curr_vars)

def get_vars_expr_list(exprs):
    curr_vars = set()
    for expr in exprs:
        get_vars_expr(expr, curr_vars)

    return curr_vars

def parse_args():
    if len(sys.argv) < 2:
        print_usage()

    args = (sys.argv[-1], sys.argv[-1] != "--ast" and "--ast" in sys.argv, sys.argv[-1] != "-h" and "-h" in sys.argv)
    return args

def main():
    args = parse_args()
    if args[2]:
        print_usage()
    try:
        parsed_exprs = []
        with open(args[0], "r") as f:
            for expr in f:
                tokens = tokenize_expr(expr)
                if len(tokens) == 0:
                    continue
                parser = Parser(tokens)
                parsed_exprs.append(parser.parse())

        if args[1]:
            print_exprs(parsed_exprs)
        solver = Solver(parsed_exprs)
        solver.solve()

    except FileNotFoundError:
        print_err(f"[Error] Unable to open file '{args[0]}'")

if __name__ == "__main__":
    main()
