import random
import math
import sys

#calculates cost of a given "route." If two nodes in that route are connected, do nothing,
#otherwise cost increases by 1 per disconnection
def cost(route):
    cost = 0
    for i in range(1, len(route)):
        if route[i] in graph[route[i - 1]]:
            # print(f'{path[i - 1]} is connected to {path[i]}')
            continue
        else:
            cost += 1
    return cost

#helper for rearranging connected sections--this helps the perturbing function that rearranges connected sections
def rearrange_graph(intervals, original_placement, longer_than_three):
    #only rearrange if we have more than three sections in the state that are connected
    if longer_than_three:
        new_random_list = intervals[1:-1].copy()

        #randomly select two connected segments to swap
        random_first = random.randint(0, len(new_random_list)-1)
        random_second = random.randint(0, len(new_random_list)-1)
        random_second_interval = new_random_list[random_second]
        random_first_interval = new_random_list[random_first]

        new_random_list[random_second] = random_first_interval
        new_random_list[random_first] = random_second_interval
        new_random_list.insert(0, intervals[0])
        new_random_list.append(intervals[-1])
        new_graph = []
        #create a new graph given the rearranged intervals
        for interval in new_random_list:
            start = interval[0]
            end = interval[1]
            while start <= end:
                new_graph.append(original_placement[start])
                start += 1
    #we can't really swap if there are only two connected parts, so do nothing
    else:
        new_graph = original_placement
    return new_graph

#helper for rearranging connected sections -- returns a list of intervals for all the sections that are connected
def calc_paths(segment):
    connected_count = 1
    segment_start = 0
    segment_next = segment_start + 1
    interval_list = []
    while segment_next <= len(segment):
        connected_count += 1
        current_interval = [segment_start]
        segment_end = segment_start
        while segment_next <= len(segment)-1 and segment[segment_next] in graph[segment[segment_start]]:
            segment_start += 1
            segment_next += 1
            segment_end += 1
        current_interval.append(segment_end)
        interval_list.append(current_interval)
        segment_start += 1
        segment_next += 1
    # don't want to impact starting or end vertices
    #after we find the connected intervals, call a function to rearrange the intervals and return a new state
    if len(interval_list) > 3:
        new_graph = rearrange_graph(interval_list, segment, True)
    else:
        new_graph = rearrange_graph(interval_list, segment, False)
    return new_graph


#this is the actually annealing function -- takes an initial route state, intitial temperature, and iteration_stop
#basically the number of iterations it completes before halting
def anneal(route, initial_temperature, iteration_stop):
    worse_move_made = 0
    print(f'Intitial random placement is: {route}')
    best = route
    iterations = 0
    initial_temp = initial_temperature
    while iterations < iteration_stop:
        #random number for calculating probability of taking a worse option
        random_num = random.random()
        temperature = initial_temp / float(iterations + 1)
        #calculated temperature and iterated +2
        iterations += 2

        #if random number greater than 1/5 in range [0,1], then do the 2-OPT perturbation below
        if random.random() > float(1/5):
            for i in range(1, len(route) - 2):
                for j in range(i + 1, len(route)):
                    if j - i == 1: continue  # changes nothing, skip then
                    new_route = route[:]
                    new_route[i:j] = route[j - 1:i - 1:-1]  # this is the 2woptSwap
                    d = (cost(best) - cost(new_route))*.4

                    if cost(new_route) <= cost(best):
                        best = new_route
                    #small chance we select a less than optimal change
                    elif d <= -1 and (random_num < math.exp(d/temperature)):
                        worse_move_made += 1
                        best = new_route

        ##if random number less than 1/5 in range [0,1], then perturb by rearranging two connected components
        else:
            potential_rearranegment = calc_paths(route)
            d = (cost(best) - cost(potential_rearranegment))*.4
            if cost(potential_rearranegment) < cost(best):
                best = potential_rearranegment

            #small chance we select a less than optimal change
            elif d <= -1 and (random_num < math.exp(d / temperature)):
                worse_move_made += 1
                best = potential_rearranegment
        route = best
    best_path_cost = cost(best)

    print(f'Number of worse moves made: {worse_move_made}')
    return best

#this keeps the same node but ranomizes the internal nodes
initial_temperature = int(sys.argv[1])
iteration_stop = int(sys.argv[2])
print(f'Iterations: {iteration_stop}')
graph_name = sys.argv[3]


