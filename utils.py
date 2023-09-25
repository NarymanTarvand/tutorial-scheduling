import numpy as np
import pandas as pd

from constants import *


def generate_random_index(allocation_number, past_indices):
    # Generates an index that hasn't already been considered
    boolean = True

    while boolean:

        # Generates random index
        random_index = np.random.randint(0, allocation_number)

        # If index has not been considered, that index is returned
        # Otherwise repeat process until a feasible index is found
        if random_index not in past_indices:
            boolean = False

    return random_index


def generate_random_room(rooms, num_rooms):
    # Gets an index of a room that is not occupied
    boolean = True

    # If there are no rooms available, returns -1
    if sum(rooms) == num_rooms:
        return "No Rooms Available"

    # Looks up rooms which are available
    available_rooms = np.where(rooms == 0)

    while boolean:

        # Generates random index
        random_room = np.random.randint(0, num_rooms)

        # If index corresponds to available room, index is returned
        # Otherwise repeat process until a feasible index is found
        if random_room in available_rooms[0]:
            boolean = False

    return random_room


def generate_feasible_schedule(
    num_tutors,
    num_slots,
    num_days,
    num_rooms,
    tutor_availability,
    allocation_num,
    ind_tutors,
):

    feasible = False
    attempts = 1

    while not (feasible):

        problem = False

        x = np.zeros((num_tutors, num_slots, num_days, num_rooms))

        for tutor in range(num_tutors):

            # Gets all slots and days tutor is available
            possible_allocations = np.where(tutor_availability[tutor] == 1)

            # For each tutor, saves indeces of allocated spaces such that tutor is not scheduled to the same time
            past_indeces = []

            # If allocation number greater than possible allocations: problem is infeasable
            if len(possible_allocations[0]) < allocation_num[tutor]:
                print(
                    "Problem is infeasable as number of allocations needed is greater than preference number"
                )
                print("Please review data")
                break

            # Allocates tutor to a room
            for i in range(allocation_num[tutor]):

                # Random index (doesn't double schedule the tutor)
                random_index = generate_random_index(
                    len(possible_allocations[0]), past_indeces
                )

                # Gets the slot and day of randomized index
                random_slot = possible_allocations[0][random_index]
                random_day = possible_allocations[1][random_index]

                # Randomizes room for allocation, and selects a room that is available
                available_rooms = np.apply_over_axes(np.sum, x, ind_tutors)
                available_rooms = available_rooms[0, random_slot, random_day]

                # Gets room that is empty
                random_room = generate_random_room(available_rooms, num_rooms)

                # If can't allocate room: break and restart the porcess
                if random_room == "No Rooms Available":
                    problem = True
                    break

                # Fix so it escapes loop and add while
                x[tutor, random_slot, random_day, random_room] = 1

                past_indeces.append(random_index)

        if problem:
            problem = False
            attempts += 1
        else:
            feasible = True

    return (attempts, x)


def print_schedule(
    instance,
    slots,
    days,
    rooms,
    num_tutors,
    num_slots,
    num_days,
    num_rooms,
    availability,
):
    # Prints out schedule

    # Creates empty schedule
    columns = pd.MultiIndex(
        levels=[days["Day"].values, slots["Slot ID"].values],
        codes=[
            [0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2],
            [0, 1, 2, 3, 4, 0, 1, 2, 3, 4, 0, 1, 2, 3, 4],
        ],
    )
    indeces = rooms["Room ID"].values
    schedule = pd.DataFrame(
        np.zeros((num_rooms, num_days * num_slots)), columns=columns, index=indeces
    )
    schedule = schedule.astype(str)

    # Populates empty schedule with tutors dictated by the decission variable
    for day in range(num_days):
        for room in range(num_rooms):
            for slot in range(num_slots):

                # Finds who is the tutor in that room at that slot at that day
                tutor_index = np.where(instance[:, slot, day, room] == 1)

                # Converts from index form
                day_name = days["Day"][day]
                slot_name = slots["Slot ID"][slot]
                room_name = rooms["Room ID"][room]

                # Populates cell with tutor name, and if no tutor allocated, leaves it empty
                if tutor_index[0].size != 0:
                    # Gets tutor Id
                    tutor_id = availability["Slot"][tutor_index[0]]

                    # Updates schdule
                    schedule.loc[room_name, day_name][slot_name] = tutor_id.values[0]

                else:
                    schedule.loc[room_name, day_name][slot_name] = ""
    return schedule


def total_days_visted_by_tutors(instance):

    # Sums over rooms and slots
    sum_over_rooms_and_slots = np.squeeze(np.sum(instance, axis=(SLOT_IDX, ROOM_IDX)))

    count = 0

    # Iterates over each tutor
    for j in range(NUM_TUTORS):

        # Counts the days a tutor has to teach
        count += np.count_nonzero(sum_over_rooms_and_slots[j])

    return count


def total_rooms_used_in_week(instance):

    # Sums over slots and tutors
    sum_over_tutors_and_slots = np.squeeze(
        np.apply_over_axes(np.sum, instance, [TUTOR_IDX, SLOT_IDX])
    )

    count = 0

    # Iterates over each day
    for j in range(NUM_DAYS):

        # Counts the rooms that are used each day
        count += np.count_nonzero(sum_over_tutors_and_slots[j])

    return count


