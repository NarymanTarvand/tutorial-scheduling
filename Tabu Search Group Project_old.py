# Tabu Search Algorithm

from Scheduling_Assignment import *
import random
import time

# Set display options to show all rows and columns
pd.set_option('display.max_rows', None)  # Show all rows
pd.set_option('display.max_columns', None)  # Show all columns

# Define your problem-specific data structures and objective function
# You should have a representation of class assignments and a way to calculate the objective value.

# Soft constraints
# Minimise tutor idle time between tutorials

# x_[tutor][slot][day][room]
attempts, x = generate_feasible_schedule()
instance = x

# def tutors_in_idle(instance):
#     # sum over the rooms to see the tutors schedule
#     sum_over_rooms = np.squeeze(np.apply_over_axes(np.sum, instance, ind_rooms))
#
#     idle_time = 0
#     # For a tutor, look at the slots it is assigned to on a day
#     # If the tutor has two or more classes on a day, it could be idle for some time
#     # Penalise the amount of slots that it is waiting around in between
#     for t in range(num_tutors):
#         for d in range(num_days):
#             # Gets each tutor's schedule for a given day
#             # An array with element for each slot, 1 if used
#             day_schedule = sum_over_rooms[t, :, d].astype(int)
#             # check where the slots are assigned
#             slot_index = np.where(day_schedule == 1)[0]
#             # Calculates the time tutor is waiting around in between tutorials
#             if len(slot_index) > 1:
#                 # getting the idle time
#                 idle_time += max(slot_index) - min(slot_index) + 1 - len(slot_index)
#         return idle_time
#
# # If a tutor has back to back classes, keep them in the same room
# def times_tutors_move_rooms_with_b2b_tutorials(instance):
#     times_moved = 0
#
#     # Iterates over each tutor over each day
#     for t in range(num_tutors):
#         for d in range(num_days):
#
#             # Iterates over each slot
#             for s in range(num_slots - 1):
#
#                 # If that tutor is allocated to that slot in that day
#                 if sum(instance[t, s, d, :] == 1):
#                     # Gets what room it is allocated to
#                     room_index = np.where(instance[t, s, d, :] == 1)[0]
#                     # Check if tutor is allocated on the next slot
#                     if sum(instance[t, s + 1, d, :] == 1):
#                         # Gets what room it is allocated to next slot
#                         next_room_index = np.where(instance[t, s + 1, d, :] == 1)[0]
#                         # Penalizes if rooms are not the same
#                         if room_index != next_room_index:
#                             times_moved += 1
#     return times_moved
#
# # Minimise amount of days tutor comes in to teach
# def total_days_visted_by_tutors(instance):
#     # For each tutor, look how many days it is assigned to
#     # Sum over the rooms and slots
#     # below returns a 21 * 3 matrix with entries with the amount of times a tutor is scheduled that day
#     sum_over_rooms_and_slots = np.squeeze(np.apply_over_axes(np.sum, instance, [ind_slots, ind_rooms]))
#     # Then for each tutor, see whether we have a non-zero value for that day
#     count = 0
#     # Iterates over each tutor
#     for tutor in range(num_tutors):
#         # Counts the days a tutor has to teach - we want to minimise this
#         count += np.count_nonzero(sum_over_rooms_and_slots[tutor])
#     return count
#
# # Minimise the amount of rooms used per day
# def total_rooms_used_in_week(instance):
#     # for each day, see how many rooms are used
#     # sum over tutors and slots
#     # below returns a 3*6 matrix with entries representing the amount of times that room was used that day
#     sum_over_tutors_and_slots = np.squeeze(np.apply_over_axes(np.sum, instance, [ind_tutors, ind_slots]))
#     count = 0
#     # Iterates over each day
#     for day in range(num_days):
#         # Counts the rooms that are used each day - we want to minimise this
#         count += np.count_nonzero(sum_over_tutors_and_slots[day])
#     return count

def fitness(solution):
    # Include the values for all of our soft constraints
    number_of_visits_cost = total_days_visted_by_tutors(solution)
    rooms_used_cost = total_rooms_used_in_week(solution)
    tutors_waiting_cost = tutors_in_idle(solution)
    moving_rooms_cost = times_tutors_move_rooms_with_b2b_tutorials(solution)
    return number_of_visits_cost + rooms_used_cost + tutors_waiting_cost + moving_rooms_cost

