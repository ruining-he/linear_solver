from operation import *


class Matrix(list):

    def __init__(self, *i_all_row):
        print("i_all_row = ", i_all_row)
        if len(i_all_row) == 1:
            list.__init__(self, i_all_row[0])
            if isinstance(i_all_row[0], int):
                self.nrow = 1
                self.ncol = 1
            else:
                self.nrow = len(self)
                self.ncol = len(self[0])
        elif len(i_all_row) == 0:
            # 没处理 a = Matrix([]) 的情况；处理了 a = Matrix()的情况
            list.__init__(self, [])
            self.nrow = 0
            self.ncol = 0
        else:
            list.__init__(self, i_all_row)
            self.nrow = len(i_all_row)
            self.ncol = len(i_all_row[0])

    def add_new_row(self, i, new_row):
        # insert new_row in ith elements, making the new_row the new ith elements in new matrix( i = 0, 1, 2, ... nrow
        if len(new_row) != self.ncol:
            sys.exit("Error: Wrong new row with different number of elements.")

        self.insert(i, new_row)
        self.nrow += 1

    def add_new_col(self, i, new_col):
        # insert new_col in ith elements, i = 0, 1, 2, ... nrow
        if len(new_col) != self.nrow:
            sys.exit("Error: Wrong new col with different number of elements.")

        k = 0
        for item in new_col:
            self[k].insert(i, item)
            k += 1

        self.ncol += 1

    def if_identity(self, j):
        count_one = 0
        count_zero = 0
        index_one = 0
        for i in range(self.nrow):
            if if_equal(self[i][j], 1):
                count_one += 1
                index_one = i
                if count_one > 1:
                    return False
            elif if_equal(self[i][j], 0):
                count_zero += 1
        # if True, then return the index of i
        if count_zero + count_one == self.nrow:
            return index_one
        else:
            return False

    def row_add(self, m, n, mul=1):
        self[m] = [self[m][i] + mul*self[n][i] for i in range(self.ncol)]

    def row_self_mul(self, i, mul):
        self[i] = [self[i][j]*mul for j in range(self.ncol)]

    def if_all_negative_other_first(self, i=0):
        # valid for row
        for j in range(1, self.ncol):
            if self[i][j] > 0.00001:
                return False
        return True

    def find_max_other_first(self, i=0):
        # valid for row
        maxj = 1
        for j in range(1, self.ncol):
            if self[i][maxj] < self[i][j]:
                maxj = j
        return maxj

    def ratio_RHS(self, i, j):
        return self[i][-1]/self[i][j]


if __name__ == '__main__':
    c = Matrix([[1, 1], [2, 2]])
    print("c=", c)

    c.add_new_row(0, [3,3])
    print("new c = ", c)
    c.add_new_col(3,[9, 9, 9])
    print("new new new c =", c)

    c.add_new_col(0, [1, 0, 0])
    print("new new c = ", c)
    print("if identity?", 0, c.if_identity(0), "\nif identity?", 1, c.if_identity(1))

    a = Matrix([[5, 5, 5], [6, 6, 6], [7, 7, 7]])
    print("a=",a)

    a.row_add(0, 1, 1)
    print("after row_add, a=", a)

    a.row_sub(0, 1)
    print("after row_sub, a=", a)

    test_a = Matrix()
    print("test_a = ", test_a)

    test_b = Matrix([233, 233, 233], [666, 666, 666])
    print("test_b =", test_b)

    test_c = Matrix([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
    print("test_c =", test_c)
