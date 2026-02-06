from z3 import *
from argparse import ArgumentParser

parser = ArgumentParser()

parser.add_argument(
    "--numbers",
    type=int,
    nargs="+",      # + significa almeno 1 numero
    required=True,
    help="List of space-separated numbers"
)

parser.add_argument(
    "--target",
    type=int,
    required=True,
    help="Target number to reach"
)

def CountingStrategy(numbers: list, target: int):

    """ PROBLEM DEFINITION """

    n = len(numbers)

    # We want to determine the best sequence of RESULTS to minimize the distance and the number of used numbers
    results = [Int(f'res_{i}') for i in range(n)]

    # We want to determine the best permutation of NUMBERS (a.k.a. indices of numbers array) to use to minimize the distance and the number of used numbers
    perm = [Int(f"perm_{i}") for i in range(n)]

    Operation = Datatype('Operation')
    Operation.declare('add')
    Operation.declare('sub')
    Operation.declare('mul')
    Operation.declare('div')
    Operation = Operation.create()

    # We want to determine the best sequence of OPERATIONS to minimize the distance and the number of used numbers
    ops = [Const(f"op_{i}", Operation) for i in range(n-1)]

    final_result = Int("final_result")

    # The primary goal is to minimize the number of used numbers
    distance = Int("distance")

    # The secondary goal is to minimize the number of used numbers
    used_numbers = Int("used_numbers")

    solver = Optimize() # Our aim is to minimize two objective functions

    # In order to indicize the array of numbers with indexes in perm, z3 requires to convert it into a native array with the Array function
    num_array = Array('num_array', IntSort(), IntSort())
    for i, v in enumerate(numbers):
        solver.add(num_array[i] == v)

    # Doing the same for the array of intermediate results
    res_array = Array('res_array', IntSort(), IntSort())
    for i, _ in enumerate(range(n)):
        solver.add(res_array[i] == results[i])

    """ OPERATIONS DEFINITION """

    def add(init_res, next_num):
        return init_res + next_num
    
    def sub(init_res, next_num):
        return init_res - next_num
    
    def mul(init_res, next_num):
        return init_res * next_num
    
    def div(init_res, next_num):
        return If(And(next_num != 0, init_res % next_num == 0), init_res / next_num, init_res)  # Eseguo la divisione solo se il dividendo non è zero e la divisione è intera, altrimenti non la eseguo

    """ CONSTRAINTS """

    solver.add(Distinct(perm))  # The permutations MUST contain different values
    for i in range(n):
        solver.add(And(perm[i] >= 0, perm[i] < n))  # Each index in the permutation array must belong to [0, n)

    solver.add(And(used_numbers >= 1, used_numbers <= n))   # The number of used numbers must belong to [1, n]

    # To indicize the array, z3 uses the Select native function
    solver.add(results[0] == Select(num_array, perm[0]))  # The first result must be equal to the first number chosen (read: first result equal to num_array of index perm[0])

    for i in range(n-1):

        transition = Or(
            And(ops[i] == Operation.add, Select(res_array, i+1) == add(results[i], Select(num_array, perm[i+1]))),
            And(ops[i] == Operation.sub, Select(res_array, i+1) == sub(results[i], Select(num_array, perm[i+1]))),
            And(ops[i] == Operation.mul, Select(res_array, i+1) == mul(results[i], Select(num_array, perm[i+1]))),
            And(ops[i] == Operation.div, Select(res_array, i+1) == div(results[i], Select(num_array, perm[i+1])))
        )

        # If the step number is greater than the number of used numbers, do not apply any transition: next state is equal to previous one
        solver.add(If(i < used_numbers - 1, transition, Select(res_array, i+1) == Select(res_array, i)))

    # The final result is the element in the array of intermediate results at the used_numbers-1 position
    solver.add(final_result == Select(res_array, used_numbers - 1))

    # The distance is defined as absolute value of final_result - target
    solver.add(distance == Abs(final_result - target))

    # Objective functions
    solver.minimize(distance)
    solver.minimize(used_numbers)

    """ SOLVING AND PRINTING """
    if solver.check() == sat:
        model = solver.model()

        # The as_long() method allows to convert z3 object into python-readable integers
        used_count = model[used_numbers].as_long()
        order_vals = [model[perm[i]].as_long() for i in range(used_count)]
        result_vals = [model[results[i]].as_long() for i in range(used_count)]

        first_num = model[results[0]].as_long()
        print("Initial number:", first_num)
        
        for i in range(used_count - 1):
            op_symbol = "?"
            if model[ops[i]] == Operation.add:
                op_symbol = "+"
            elif model[ops[i]] == Operation.sub:
                op_symbol = "-"
            elif model[ops[i]] == Operation.mul:
                op_symbol = "*"
            elif model[ops[i]] == Operation.div:
                op_symbol = "/"

            print(f"Step {i+1}: operation {op_symbol} with number {numbers[order_vals[i+1]]} -> result {result_vals[i+1]}")
        
        final = result_vals[used_count-1]
        dist = model[distance].as_long()
        
        print(f"Final number: {final}")
        print(f"Distance from goal: {dist}")

if __name__ == "__main__":
    args = parser.parse_args()
    CountingStrategy(args.numbers, args.target)