import os
import random
import time
import numpy as np
import pandas as pd

from utils import calculate_fitness, is_feasible_schedule, print_schedule
from constants import *


def greedy_randomised_construction(availability, tutor_class, tutor_availability):
    """
    Produce a greedy randomised construction of a schedule.
    First randomly shuffle the list of all possible allocations (slot, day, room) and the list of tutors.
    For all possible allocations iterate over the tutors and if it's feasible,
    assign the tutor that has the lowest marginal cost to that position.
    """
    # start with an empty solution
    schedule = np.zeros((NUM_TUTORS, NUM_SLOTS, NUM_DAYS, NUM_ROOMS))

    # define and shuffle all possible locations
    possible_allocations = [
        [slots_idx, day_idx, room_idx]
        for slots_idx in range(NUM_SLOTS)
        for day_idx in range(NUM_DAYS)
        for room_idx in range(NUM_ROOMS)
    ]
    random.shuffle(possible_allocations)

    # define and shuffle all tutors
    tutor_to_idx = dict(zip(availability["Slot"], availability.index))
    unassigned_tutors = tutor_class["Tutor ID"].to_list()
    random.shuffle(unassigned_tutors)

    unassigned_tutor_idx = [tutor_to_idx[tutor] for tutor in unassigned_tutors]

    for allocation in possible_allocations:
        cost = []
        valid_tutors = []

        # if no more tutors to assign, stop
        if len(unassigned_tutor_idx) == 0:
            break

        for tutor in unassigned_tutor_idx:
            # if the tutor is unavailable at that slot and day, continue
            # if any tutor is already in that slot, day and room, continue
            # if the tutor is already in a room at that slot and day, continue
            if (
                (tutor_availability[tutor, allocation[0], allocation[1]] == 0)
                or any(schedule[:, allocation[0], allocation[1], allocation[2]])
                or any(schedule[tutor, allocation[0], allocation[1], :])
            ):
                continue
            schedule_copy = schedule.copy()
            schedule_copy[tutor, allocation[0], allocation[1], allocation[2]] = 1
            cost.append(calculate_fitness(schedule_copy))
            valid_tutors.append(tutor)
        if len(cost) == 0:
            continue

        # allocate the lowest cost tutor to that slot, day and room
        lowest_cost_tutor = valid_tutors[cost.index(min(cost))]
        schedule[lowest_cost_tutor, allocation[0], allocation[1], allocation[2]] = 1
        unassigned_tutor_idx.pop(unassigned_tutor_idx.index(lowest_cost_tutor))

    return schedule


def single_swap_neighbourhood(solution, tutor_availability):
    """
    Produce a neighbourhood that contains all feasible swaps from allocations in an existing schedule
    """
    possible_allocations = [
        [slots_idx, day_idx, room_idx]
        for slots_idx in range(NUM_SLOTS)
        for day_idx in range(NUM_DAYS)
        for room_idx in range(NUM_ROOMS)
    ]
    current_allocations = np.where(solution == 1)

    neighbourhood = []
    for i in range(int(solution.sum())):
        current_tutor = current_allocations[0][i]
        current_slot = current_allocations[1][i]
        current_day = current_allocations[2][i]
        current_room = current_allocations[3][i]
        for allocation in possible_allocations:
            neighbour = solution.copy()
            potential_slot = allocation[0]
            potential_day = allocation[1]
            potential_room = allocation[2]

            # if the tutor is unavailable at that slot and day, continue
            # if any tutor is already in that slot, day and room, continue
            # if the tutor is already in a room at that slot and day, continue
            if (
                (tutor_availability[current_tutor, potential_slot, potential_day] == 0)
                or any(neighbour[current_tutor, potential_slot, potential_day])
                or any(neighbour[:, potential_slot, potential_day, potential_room])
            ):
                continue
            # if there is another tutor in the potential location we want to swap to, and our current tutors position is unavailable, continue
            if any(neighbour[:, potential_slot, potential_day, potential_room]):
                potential_tutor = int(
                    np.where(
                        neighbour[:, potential_slot, potential_day, potential_room]
                    )[0]
                )
                if (
                    tutor_availability[potential_tutor, current_slot, current_day] == 0
                    or any(neighbour[potential_tutor, current_slot, current_day])
                    or any(neighbour[:, current_slot, current_day, current_room])
                ):
                    continue

                neighbour[current_tutor, current_slot, current_day, current_room] = 0
                neighbour[
                    current_tutor, potential_slot, potential_day, potential_room
                ] = 1
                neighbour[
                    potential_tutor, potential_slot, potential_day, potential_room
                ] = 0
                neighbour[potential_tutor, current_slot, current_day, current_room] = 1
            else:
                neighbour[current_tutor, current_slot, current_day, current_room] = 0
                neighbour[
                    current_tutor, potential_slot, potential_day, potential_room
                ] = 1

            neighbourhood.append(neighbour)
    return neighbourhood


def select_neighbour(neighbourhood):
    """
    Choose the lowest cost neighbour in the neighbourhood
    """

    costs = []
    for neighbour in neighbourhood:
        costs.append(calculate_fitness(neighbour))

    candidate_solution = neighbourhood[np.argmin(costs)]
    cost = np.min(costs)

    return candidate_solution, cost


def local_search(solution, tutor_availability):
    """
    Produce a local search schedule. Find the best neighbour in the neighbourhood of the current solution.
    If the best neighbour is no better than the current solution, return the current solution.
    Otherwise repeat.
    """
    cost = calculate_fitness(solution)

    while True:
        neighbourhood = single_swap_neighbourhood(solution, tutor_availability)
        candidate_solution, candidate_cost = select_neighbour(neighbourhood)

        if candidate_cost < cost:
            cost = candidate_cost
            solution = candidate_solution
        else:
            break

    return solution, cost


def grasp_algorithm(n_iterations, availability, tutor_class, tutor_availability):
    """
    Run the GRASP algorithm. This involves,
    iteratively finding a greedy solution and perform a random search.
    """
    cost = np.inf
    for i in range(n_iterations):
        print(f"iteration {i}")
        print("random greedy started")
        greedy_random_solution = greedy_randomised_construction(
            availability, tutor_class, tutor_availability
        )

        print("local search started")
        local_search_solution, local_search_cost = local_search(
            greedy_random_solution, tutor_availability
        )

        if local_search_cost < cost:
            cost = local_search_cost
            solution = local_search_solution

    return solution, cost


if __name__ == "__main__":
    n_iterations = 10

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

    solution, cost = grasp_algorithm(
        n_iterations, availability, tutor_class, tutor_availability
    )
    # solution = greedy_randomised_construction(availability, tutor_class, tutor_availability)

    print(is_feasible_schedule(solution, tutor_availability, allocation_num))
    print(f"cost {cost}")
    schedule = print_schedule(solution, days, slots, rooms, availability)
    print(schedule)
