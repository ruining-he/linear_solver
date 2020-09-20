from Matrix import *
from operation import *


class SimplexTableau(list):

    def __init__(self, i_obj, ic, i_m, i_n, ia, i_sign, ib, i_x):
        '''
        ia: matrix

        input like:
        Min Z = ((c1, c2, c3, ...)^T)*(x1, x2, x3, ...)
        c is in RHS

        try to transform to Standard Form of LP and build a tableau
        Standard Form of LP:
        Min Z = ((c1, c2, c3, ...)^T)*(x1, x2, x3, ...)
        AX = b
        X >= 0

        Remaining questions: how to express"<="? I think {<=,==,>=}={-1,0,1}
        ix: (<=0, free, >=0) = (-1, 0, 1)
        And to standardize, many things needs to be done!
        '''

        self.m = i_m # numbers  of constraints
        self.n = i_n # numbers of variables
        self.slack_n = 0
        self.obj = i_obj # max or min: 0-min, 1-max
        self.x = i_x # variables: (>=0, free, <=0) = (-1, 0, 1)
        self.c = ic # coefficients in OBJ function
        self.a = Matrix(ia) # coefficients in constraints
        self.b = ib # RHS numbers
        self.sign = i_sign # <=, ==, >= in constraints
        self.standard()
        self.tableau = self.build_tableau()
        self.changed_variables = [] # index: 0, 1, 2
        # if optimal_solution = [], unbounded
        self.optimal_solution = self.iter_tableau()

    def standard(self):
        # two-phase can inherit from this

        # obj: 0-min; 1-max
        if self.obj == 1:
            self.c = [-1*item for item in self.c]

        # introduce slack;
        # sign: (<=, ==, >=) == (-1, 0, 1)
        # ix: (<=0, free, >=0) = (-1, 0, 1)
        for i in range(self.m):
            if self.sign[i] == 0:
                continue
            else:
                self.n += 1
                self.slack_n += 1
                self.c.append(0)
                self.x.append(1)
                new_col = [0 for i in range(self.m)]
                if self.sign[i] == -1:
                    new_col[i] = 1
                elif self.sign[i] == 1:
                    new_col[i] = -1
                self.a.add_new_col(self.n, new_col)

        # variables -> >=0
        # ix: (<=0, free, >=0) = (-1, 0, 1)
        i = 0
        # for i in range(self.n):
        while i < self.n:
            if self.x[i] == 1:
                i += 1
                continue

            elif self.x[i] == -1: # negative variable
                self.c[i] = -1*(self.c[i])
                for row_a in self.a:
                    row_a[i] = -1*(row_a[i])
                self.x[i] = 1
                self.changed_variables.append([i, -1])

            elif self.x[i] == 0: # free variable
                self.c.insert(i+1, -1*self.c[i])
                for row_a in self.a:
                    row_a.insert(i+1, -1*(row_a[i]))
                self.x.insert(i+1, 1)
                self.x[i] = 1
                self.n += 1
                # ↑会更新range？while会。
                self.changed_variables.append([i, 0])
            i += 1

    def build_tableau(self):
        # build tableau
        # 不能用a, 要更新成用tableau
        tab = Matrix(self.a.copy())
        # c
        build_c = [-1*item for item in self.c]
        tab.add_new_row(0, build_c)
        # leftest col
        build_newcol = [0 for i in range(self.m+1)]
        build_newcol[0] = 1
        tab.add_new_col(0, build_newcol)
        # b
        build_newcol = [item for item in self.b]
        build_newcol.insert(0, 0)
        tab.add_new_col(self.n+2, build_newcol)

        print("in Class, tab = ", tab)
        return tab

    def iter_tableau(self):
        # 暂时没有排除 无界解等情况
        # initial solution
        basic_variable_all = []
        basic_variable = []
        # col number of basic variable
        for j in range(1, self.tableau.ncol-1):
            if len(basic_variable) == self.tableau.nrow:
                break
            if self.tableau.if_identity(j):
                basic_variable.append(j)
        basic_variable.sort()

        if len(basic_variable) != self.m:
            sys.exit("Error: Wrong initialize. Can't find initial solution.")

        # iter begin
        count = 0
        bland_flag = 0
        while not self.tableau.if_all_negative_other_first():
            # print
            print("Iteration: ", count)
            self.print_tab()
            count += 1

            # entering
            if not bland_flag and basic_variable not in basic_variable_all:
                enterj = self.tableau.find_max_other_first()
            else:
                # bland法则是从此都这样用还是仅一次用？--从此都这样用
                bland_flag = 1
                for j in range(1, self.tableau.ncol-1):
                    if self.tableau[0][j] > 0:
                        enterj = j
                        break

            # transform enterj th col to identity
            # choose leaving variables
            min_ratio_i = 1
            min_ratio = 9999
            # row number in leaving_set
            leaving_set = []
            nonpositive_leaving_count = 0
            for i in range(1, self.tableau.nrow):
                if self.tableau[i][enterj] != 0:
                    # avoid divide 0
                    new_ratio = self.tableau.ratio_RHS(i, enterj)
                    if new_ratio < 0:
                        nonpositive_leaving_count += 1
                        continue
                    elif new_ratio == 0:
                        if self.tableau[i][enterj] < 0:
                            continue

                    if new_ratio == min_ratio:
                        leaving_set.append(i)
                    elif new_ratio < min_ratio:
                        min_ratio_i = i
                        min_ratio = new_ratio
                        if not leaving_set:
                            leaving_set.append(i)
                        elif new_ratio < self.tableau.ratio_RHS(leaving_set[0], enterj):
                            leaving_set.clear()
                            leaving_set.append(i)
                else:
                    nonpositive_leaving_count += 1

            if nonpositive_leaving_count == self.tableau.nrow-1:
                return None

            # find exact leaving variables(noted as leave_j)
            # Bland rule: min leaving j.
            leave_j = 9999
            for i in leaving_set:
                for j in basic_variable:
                    if self.tableau[i][j] == 1:
                        this_leave_j = j
                        if this_leave_j < leave_j:
                            leave_j = this_leave_j
            '''
            for j in basic_variable:
                if self.tableau[min_ratio_i][j] == 1:
                    leave_j = j
                    break
            '''

            # col[maxj] should only leave min_ratio_i as 1, other elements in this col should be 0
            # QUESTION: 数学上，要如何最快地能够消元成功？这种成功是必然的吗？--有的，成功是必然的，因为对于其他原是identity的列\
            # 都是0-0，而对于要争夺basis位置的两个新老变量，才会是其他数减去非零数。
            for i in range(0, self.tableau.nrow):
                if self.tableau[i][enterj] == 0:
                    continue
                if i == min_ratio_i:
                    self.tableau.row_self_mul(min_ratio_i, 1/self.tableau[min_ratio_i][enterj])
                else:
                    divide_ratio = self.tableau[i][enterj]/self.tableau[min_ratio_i][enterj]
                    self.tableau.row_add(i, min_ratio_i, -1*divide_ratio)

            # update all basis
            basic_variable_all.append(basic_variable)
            # update basis
            basic_variable.append(enterj)
            basic_variable.remove(leave_j)
            basic_variable.sort()

        print("Iteration: ", count)
        self.print_tab()

        # insert multiple optimal solution here

        # insert multiple optimal solution here

        # get the optimal solution
        # optimal_solution[0] is the obj value, optimal_solution[i] is the value of Xi
        optimal_solution = [0 for i in range(self.n+1)]
        basic_variable.sort()
        for j in basic_variable:
            i = self.tableau.if_identity(j)
            optimal_solution[j] = self.tableau[i][-1]
        '''
        for j in range(self.tableau.ncol):
            
            i = self.tableau.if_identity(j)
            if i and (j in basic_variable):
                optimal_solution.append(self.tableau[i][-1])
            else:
                optimal_solution.append(0)
        '''

        # ↑得出的是标准化后各变量最后的值
        # get optimal function value
        obj_value = list_dot_mul_sum(optimal_solution[1:], self.c)
        if self.obj == 1:
            obj_value = -1*obj_value
        optimal_solution[0] = obj_value

        # 。。。对应的负的变量或者free的变量也得还原回去，我跪了。
        for pairs in self.changed_variables:
            if pairs[1] == -1:
                optimal_solution[pairs[0]+1] = -1*optimal_solution[pairs[0]+1]
            if pairs[1] == 0:
                optimal_solution[pairs[0]+1] = optimal_solution[pairs[0]+1]-optimal_solution[pairs[0]+2]
                del optimal_solution[pairs[0]+2]

        return optimal_solution

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

        for i in range(1, (len(self.optimal_solution)-self.slack_n)):
            print("X", i, ": ", self.optimal_solution[i])

    def print_tab(self):
        for row in self.tableau:
            for item in row:
                print('{:^10.4f}'.format(item), end='')
            print()


