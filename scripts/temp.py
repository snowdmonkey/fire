import time
import threading


def test_function():
    try:
        x = 1/0
    except Exception as e:
        print("error happend")
        return 0
    finally:
        print("finally executed")

if __name__ == "__main__":
    print(test_function())