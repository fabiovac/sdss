import json
import math
import random
from rmap import RMap
from ortools.sat.python import cp_model


class Restaurant:

    def __init__(self):
        self.tables = []
        self.num_tables = 0
        self.model = cp_model.CpModel()
        self.variables = {}
        self.seat_dim = 0.5
        self.time_limit = 0
        self.security_dis = 1.0
        self.save = True
        self.show = False

    def add_table(self, x_pos, y_pos, x_dim, y_dim):
        """
        Adds a new table to the tables list
        :param x_pos: x position of the table
        :param y_pos: y position of the table
        :param x_dim: x dimension of the table
        :param y_dim: y dimension of the table
        :return: table object
        """
        self.num_tables += 1
        table = Table(x_pos, y_pos, x_dim, y_dim, self.num_tables)
        self.tables.append(table)
        return table

    def load_data(self):
        """
        Loads data from the .json file, set software parameters and create new tables ans seats
        :return: nothing
        """
        while True:
            file_name = input('Input file name: ')
            try:
                with open(file_name, 'r') as json_file:
                    data = json.load(json_file)
                    self.seat_dim = float(data['seat_dim'])
                    self.time_limit = int(data['time_limit'])
                    self.security_dis = float(data['security_dis'])
                    self.save = bool(data['save'])
                    self.show = bool(data['show'])

                    for table in data['tables']:
                        x_pos = float(table['x_pos'])
                        y_pos = float(table['y_pos'])
                        x_dim = float(table['x_dim'])
                        y_dim = float(table['y_dim'])
                        table_obj = self.add_table(x_pos, y_pos, x_dim, y_dim)
                        for seat in table['seats']:
                            x_pos = float(seat['x_pos'])
                            y_pos = float(seat['y_pos'])
                            table_obj.add_seat(x_pos, y_pos)
                    break
            except FileNotFoundError:
                print('File not found')

    def define_variables(self):
        """
        Defines variables inside the model. Every seat is considered a Boolean variable as it can be
        True (enabled) or False (disabled).
        :return: nothing
        """
        for table in self.tables:
            for seat in table.seats:
                seat_name = seat.get_name()
                variable = self.model.NewBoolVar(seat_name)
                self.variables[seat_name] = variable

    def define_constraints(self):
        """
        Defines constraints inside the model. Only constraints between too close seats of different
        tables are set.
        :return: nothing
        """
        for table1 in self.tables:
            for seat1 in table1.seats:
                for table2 in self.tables:
                    for seat2 in table2.seats:
                        if table1 is not table2:
                            if seat1.distance(seat2) <= self.security_dis:
                                self.model.AddBoolOr(
                                    [self.variables[seat1.get_name()].Not(), self.variables[seat2.get_name()].Not()])

    def solve(self):
        """
        This is the core method of this Class and can be used outside to run the optimization.
        The method uses load_data(), define_variables() and define_constraints()
        The method uses also the SolutionsAnalyzer Class to analyse the solutions and to return
        only the top ones.
        :return: nothing
        """
        self.load_data()
        self.define_variables()
        self.define_constraints()

        solver = cp_model.CpSolver()
        if self.time_limit != 0:
            solver.parameters.max_time_in_seconds = self.time_limit * 60

        solutions_analyzer = SolutionsAnalyzer(self.variables)
        status = solver.SearchForAllSolutions(self.model, solutions_analyzer)

        top_solutions, top_solutions_score = solutions_analyzer.top_solutions()
        print(f'\nTop solutions (score={top_solutions_score}):')
        solutions_analyzer.print_solutions(top_solutions)

        self.save_solutions(top_solutions)

    def print(self):
        """
        Prints all the tables present in the restaurant and also the seats for each table.
        :return: nothinh
        """
        for table in self.tables:
            print(f'Table {table.num_table} ({table.x_pos}, {table.y_pos})')
            for seat in table.seats:
                print(f'    Seat {seat.get_name()} ({seat.x_pos}, {seat.y_pos})')

    def save_solutions(self, solutions):
        """
        This method using the RMap Class saves the solutions found by the solver.
        It can only save, only show or bot save and show the solutions.
        :param solutions: Solutions taken from the SolutionsAnalyzer
        :return: nothing
        """
        run_number = random.randint(1, 1000000)

        for idx, solution in enumerate(solutions):
            added_tables = []
            rmap = RMap()

            for variable in solution:
                table_seat_num = str(variable)
                table_num, seat_num = table_seat_num.split('-')
                table_num = int(table_num)
                seat_num = int(seat_num)

                table = self.tables[table_num - 1]
                seat = table.seats[seat_num - 1]

                if not table in added_tables:
                    added_tables.append(table)
                    rmap.add_table(table.x_pos, table.y_pos, table.x_dim, table.y_dim, name=str(table.num_table))

                if solution[variable] == 1:
                    enable = True
                else:
                    enable = False

                rmap.add_seat(seat.x_pos, seat.y_pos, seat_dim=self.seat_dim, name=str(seat.num_seat), enable=enable)

            if self.show:
                rmap.show(run_number, idx)
            if self.save:
                rmap.save(run_number, idx)