def neighbour_slot_swap(sol):
    # This swaps time slots but keeps day and room the same
    # Pick a random day. Randomly select two different timeslots that have been assigned to tutors
    # Check if the tutors are available at the opposite times
    # Swap them keeping room constant
    # Picking a random day
    day_ind = random.randint(0, num_days - 1)
    # getting the tutor, slot and rooms allocated for that day
    tutor_ids, slot_ids, room_ids = np.where(sol[:, :, day_ind, :] == 1)
    # pick two tutors that have different slot IDs
    while True:
        tutor_1_index = random.randint(0, len(tutor_ids) - 1)
        tutor1 = tutor_ids[tutor_1_index]
        tutor1_slot, tutor1_room = slot_ids[tutor_1_index], room_ids[tutor_1_index]
        tutors_with_different_slots = [[ind, tutor] for ind, tutor in enumerate(tutor_ids) if
                                       tutor != tutor1 and slot_ids[ind] != slot_ids[tutor_1_index]]
        if len(tutors_with_different_slots) == 0:
            # restart the while loop if we don't have any tutors
            continue

        [tutor_2_index, tutor2] = random.choice(tutors_with_different_slots)
        tutor2_slot, tutor2_room = slot_ids[tutor_2_index], room_ids[tutor_2_index]
        # Check if the tutors are available at the opposite times
        if tutor_availability[tutor1, tutor2_slot, day_ind] == 1 and \
                tutor_availability[tutor2, tutor1_slot, day_ind] == 1:
            # we have found our two tutors
            break

    # Get rid of old allocations
    sol[tutor1, tutor1_slot, day_ind, tutor1_room] = 0
    sol[tutor2, tutor2_slot, day_ind, tutor2_room] = 0
    # Make new allocations - swaps slots, keep room and tutor
    sol[tutor1, tutor2_slot, day_ind, tutor1_room] = 1
    sol[tutor2, tutor1_slot, day_ind, tutor2_room] = 1
    tutor_1 = availability['Slot'][tutor1]
    tutor_2 = availability['Slot'][tutor2]
    slot_1 = slots['Slot ID'][tutor1_slot]
    slot_2 = slots['Slot ID'][tutor2_slot]
    day_name = days['Day'][day_ind]
    print(f"{tutor_1} swapped into {slot_2} and {tutor_2} swapped into {slot_1} on {day_name}")
    return sol

def neighbour_room_swap(sol):
    # This swaps rooms but keeps day and timeslot the same
    # Pick a random day and timeslot
    # We know that tutors are available in this time
    # We also know the rooms aren't the same
    # Swap the rooms of two of the tutors assigned to this time
    # Picking a random day
    while True:
        day_ind = random.randint(0, num_days - 1)
        slot_ind = random.randint(0, num_slots - 1)
        # getting the tutor, slot and rooms allocated for that day
        tutor_ids, room_ids = np.where(sol[:, slot_ind, day_ind, :] == 1)
        if len(tutor_ids) > 2:
            # We have enough tutors in a timeslot to swap. Don't need to pick another slot and day
            break

    tutor_1_index, tutor_2_index = random.sample(range(len(tutor_ids)), 2)
    tutor1 = tutor_ids[tutor_1_index]
    tutor1_room = room_ids[tutor_1_index]
    tutor2 = tutor_ids[tutor_2_index]
    tutor2_room = room_ids[tutor_2_index]
    # Check if the tutors are available at the opposite times

    # Get rid of old allocations
    sol[tutor1, slot_ind, day_ind, tutor1_room] = 0
    sol[tutor2, slot_ind, day_ind, tutor2_room] = 0
    # Make new allocations - swaps slots, keep room and tutor
    sol[tutor1, slot_ind, day_ind, tutor2_room] = 1
    sol[tutor2, slot_ind, day_ind, tutor1_room] = 1
    tutor_1 = availability['Slot'][tutor1]
    tutor_2 = availability['Slot'][tutor2]
    room_1 = rooms['Room ID'][tutor1_room]
    room_2 = rooms['Room ID'][tutor2_room]
    day_name = days['Day'][day_ind]
    slot_name = slots['Slot ID'][slot_ind]
    print(f"{tutor_1} swapped into {room_2} and {tutor_2} swapped into {room_1} on {day_name} in slot {slot_name}")
    return sol

