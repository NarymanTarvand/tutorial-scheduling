from GRASP import *
from utils import *
from constants import *
import random
import math
import time
import numpy as np
import matplotlib.pyplot as plt

file = "Data_Scheduling_AN.xlsx"
# file = "Data_Scheduling_AN_New_Instance.xlsx"
rootpath = "./"
sheets = pd.ExcelFile(os.path.join(rootpath, file))
availability = pd.read_excel(sheets, "Availability AN", header=2)
tutor_class = pd.read_excel(sheets, "Tutor_Class AN")
rooms = pd.read_excel(sheets, "Rooms AN")
slots = pd.read_excel(sheets, "Slots AN")
days = pd.read_excel(sheets, "Days AN")

# Rearranges availability have same index format as decission variable
mon_availability = np.array(
    availability[["S01-Mon", "S02-Mon", "S03-Mon", "S04-Mon", "S05-Mon"]]
)
tue_availability = np.array(
    availability[["S01-Tue", "S02-Tue", "S03-Tue", "S04-Tue", "S05-Tue"]]
)
wed_availability = np.array(
    availability[["S01-Wed", "S02-Wed", "S03-Wed", "S04-Wed", "S05-Wed"]]
)
tutor_availability = np.array(
    [mon_availability, tue_availability, wed_availability]
)
tutor_availability = np.moveaxis(tutor_availability, 0, -1)

allocation_num = np.array(
    tutor_class["Tutor ID"].value_counts()[availability["Slot"]]
)

ind_tutors = 0
_, solution = generate_feasible_schedule(NUM_TUTORS,
    NUM_SLOTS,
    NUM_DAYS,
    NUM_ROOMS,
    tutor_availability,
    allocation_num,
    ind_tutors,
)

# Set display options to show all rows and columns
pd.set_option('display.max_rows', None)  # Show all rows
pd.set_option('display.max_columns', None)  # Show all columns

def tabu_search(tabu_list_size, iter_without_improv, neighb_subset_size):
    # Generate starting solution
    _, current_solution = generate_feasible_schedule(NUM_TUTORS,
    NUM_SLOTS,
    NUM_DAYS,
    NUM_ROOMS,
    tutor_availability,
    allocation_num,
    ind_tutors)
    # our first values
    best_solution = current_solution
    best_solution_value = calculate_fitness(current_solution)
    print(f"Initial sol has value {best_solution_value}")
    tabu_list = [current_solution]
    term_counter = 0

    i = 0
    iterations = []
    best_solutions = []
    while term_counter < iter_without_improv:
        # create neighbourhood
        neighbourhood = single_swap_neighbourhood(current_solution, tutor_availability)
        # picking a random subset of 100
        neighbourhood = random.sample(neighbourhood, neighb_subset_size)
        # initialising best neighbour

        neighbour_vals = []
        for neighbour in neighbourhood:
            # go thru neighbourhood and calculate the fitness of each neighbour
            neighbour_vals += [(neighbour, calculate_fitness(neighbour))]
        while True:
            # Find the index of the tuple with the lowest second element (x[1])
            index_min_obj = min(range(len(neighbour_vals)), key=lambda i: neighbour_vals[i][1])

            # Use the index to access the actual values
            best_neighbour_pair = neighbour_vals[index_min_obj]
            best_neighbour = best_neighbour_pair[0]
            best_neighbour_val = best_neighbour_pair[1]

            is_in_tabu_list = any(np.array_equal(neighbour, arr) for arr in tabu_list)
            if not is_in_tabu_list:
                current_solution = best_neighbour
                current_obj = best_neighbour_val
                tabu_list.append(best_neighbour)
                if best_neighbour_val < best_solution_value:
                    # best neighbour is better than our best sol, update
                    best_solution = current_solution
                    best_solution_value = current_obj
                    # we've got an improvement
                    term_counter = 0
                else:
                    # no improvement
                    term_counter += 1
                break
            else:
                # We are in the tabu list
                if best_neighbour_val <= best_solution_value:
                    current_solution = best_neighbour
                    current_obj = best_neighbour_val
                    best_solution = current_solution
                    best_solution_value = current_obj
                    print("Aspiration criteria met, revoked from tabu list")
                    if best_neighbour_val < best_solution_value:
                        # improvement made
                        term_counter = 0
                    if best_neighbour_val == best_solution_value:
                        # no improvement made
                        term_counter += 1
                    break
                else:
                    # We are in tabu, and our best sol is not better
                    updated_pair = (best_neighbour, math.inf)
                    neighbour_vals[index_min_obj] = updated_pair
                    print("Best sol was in tabu list, but aspiration criteria not met")
                    term_counter += 1
                    continue

        if len(tabu_list) > tabu_list_size:
            # remove from tabu list once it gets too big
            tabu_list.pop(0)
        i += 1

        iterations += [i]
        best_solutions += [best_solution_value]
        print(f"Iteration {i}, Best Value: {best_solution_value}")

    return iterations, best_solutions, best_solution, best_solution_value

# Code to run Tabu Search, along with average time taken, amount of iterations, and the best sol out of a number of runs
tabu_attempts = []
times = []
num_tabu_runs = 10
for i in range(num_tabu_runs):
    print(f"Tabu run {i}")
    start_time = time.time()
    tabu_iterations, tabu_best_sols, sol, sol_value = tabu_search(tabu_list_size=500, iter_without_improv=100, neighb_subset_size=100)
    times += [float(time.time() - start_time)]
    tabu_attempts += [(tabu_iterations, tabu_best_sols, sol, sol_value)]
best_pair = min(tabu_attempts, key=lambda x: x[3])
tabu_iterations = best_pair[0]
tabu_best_sols = best_pair[1]
best_sol = best_pair[2]
best_val = best_pair[3]
print(f"The average time taken per run is {np.mean(times)}")
print(f"The best schedule achieves an objective value of {best_val}, it is:")
print(print_schedule(best_sol, days, slots, rooms, availability))
print(tabu_iterations, tabu_best_sols)