class Table:

    def __init__(self, x_pos, y_pos, x_dim, y_dim, num_table):
        self.seats = []
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.x_dim = x_dim
        self.y_dim = y_dim
        self.num_table = num_table
        self.num_seats = 0

    def add_seat(self, x_pos, y_pos):
        """
        Adds a seat in the current Table object
        :param x_pos: x position of the seat
        :param y_pos: y position of the seat
        :return: nothing
        """
        self.num_seats += 1
        self.seats.append(Seat(x_pos, y_pos, self.num_table, self.num_seats))

    def get_name(self):
        """
        Return the name of the current table object
        :return: name of the current table object
        """
        return self.num_table


class Seat:

    def __init__(self, x_pos, y_pos, num_table, num_seat):
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.num_table = num_table
        self.num_seat = num_seat

    def distance(self, seat):
        """
        Calculates the distance between the current seat and other one
        :param seat: Other seat to calculate the distance from
        :return: the distance between two seats
        """
        return math.sqrt((self.x_pos - seat.x_pos) ** 2 + (self.y_pos - seat.y_pos) ** 2)

    def get_pos(self):
        """
        Gives the position tuple of the current seat object
        :return: position tuple of the current seat object
        """
        return self.x_pos, self.y_pos

    def get_name(self):
        """
        Gives the name of the current seat object with both the table number and seat number
        :return: the name of the current seat object with both the table number and seat number
        """
        return str(self.num_table) + '-' + str(self.num_seat)


class SolutionsAnalyzer(cp_model.CpSolverSolutionCallback):

    def __init__(self, variables, debug=False):
        cp_model.CpSolverSolutionCallback.__init__(self)
        self.variables = variables
        self.variables_list = [variables[variable] for variable in variables]
        self.debug = debug
        self.solutions = []

    def on_solution_callback(self):
        """
        Called to analyse a solution
        :return: nothing
        """
        seats = 0
        solution = {}
        for variable in self.variables_list:
            if self.debug: print('%s=%i' % (variable, self.Value(variable)), end=' ')
            solution[variable] = self.Value(variable)
            if self.Value(variable) == 1:
                seats += 1
        if self.debug: print(' seats =', seats)
        self.solutions.append(solution)

    def print_solutions(self, solutions=None):
        """
        Prints solutions of the parameter solutions
        :param solutions: solutions to print
        :return: nothing
        """
        solutions_to_print = None
        if solutions:
            solutions_to_print = solutions
        else:
            solutions_to_print = self.solutions

        for solution in solutions_to_print:
            for variable in solution:
                print(f'{variable}={solution[variable]}', end=' ')
            print()

    def solution_score(self, solution):
        """
        Calculates the score for each solution.
        The score consists of the number of active (enabled) seats in the current solution
        :param solution: solution to calculate the score
        :return: score of the solution
        """
        score = 0
        for seat in solution:
            if solution[seat] == 1:
                score += 1

        return score

    def top_solutions(self):
        """
        Gives only the top solution based on the solution score calculation
        :return: top solutions and the top solutions score
        """
        top_solutions = []
        top_solutions_score = 0

        for solution in self.solutions:
            solution_score = self.solution_score(solution)

            if top_solutions_score < solution_score:
                top_solutions = [solution]
                top_solutions_score = solution_score
            elif top_solutions_score == solution_score:
                top_solutions.append(solution)

        return top_solutions, top_solutions_score