def neighbour_day_swap(sol):
    # This function can get stuck - should set a certain timer to say that if it's taking too long, just return sol
    # But sometimes it spits it out quickly, if it can be found

    # This swaps days but keeps time slot and room the same
    # Randomly select two days
    # Swap two classes that are assigned to the same time slot and room - if the tutor is available
    # I choose to consider only feasible solutions
    start_time = time.time()
    time_limit = 1 # if the algorithm is running longer than this, we won't get a solution
    while True:
        # randomly picking two days
        # Monday has barely any options... can be a problem and add to the run time
        day_1, day_2 = random.sample(range(num_days), 2)
        # getting the tutor, slot and rooms allocated for each
        # getting tutors that have the same room and slot combo
        while True:
            # finding our tutors
            tutor_ids_d1, slot_ids_d1, room_ids_d1 = np.where(sol[:, :, day_1, :] == 1)
            tutor_ids_d2, slot_ids_d2, room_ids_d2 = np.where(sol[:, :, day_2, :] == 1)
            matching_tutors = []
            slot_room = []
            matching_indices = np.where((slot_ids_d1[:, None] == slot_ids_d2) & (room_ids_d1[:, None] == room_ids_d2))

            # Get matching tutor indexes and slot/room values
            matching_tutors = list(zip(matching_indices[0], matching_indices[1]))
            slot_room = list(zip(slot_ids_d1[matching_indices[0]], room_ids_d1[matching_indices[0]]))

            # for i in range(len(slot_ids_d1)):
            #     for j in range(len(slot_ids_d2)):
            #         if slot_ids_d1[i] == slot_ids_d2[j] and room_ids_d1[i] == room_ids_d2[j]:
            #             # If slot and room values match for both days, add tutor indexes to the list
            #             matching_tutors.append((i, j))
            #             slot_room.append((slot_ids_d1[i], room_ids_d1[i]))
            elapsed_time = time.time() - start_time
            if elapsed_time > time_limit:
                print("Time limit exceeded. Stopping the algorithm.")
                # We won't find a new solution doing this swapping, so just return original sol
                return None

            if len(matching_tutors) > 0:
                # we have found a matching slot/room combo
                break
        # checking the tutors are both available on those days at those times
        tutors_ind = random.randint(0, len(matching_tutors) - 1)
        tutors = matching_tutors[tutors_ind]
        tutor1 = tutor_ids_d1[tutors[0]]
        tutor2 = tutor_ids_d2[tutors[1]]
        same_slot = slot_room[tutors_ind][0]
        same_room = slot_room[tutors_ind][1]
        # Check if the tutors are available at the opposite days
        # This can increase the run time a lot... sometimes it is quick but other times it struggles to get
        # available slots
        if tutor_availability[tutor1, same_slot, day_2] == 1 and \
                tutor_availability[tutor2, same_slot, day_1] == 1:
            # we have found our two tutors
            break

    # Get rid of old allocations
    sol[tutor1, same_slot, day_1, same_room] = 0
    sol[tutor2, same_slot, day_2, same_room] = 0
    # Make new allocations - swaps slots, keep room and tutor
    sol[tutor1, same_slot, day_2, same_room] = 1
    sol[tutor2, same_slot, day_1, same_room] = 1
    tutor_1 = availability['Slot'][tutor1]
    tutor_2 = availability['Slot'][tutor2]
    slot = slots['Slot ID'][same_slot]
    room = rooms['Room ID'][same_room]
    day_1 = days['Day'][day_1]
    day_2 = days['Day'][day_2]
    print(f"{tutor_1} swapped into {day_2} and {tutor_2} swapped into {day_1} in {same_slot} and {same_room}")
    return sol

def neighbors(sol, num_neighbours=10):
    # creating a neighbourhood from the current solution
    # I create 10 neighbours
    # WE COULD HAVE CLASHES WITH ROOMS! AND TUTORS COULD ALREADY BE ASSIGNED AT THAT TIME!
    neighbors = []
    count = 0
    while len(neighbors) < num_neighbours:
        count +=1
        # 10 neighbours - but may be different if the day swap algo works or not
        swap_function = random.choice([neighbour_room_swap, neighbour_slot_swap, neighbour_day_swap])
        neighbor = swap_function(sol)

        # Check if the neighbor is feasible
        # Sometimes day swap returns None if it can't find a sol, so don't include that
        if neighbor is not None and is_feasible_schedule(sol):
            neighbors.append(neighbor)
    print(count)
    return neighbors

def tabu_search(max_iterations, tabu_list_size):
    # Use silvestre's algorithm to generate a starting sol
    _, current_solution = generate_feasible_schedule()
    best_solution = current_solution
    best_solution_value = fitness(current_solution)
    tabu_list = []

    for iteration in range(max_iterations):
        neighborhood = neighbors(current_solution)
        best_neighbor = None
        best_neighbor_value = float('inf')

        for neighbor in neighborhood:
            if neighbor not in tabu_list:
                neighbor_value = fitness(neighbor)
                if neighbor_value < best_neighbor_value:
                    best_neighbor = neighbor
                    best_neighbor_value = neighbor_value

        if best_neighbor is not None:
            current_solution = best_neighbor
            tabu_list.append(best_neighbor)

            if best_neighbor_value < best_solution_value:
                best_solution = best_neighbor
                best_solution_value = best_neighbor_value

            if len(tabu_list) > tabu_list_size:
                # remove the oldest entry
                tabu_list.pop(0)

        print(f"Iteration {iteration + 1}/{max_iterations} - Best Value: {best_solution_value}")

    return best_solution, best_solution_value

print(tabu_search(5, 10))