# 12 sample graphs

if graph_name == "graph_1":
    graph = {0: [1, 4], 1: [0, 2, 5], 2: [1, 3, 6], 3: [2, 7], 4: [0, 5, 8], 5: [1, 4, 6, 9],
               6: [2, 5, 7, 10], 7: [3, 6, 11], 8: [4, 9, 12], 9: [5, 8, 10, 13], 10: [6, 9, 11, 14],
               11: [7, 10, 15], 12: [8, 13], 13: [9, 12, 14], 14: [10, 13, 15], 15: [11, 14]}
    vertices = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15]

if graph_name == "graph_2":
    graph = {0: [1, 10, 11, 19], 1: [0, 2, 11, 12], 2: [1, 3, 11, 12], 3: [2, 4, 12, 13], 4: [3, 5, 13, 14],
             5: [4, 6, 13, 14],
             6: [5, 7, 14, 15], 7: [6, 8, 15, 16], 8: [7, 9, 16, 17], 9: [8, 10, 17, 18], 10: [0, 9, 18, 19],
             11: [0, 1, 2, 19],
             12: [1, 2, 3, 13], 13: [3, 4, 5, 12], 14: [4, 5, 6, 15], 15: [6, 7, 14, 16], 16: [7, 8, 15, 17],
             17: [8, 9, 16, 18],
             18: [9, 10, 17, 19], 19: [0, 10, 11, 18]}
    vertices = [0, 1, 2, 3,4,5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15,16,17,18]

if graph_name == "graph_3":
    graph = {0: [1, 3, 5], 1: [0, 2, 5], 2: [1, 6, 7], 3: [0, 4, 8], 4: [0, 3, 5, 8], 5: [1, 4, 6, 9],
             6: [2, 5, 7, 10],
             7: [2, 6, 10], 8: [3, 4, 9], 9: [5, 8, 10], 10: [6, 7, 9]}
    vertices = [0, 1, 2, 3,4,5, 6, 7, 8, 9, 10]

if graph_name == "graph_4":
    graph = {0: [1, 3, 4, 5], 1: [0, 2, 5, 9], 2: [1, 3, 9, 10], 3: [0, 2, 4, 10], 4: [0, 3, 7, 11], 5: [0, 1, 6, 7], 6: [5, 7, 8, 9],
           7: [4, 5, 6, 11], 8: [6, 9, 10, 11], 9: [1, 2, 6, 8], 10: [2, 3, 8, 11], 11: [4, 7, 8, 10]}
    vertices = [0, 1, 2, 3,4,5, 6, 7, 8, 9, 10,11]

if graph_name == "graph_5":
    graph = {0: [1, 4, 6, 9], 1: [0, 2, 5, 7], 2: [1, 3, 6, 8], 3: [2, 4, 7, 9], 4: [0, 3, 5, 8], 5: [1, 4, 10],
     6: [0, 2, 10],
     7: [1, 3, 10], 8: [2, 4, 10], 9: [0, 3, 10], 10: [5, 6, 7, 8, 9]}
    vertices = [0, 1, 2, 3,4,5, 6, 7, 8, 9, 10]

if graph_name == "graph_6":
    graph = {0: [1, 4, 13], 1: [0, 2, 11], 2: [1, 3, 9], 3: [2, 4, 7], 4: [0, 3, 5], 5: [4, 6, 14], 6: [5, 7, 16],
             7: [3, 6, 8],
             8: [7, 9, 17], 9: [2, 8, 10], 10: [9, 11, 18], 11: [1, 10, 12], 12: [11, 13, 19], 13: [0, 12, 14],
             14: [5, 13, 15],
             15: [14, 16, 19], 16: [6, 15, 17], 17: [8, 16, 18], 18: [10, 17, 19], 19: [12, 15, 18]}
    vertices = [0, 1, 2,3,4,5, 6, 7, 8, 9, 10,11,12,13,14,15,16,17,18,19]

if graph_name == "graph_7":
    graph = {0: [1, 5, 7], 1: [0, 2, 7], 2: [1, 3, 8], 3: [2, 4, 8], 4: [3, 5, 6], 5: [0, 4, 6], 6: [4, 5, 11],
             7: [0, 1, 10],
             8: [2, 3, 9], 9: [8, 10, 11], 10: [7, 9, 11], 11: [6, 9, 10]}
    vertices = [0, 1, 2, 3,4,5, 6, 7, 8, 9, 10,11]

