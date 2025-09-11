#!/usr/bin/env -S uv run --script
import sys


def check_python_version():
    error = False
    if sys.version_info < (3, 14):
        print(f"Error: Python {sys.version_info.major}.{sys.version_info.minor} detected.")
        error = True
    if not hasattr(sys, "_is_gil_enabled") or sys._is_gil_enabled():
        print("Error: Freethreading support is not enabled.")
        error = True
    if error:
        print("---")
        print("Python 3.14+ with freethreading required. Install with:")
        print("    uv python install 3.14t")
        print("or similar.")
        sys.exit(1)


def fib(n):
    if n <= 1:
        return n
    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, a + b
    return b


def main():
    check_python_version()
    n = int(input("Enter a number. Try 100000 or more: "))
    print("Calculating...")
    result = fib(n)
    # print(result)
    print("Done.")


if __name__ == "__main__":
    main()
