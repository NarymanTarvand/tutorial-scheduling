from GRASP import *
from utils import *
from constants import *
import random
import time
from copy import copy

file = "Data_Scheduling_AN.xlsx"
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

def tabu_search(max_iterations, tabu_list_size):
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
    tabu_list = []

    for i in range(max_iterations):
        # create neighbourhood
        neighbourhood = single_swap_neighbourhood(current_solution, tutor_availability)
        # initialising best neighbour
        best_neighbour = None
        best_neighbour_value = float('inf')

        for neighbour in neighbourhood:
            # check whether the neighbour is in the tabu list, if not, explore it
            is_in_tabu_list = any(np.array_equal(neighbour, arr) for arr in tabu_list)
            if not is_in_tabu_list:
                neighbour_value = calculate_fitness(neighbour)
                if neighbour_value < best_neighbour_value:
                    # we update our best neighbour in the neighbourhood
                    best_neighbour = neighbour
                    best_neighbour_value = neighbour_value

        if best_neighbour is not None:
            # best neighbour is now our current sol, allows us to escape local optima
            current_solution = best_neighbour
            tabu_list.append(best_neighbour)

            if best_neighbour_value < best_solution_value:
                # best neighbour is now our best sol
                best_solution = best_neighbour
                best_solution_value = best_neighbour_value

            if len(tabu_list) > tabu_list_size:
                # remove from tabu list once it gets too big
                tabu_list.pop(0)

        print(f"Iteration {i}, Best Value: {best_solution_value}")

    return best_solution, best_solution_value

sol, _ = tabu_search(100, 1000)
print(print_schedule(sol, days, slots, rooms, availability))