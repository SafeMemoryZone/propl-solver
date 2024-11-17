import sys
import re

def tokenize_expr(expr):
    # Any other punctuators will be skiped
    return re.findall(r"\(|\)|\w+", expr.strip())

def print_err(*args):
    print(*args)
    exit(1)

def print_usage():
    print(f"Usage: python3 {sys.argv[0]} [-s <file>]")
    print("    -s <file> : Parses and solves linked boolean algebra expressions from each line of the specified file.")
    print_err()

def main():
    if len(sys.argv) < 2:
        print_usage()

    try:
        with open(sys.argv[1], "r") as f:
            for expr in f:
                print(tokenize_expr(expr))
    except FileNotFoundError:
        print_err(f"Error: Unable to open file '{sys.argv[1]}'")

if __name__ == "__main__":
    main()
