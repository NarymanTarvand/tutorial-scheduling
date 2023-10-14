from tabu_search_newest import *

# start each iteration at 1
ga_iterations = list(range(1, 101))
ga_best_sols = [43, 33, 32, 31, 31, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30,
                        30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30,
                        30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30,
                        30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30]

tabu_iterations = list(range(1,159))
tabu_best_sols = [47, 46, 44, 43, 42, 41, 40, 40, 40, 39, 39, 39, 39, 38, 38, 37, 37, 37, 37, 36, 36, 36, 36, 36, 36,
                  36, 36, 36, 36, 36, 36, 36, 36, 36, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35,
                  35, 35, 35, 35, 35, 35, 35, 34, 34, 34, 34, 34, 34, 34, 34, 34, 34, 34, 34, 34, 34, 34, 34, 34, 34,
                  34, 34, 34, 34, 34, 34, 34, 34, 34, 34, 34, 34, 34, 34, 34, 34, 34, 34, 34, 34, 34, 34, 34, 34, 34,
                  34, 34, 34, 34, 34, 34, 34, 34, 34, 34, 34, 34, 34, 34, 34, 34, 34, 34, 34, 34, 34, 34, 34, 34, 34,
                  34, 34, 34, 34, 34, 34, 34, 34, 34, 34, 34, 34, 34, 34, 34, 34, 34, 34, 34, 34, 34, 34, 34, 34, 34,
                  34, 34, 34, 34, 34, 34, 34, 34]

# start each iteration at 1

# add in GRASP here
grasp_iterations = list(range(1, 101))
grasp_best_sols = []
all_iters = [ga_iterations, tabu_iterations, grasp_iterations]
all_best_sols = [ga_best_sols, tabu_best_sols, grasp_best_sols]

def ensure_max_length(lst, max_length):
    if len(lst) < max_length:
        lst.extend([lst[-1]] * (max_length - len(lst)))

def create_graph(iterations, best_sols):
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
    plt.savefig('iterations_best_sol.png')
    plt.show()

create_graph(all_iters, all_best_sols)
