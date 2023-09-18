import numpy as np
import pandas as pd


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
            # print(f'Tutor: {tutor}')

            # Gets all slots and days tutor is available
            possible_allocations = np.where(tutor_availability[tutor] == 1)

            # For each tutor, saves indeces of allocated spaces such that tutor is not scheduled to the same time
            past_indeces = []

            # print(f'Possible Allocations: {len(possible_allocations[0])}')
            # print(f'Number of allocations needed: {allocation_num[tutor]}')

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
                random_room = generate_random_room(available_rooms)

                # If can't allocate room: break and restart the porcess
                if random_room == "No Rooms Available":
                    problem = True
                    # print('No Rooms Available')
                    break

                # Fix so it escapes loop and add while
                x[tutor, random_slot, random_day, random_room] = 1

                past_indeces.append(random_index)
                # print("")

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