if graph_name == "graph_8":
    graph = {0: [1, 7, 8], 1: [0, 2, 9], 2: [1, 3, 9], 3: [2, 4, 10], 4: [3, 5, 10], 5: [4, 6, 11], 6: [5, 7, 11], 7: [0, 6, 8],
           8: [0, 7, 12], 9: [1, 2, 16], 10: [3, 4, 19], 11: [5, 6, 23], 12: [8, 13, 14], 13: [12, 14, 15], 14: [12, 13, 22],
           15: [13, 16, 17], 16: [9, 15, 17], 17: [15, 16, 18], 18: [17, 19, 20], 19: [10, 18, 20], 20: [18, 19, 21], 21: [10, 22, 13],
           22: [14, 21, 23], 23: [11, 21, 22]}
    vertices = [0, 1, 2, 3,4,5, 6, 7, 8, 9, 10,11,12,13,14,15,16,17,18,19,20,21,22,23]

if graph_name == "graph_9":
    graph = {0: [1, 3, 4], 1: [0, 3, 7], 2: [1, 3, 10], 3: [0, 2, 13], 4: [0, 5, 15], 5: [4, 6, 16], 6: [5, 7, 17],
             7: [1, 6, 8],
             8: [7, 9, 17], 9: [8, 10, 18], 10: [2, 9, 11], 11: [10, 12, 18], 12: [11, 13, 19], 13: [3, 12, 14],
             14: [13, 15, 19],
             15: [4, 14, 16], 16: [5, 15, 20], 17: [6, 8, 21], 18: [9, 11, 22], 19: [12, 14, 23], 20: [16, 21, 23],
             21: [17, 20, 22],
             22: [18, 21, 23], 23: [19, 20, 22]}
    vertices = [0, 1, 2, 3,4,5, 6, 7, 8, 9, 10,11,12,13,14,15,16,17,18,19,20,21,22,23]

if graph_name == "graph_10":
    graph = {0: [1, 2, 3], 1: [0, 2, 4], 2: [0, 1, 5], 3: [0, 10, 11], 4: [1, 6, 7], 5: [2, 8, 9], 6: [4, 7, 11], 7: [4, 6, 9], 8: [5, 9, 10],
           9: [5, 7, 8], 10: [3, 8, 11], 11: [3, 6, 10]}
    vertices = [0, 1, 2, 3,4,5, 6, 7, 8, 9, 10,11]

if graph_name == "graph_11":
    graph = graph = {0: [1, 2, 3, 4, 5], 1: [0, 2, 3, 4], 2: [0, 1, 3], 3: [0, 1, 2], 4: [0, 1, 5], 5: [0, 4]}
    vertices = [0, 1, 2, 3,4,5]

if graph_name == "graph_12":
    graph = graph = {0: [1, 4, 5], 1: [0, 2, 7], 2: [1, 3, 8], 3: [2, 4, 9], 4: [0, 3, 11], 5: [0, 6, 11], 6: [5, 7, 10], 7: [1, 6, 8], 8: [2, 7, 9],
           9: [3, 8, 10], 10: [6, 9, 11], 11: [4, 5, 10]}
    vertices = [0, 1, 2, 3,4,5, 6, 7, 8, 9, 10,11]

print(f'Calling Simulated Annealing with Iterations: {iteration_stop} and Temperature: {initial_temperature}\n')
# this randomizes the start/end nodes
local_maxima = 0
global_maxima = 0
for i in range(len(vertices)):
    print(f'Start/End Vertex: {vertices[i]}')
    start_end = vertices.pop(i)
    random_start = random.sample(vertices, len(vertices))
    random_start.insert(0, start_end)
    random_start.append(start_end)
    # print(random_start)
    vertices.insert(i, start_end)

    best_path = anneal(random_start, initial_temperature, iteration_stop)
    best_path_cost = cost(best_path)
    if best_path_cost > 0:
        local_maxima += 1
        print(f'Found local minima, cost: {best_path_cost}, {best_path}\n ')
    else:
        global_maxima += 1
        print(f'Found global minimum, cost: {best_path_cost}, {best_path}\n')
print(f'Global Minima: {global_maxima} Local Minima: {local_maxima}')




