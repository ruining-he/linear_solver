import sys


def list_dot_mul_sum(list_a, list_b):
    if len(list_a) != len(list_b):
        sys.exit("Error: list_dot_mul_sum: lists have different length.")
    return sum([list_a[i]*list_b[i] for i in range(len(list_a))])


def if_equal(a, b):
    if abs(a-b) < 0.0001:
        return True
    else:
        return False

# def input_data():


if __name__ == '__main__':
    print("RESULT: list_dot_mul:", list_dot_mul_sum([1, 2, 3], [1, 1, 1]))
