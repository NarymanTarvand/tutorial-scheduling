from tabu_search_newest import *

# start each iteration at 1

# INSTANCE 1
ga_iterations_i1 = list(range(1, 101))
ga_best_sols_i1 = [43, 33, 32, 31, 31, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30,
                        30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30,
                        30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30,
                        30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30]

tabu_iterations_i1 = list(range(1,159))
tabu_best_sols_i1 = [47, 46, 44, 43, 42, 41, 40, 40, 40, 39, 39, 39, 39, 38, 38, 37, 37, 37, 37, 36, 36, 36, 36, 36, 36,
                  36, 36, 36, 36, 36, 36, 36, 36, 36, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35,
                  35, 35, 35, 35, 35, 35, 35, 34, 34, 34, 34, 34, 34, 34, 34, 34, 34, 34, 34, 34, 34, 34, 34, 34, 34,
                  34, 34, 34, 34, 34, 34, 34, 34, 34, 34, 34, 34, 34, 34, 34, 34, 34, 34, 34, 34, 34, 34, 34, 34, 34,
                  34, 34, 34, 34, 34, 34, 34, 34, 34, 34, 34, 34, 34, 34, 34, 34, 34, 34, 34, 34, 34, 34, 34, 34, 34,
                  34, 34, 34, 34, 34, 34, 34, 34, 34, 34, 34, 34, 34, 34, 34, 34, 34, 34, 34, 34, 34, 34, 34, 34, 34,
                  34, 34, 34, 34, 34, 34, 34, 34]

# add in GRASP here
grasp_iterations_i1 = list(range(1, 101))
grasp_best_sols_i1 = []

all_iters_i1  = [ga_iterations_i1, tabu_iterations_i1, grasp_iterations_i1]
all_best_sols_i1 = [ga_best_sols_i1, tabu_best_sols_i1, grasp_best_sols_i1]

# INSTANCE 2

# add in ga instance 2
ga_iterations_i2 = list(range(1, 101))
ga_best_sols_i2 = []


tabu_iterations_i2 = list(range(1, 259))
tabu_best_sols_i2 = [78, 77, 76, 76, 75, 75, 74, 74, 74, 74, 73, 72, 72, 72, 72, 72, 72, 72, 72, 71, 70, 69, 69, 69,
                     68, 67, 67, 66, 65, 65, 65, 64, 64, 64, 64, 64, 64, 64, 64, 64, 64, 64, 64, 64, 64, 64, 64, 64,
                     64, 64, 64, 64, 64, 63, 63, 63, 63, 63, 63, 63, 63, 62, 62, 62, 62, 62, 62, 62, 62, 62, 62, 62,
                     62, 62, 62, 61, 61, 61, 61, 61, 61, 60, 60, 60, 60, 60, 60, 60, 60, 60, 60, 60, 60, 60, 60, 60,
                     60, 60, 59, 59, 59, 59, 59, 59, 59, 59, 59, 59, 59, 59, 59, 59, 59, 59, 58, 58, 58, 58, 58, 58,
                     58, 58, 58, 58, 58, 58, 58, 58, 58, 58, 58, 58, 58, 58, 58, 58, 58, 58, 58, 58, 58, 58, 58, 58,
                     58, 58, 58, 58, 58, 58, 58, 58, 58, 58, 58, 58, 58, 57, 57, 57, 57, 57, 57, 57, 57, 57, 57, 57,
                     57, 57, 57, 57, 57, 57, 57, 57, 57, 57, 57, 57, 57, 57, 57, 57, 57, 57, 57, 57, 57, 57, 57, 57,
                     57, 57, 57, 57, 57, 57, 57, 57, 57, 57, 57, 57, 57, 57, 57, 57, 57, 57, 57, 57, 57, 57, 57, 57,
                     57, 57, 57, 57, 57, 57, 57, 57, 57, 57, 57, 57, 57, 57, 57, 57, 57, 57, 57, 57, 57, 57, 57, 57,
                     57, 57, 57, 57, 57, 57, 57, 57, 57, 57, 57, 57, 57, 57, 57, 57, 57, 57]

# add in grasp instance 2
grasp_iterations_i2 = list(range(1, 101))
grasp_best_sols_i2 = []

def ensure_max_length(lst, max_length):
    if len(lst) < max_length:
        lst.extend([lst[-1]] * (max_length - len(lst)))

def create_graph(iterations, best_sols, instance):
    # Intakes a list of iterations lists and a list of best sol lists
    # the lists must be in order of genetic alg, tabu search, GRASP
    max_length = max(len(iteration_list) for iteration_list in iterations)
    for sols in best_sols:
        ensure_max_length(sols, max_length)
    ga_best_sols = best_sols[0]
    tabu_best_sols = best_sols[1]
    grasp_best_sols = best_sols[2]
    plt.plot(list(range(max_length)), tabu_best_sols, label='Tabu Search', color='blue')
    plt.plot(list(range(max_length)), ga_best_sols, label='Genetic Algorithm', color='green')
    plt.plot(list(range(max_length)), grasp_best_sols, label='GRASP', color='red')
    plt.xlabel('Iteration Number')
    plt.ylabel('Best Solution Value')
    plt.title('Best Solutions Over Iterations')
    all_best_solutions = tabu_best_sols + ga_best_sols + grasp_best_sols
    min_value = int(min(all_best_solutions))
    max_value = int(max(all_best_solutions))
    yticks = np.arange(min_value, max_value + 2, step=2)
    plt.yticks(yticks)
    plt.legend()
    if instance == 1:
        plt.savefig('iterations_best_sol_i1.png')
    if instance == 2:
        plt.savefig('iterations_best_sol_i2.png')
    plt.show()

create_graph(all_iters_i1, all_best_sols_i1, 1)
create_graph(all_iters_i1, all_best_sols_i1, 2)