def tutors_in_idle(instance):

    # Sums over every room
    sum_over_rooms = np.squeeze(np.apply_over_axes(np.sum, instance, ROOM_IDX))

    idle_time = 0

    # Iterates over each tutor and each day
    for t in range(NUM_TUTORS):
        for d in range(NUM_DAYS):

            # Gets each tutor's schedule for a given day
            day_schedule = sum_over_rooms[t, :, d].astype(int)

            # Looks at the slots which have been assign to
            indeces = np.where(day_schedule == 1)[0]

            # Calculates the time tutor is waiting around in between tutorials
            if len(indeces) > 1:

                idle_time += max(indeces) - min(indeces) + 1 - len(indeces)

    return idle_time


def times_tutors_move_rooms_with_b2b_tutorials(instance):

    times_moved = 0

    # Iterates over each tutor over each day
    for t in range(NUM_TUTORS):
        for d in range(NUM_DAYS):

            # Iterates over each slot
            for s in range(NUM_SLOTS - 1):

                # If that tutor is allocated to that slot in that day
                if sum(instance[t, s, d, :] == 1):

                    # Gets what room it is allocated to
                    room_index = np.where(instance[t, s, d, :] == 1)[0]

                    # Check if tutor is allocated on the next slot
                    if sum(instance[t, s + 1, d, :] == 1):

                        # Gets what room it is allocated to next slot
                        next_room_index = np.where(instance[t, s + 1, d, :] == 1)[0]

                        # Penalizes if rooms are not the same
                        if room_index != next_room_index:
                            times_moved += 1

    return times_moved


def calculate_fitness(individual):

    number_of_visits_cost = total_days_visted_by_tutors(individual)
    rooms_used_cost = total_rooms_used_in_week(individual)
    tutors_waiting_cost = tutors_in_idle(individual)
    moving_rooms_cost = times_tutors_move_rooms_with_b2b_tutorials(individual)

    # print(f'Total number of visits = {number_of_visits_cost}')
    # print(f'Total number of rooms used over the week = {rooms_used_cost}')
    # print(f'Total time tutors spend waiting = {tutors_waiting_cost}')
    # print(f'Total amount of times tutors having to moves rooms = {moving_rooms_cost}')

    return (
        number_of_visits_cost
        + rooms_used_cost
        + tutors_waiting_cost
        + moving_rooms_cost
    )


def print_schedule(solution, days, slots, rooms, availability):
    # Prints out schedule

    # Creates empty schedule
    columns = pd.MultiIndex(
        levels=[days["Day"].values, slots["Slot ID"].values],
        codes=[
            [0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2],
            [0, 1, 2, 3, 4, 0, 1, 2, 3, 4, 0, 1, 2, 3, 4],
        ],
    )
    indices = rooms["Room ID"].values
    schedule = pd.DataFrame(
        np.zeros((NUM_ROOMS, NUM_DAYS * NUM_SLOTS)), columns=columns, index=indices
    )
    schedule = schedule.astype(str)

    # Populates empty schedule with tutors dictated by the decission variable
    for day in range(NUM_DAYS):
        for room in range(NUM_ROOMS):
            for slot in range(NUM_SLOTS):

                # Finds who is the tutor in that room at that slot at that day
                tutor_index = np.where(solution[:, slot, day, room] == 1)

                # Converts from index form
                day_name = days["Day"][day]
                slot_name = slots["Slot ID"][slot]
                room_name = rooms["Room ID"][room]

                # Populates cell with tutor name, and if no tutor allocated, leaves it empty
                if tutor_index[0].size != 0:
                    # Gets tutor Id
                    tutor_id = availability["Slot"][tutor_index[0]]

                    # Updates schdule
                    schedule.loc[room_name, day_name][slot_name] = tutor_id.values[0]

                else:
                    schedule.loc[room_name, day_name][slot_name] = ""
    return schedule


def is_feasible_schedule(instance, tutor_availability, allocation_num):

    feasible = True

    # Extends tutor availability by one dimension, to be applied to each room
    A = np.repeat(tutor_availability[:, :, :, np.newaxis], 6, axis=3)

    # Checks instance satisfies tutors availability
    for t in range(NUM_TUTORS):
        for s in range(NUM_SLOTS):
            for d in range(NUM_DAYS):
                for r in range(NUM_ROOMS):

                    if instance[t, s, d, r] > A[t, s, d, r]:
                        feasible = False
                        return feasible

    # Checks tutor is allocated the amount of times it needs to be allocated
    allocated_number = np.squeeze(
        np.apply_over_axes(np.sum, instance, [SLOT_IDX, DAY_IDX, ROOM_IDX])
    )
    for t in range(NUM_TUTORS):
        if allocated_number[t] != allocation_num[t]:
            feasible = False
            return feasible

    # Checks that for each room there is at most room tutpr allocated to
    room_usage = np.squeeze(np.apply_over_axes(np.sum, instance, TUTOR_IDX))

    for s in range(NUM_SLOTS):
        for d in range(NUM_DAYS):
            for r in range(NUM_ROOMS):

                if room_usage[s, d, r] > 1:
                    feasible = False
                    return feasible

    # Checks that a tutor can be at most one room at a time
    tutor_schedule = np.squeeze(np.apply_over_axes(np.sum, instance, ROOM_IDX))

    for t in range(NUM_TUTORS):
        for s in range(NUM_SLOTS):
            for d in range(NUM_DAYS):

                if tutor_schedule[t, s, d] > 1:
                    feasible = False
                    return feasible

    return feasible
