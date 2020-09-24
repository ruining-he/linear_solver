from SimplexTableau import *


class TwoPhaseSolver(SimplexTableau):

    def __init__(self, i_obj, ic, i_m, i_n, ia, i_sign, ib, i_x):
        SimplexTableau.__init__(self, i_obj, ic, i_m, i_n, ia, i_sign, ib, i_x)
        self.artificial_variable_col = []
        self.artificial_n = 0
        self.two_phase_init()
        print("\nTwo phase init tableau:")
        self.print_tab()
        # 换基
        self.solve_tableau()
        self.print_result()
        self.after_initial = self.after_two_phase_initial()

    def after_two_phase_initial(self):
        if if_equal(self.optimal_solution[0], 0):
            # new basic 是optimal solution中非0的量。
            new_basic_variable = []
            for i in range(1, len(self.optimal_solution)):
                if self.optimal_solution[i] != 0:
                    new_basic_variable.append(i)
            return new_basic_variable
        else:
            print("By two phase method, there is no initial feasible solution.")
            return None

    def two_phase_init(self):
        # add artificial variables and directly update new tableau without changing self.x and so on.
        for i in self.slack_variable_row:
            j = -2
            while j >= (-1*self.tableau.ncol + 1):
                if if_equal(self.tableau[i][j], 0) or if_equal(self.tableau[i][j], 1):
                    j -= 1
                    continue
                elif if_equal(self.tableau[i][j], -1):
                    self.artificial_variable_col.append(self.tableau.ncol-1)
                    # new a and c
                    new_col = [0 for k in range(self.tableau.nrow)]
                    new_col[0] = -1
                    new_col[i] = 1
                    self.tableau.add_new_col(self.tableau.ncol-1, new_col)
                    self.n += 1
                    self.artificial_n += 1
                    self.c.append(-1)
                    break

        # tableau self.c change
        for j in range(len(self.c)):
            if j+1 not in self.artificial_variable_col:
                self.c[j] = 0

        # tableau row 0 change
        for j in range(1, self.tableau.ncol-1):
            if j not in self.artificial_variable_col:
                self.tableau[0][j] = 0

        self.obj = 0

    def init_basic_variable(self):
        # col number of basic variable
        basic_variable = []
        for j in range(1, self.tableau.ncol-1):
            if len(basic_variable) == self.m-len(self.artificial_variable_col):
                break
            if self.tableau.if_identity(j):
                basic_variable.append(j)

        for j in self.artificial_variable_col:
            basic_variable.append(j)
        basic_variable.sort()

        # 如何把tableau化为初始tableau
        for j in self.artificial_variable_col:
            for i in range(1, self.tableau.nrow):
                if if_equal(self.tableau[i][j], 1):
                    self.tableau.row_add(0, i, 1)

        return basic_variable

    def print_result(self):
        # unbounded
        if not self.optimal_solution:
            print("\nUnbounded feasible region and infinite objective value.")
            return None

        if self.obj == 0:
            objstr = 'Min'
        else:
            objstr = 'Max'
        print("\n[", objstr, "]", " objective function value = ", self.optimal_solution[0])

        for i in range(1, (len(self.optimal_solution)-self.artificial_n)):
            print("X", i, ": ", self.optimal_solution[i])


if __name__ == '__main__':

    # two phase test
    i_obj = 0
    ic = [1, -2]
    i_m = 3
    i_n = 2
    ia = [[1, 1], [-1, 1], [0, 1]]
    i_sign = [1, 1, -1]
    ib = [2, 1, 3]
    i_x = [1, 1]

    b = TwoPhaseSolver(i_obj, ic.copy(), i_m, i_n, ia.copy(), i_sign.copy(), ib.copy(), i_x.copy())
    print("after two phase, the initial basis for initial equations is ", b.after_initial )