if __name__ == '__main__':
    '''
    # def __init__(self, i_obj, ic, i_m, i_n, ia, i_sign, ib, i_x):
    i_obj = 1
    ic = [1, 2]
    i_m = 2
    i_n = 2
    ia = [[1, 1], [0, 1]]
    i_sign = [-1, -1]
    ib = [3, 1]
    i_x = [1, 1]
    a = SimplexTableau(i_obj, ic, i_m, i_n, ia, i_sign, ib, i_x)
    a.print_tab()

#    a.iter_tableau()
    a.print_result()
    '''

    '''
    i_obj = 1
    ic = [3, 4, -1, 2]
    i_m = 2
    i_n = 4
    ia = [[1, 1, 1, 1], [1, 2, 1, 2]]
    i_sign = [-1, -1]
    ib = [25, 36]
    i_x = [1, 1, 1, 1]
    a = SimplexTableau(i_obj, ic, i_m, i_n, ia, i_sign, ib, i_x)
#    a.print_tab()

#    a.iter_tableau()
    print("END PRINT:")
    a.print_result()
    '''

    '''
    i_obj = 1
    ic = [3, 2, 1]
    i_m = 2
    i_n = 3
    ia = [[2, 1, 2],[-1, 2, -1]]
    i_sign = [-1, -1]
    ib = [24, 18]
    i_x = [1, 1, 1]
    a = SimplexTableau(i_obj, ic, i_m, i_n, ia, i_sign, ib, i_x)

    a.print_result()
    '''

    '''
    退化
    i_obj = 0
    ic = [-3/4, 150, -1/50, 6, 0, 0, 0]
    i_m = 3
    i_n = 7
    ia = [[1/4, -60, -1/25, 9, 1, 0, 0], [1/2, -90, -1/50, 3, 0, 1, 0], [0, 0, 1, 0, 0, 0, 1]]
    i_sign = [0, 0, 0]
    ib = [0, 0, 1]
    i_x = [1, 1, 1, 1, 1, 1, 1]
    a = SimplexTableau(i_obj, ic, i_m, i_n, ia, i_sign, ib, i_x)
    
    a.print_result()
    '''

    '''
    unbounded
    i_obj = 1
    ic = [5, 4]
    i_m = 2
    i_n = 2
    ia = [[1, 0], [1, -1]]
    i_sign = [-1, -1]
    ib = [7, 8]
    i_x = [1, 1]
    a = SimplexTableau(i_obj, ic, i_m, i_n, ia, i_sign, ib, i_x)

    a.print_result()
    '''
