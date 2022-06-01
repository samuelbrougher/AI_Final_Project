import random
import sys

# using adjacency list representation

class Graph:

    def __init__(self, vertices, graph):
        self.graph = graph
        # No. of vertices
        self.Vertices = vertices
        self.counter = 0
        self.backtrack = 0
        self.big_counter = 0
        self.min_max_connections = self.find_connectivity()
        self.max_conncted_vertex = self.min_max_connections[1]
        self.min_conncted_vertex = self.min_max_connections[0]
        self.bfs = self.distance_from_origin(self.max_conncted_vertex)
        self.start_vertex = 0
        self.average_none_backtracks = 0

    #helper for round trip heuristic -- finds distance from the origin to some node, which we then use to make decisions about node choices
    def distance_from_origin(self, origin):
        queue = []
        distance_from_origin_map = {}
        distance_from_origin_map[origin] = 0
        visited_nodes = set()
        visited_nodes.add(origin)
        queue.append(origin)
        while queue:
            visiting = queue.pop(0)
            for neighbor in self.graph[visiting]:
                if neighbor not in visited_nodes:
                    distance_from_origin_map[neighbor] = distance_from_origin_map[visiting] + 1
                    queue.append(neighbor)
                    visited_nodes.add(neighbor)
        self.bfs = distance_from_origin_map
        return distance_from_origin_map

    #this calculates the "unreachable heuristic"--basically you don't want to go to a vertex if it's connected to a vertex
    #that only has one connections--this avoids dead ends
    def unreachable_heuristic(self, node, path_visited):
        # look through each node we could potentially visit and count it's available connections (unvisited nodes)
        new_dict = {}
        for potential_node in self.graph[node]:
            #now look at nodes attached to that node
            for next_node in self.graph[potential_node]:
                #check if it has greater than one potential connection available
                num_available_connections = set(self.graph[next_node]).difference(set(path_visited))
                new_dict[potential_node] = len(num_available_connections)
                if len(num_available_connections) == 1:
                    new_dict[potential_node] = float('-inf')
        sorted_dict = dict(sorted(new_dict.items(), key=lambda item: item[1]))
        return sorted_dict

    #order nodes by proximity unvisited nodes--neccesary for cheeseman
    #this function checks the connections of potential nodes to visit to allow us to visit nodes with more connections first--highest connectivity first
    def sort_edges(self, node, path_so_far):
        visited_set = set(path_so_far)
        #look through each node we could potentially visit and count it's available connections (unvisited nodes)
        new_dict = {}
        for exploring_node in self.graph[node]:
            num_connecting = len(set(self.graph[exploring_node]).difference(visited_set))
            new_dict[exploring_node] = num_connecting

        sorted_dict = dict(sorted(new_dict.items(), key=lambda item: item[1]))
        sorted_vertex_list = (list(sorted_dict.keys())[::-1])
        return sorted_vertex_list

    #sort with lowest connectivity first--i.e. first nodes in the returned list will have lower connectivity than later in list
    def sort_edges_low_order(self, node, path_so_far):
        visited_set = set(path_so_far)
        #look through each node we could potentially visit and count it's available connections (unvisited nodes)
        new_dict = {}
        for exploring_node in self.graph[node]:
            num_connecting = len(set(self.graph[exploring_node]).difference(visited_set))
            new_dict[exploring_node] = num_connecting
        sorted_dict = dict(sorted(new_dict.items(), key=lambda item: item[1]))
        sorted_vertex_list = (list(sorted_dict.keys()))
        return sorted_vertex_list


    #this is to help calculate our own "round trip" heuristic--if we have a path constructed with only half available
    #nodes visited, we privilege nodes that are "farther" from the origin. Once we pass the half-way threshold, then we
    #privilege nodes that are returning to the origin
    def sort_edges_heuristic(self, node, path_so_far):
        vertex_count = len(path_so_far)
        #look through each node we could potentially visit and count it's available connections (unvisited nodes)
        new_dict = {}
        #go through nodes and order based on their distance from the origin
        for exploring_node in self.graph[node]:
            new_dict[exploring_node] = self.bfs[exploring_node]
        sorted_dict = dict(sorted(new_dict.items(), key=lambda item: item[1]))
        sorted_answer = (list(sorted_dict.keys())[::-1])
        if vertex_count / self.Vertices > .5:
            sorted_answer = sorted_answer[::-1]
        return sorted_answer



    #this is the actual backtracking algorithm
    def backtrack_function(self, u, d, visited_set, path, heuristic):
        self.backtrack += 1
        # Mark the current node as visited and store in path
        path.append(u)
        # If current vertex is same as destination, and the list is long enough (i.e. complete) then print
        if len(path) == self.Vertices + 1 and u == d:
            self.big_counter += 1
            self.counter += 1
            self.average_none_backtracks += self.backtrack
            self.backtrack += self.big_counter

            print(f'#{self.counter} {path} Backtracks: {self.backtrack}')

        else:
            # If current vertex is not destination
            # Recur for all the vertices adjacent to this vertex, but first order the possible
            #next visits according to the appropriate heuristic
            if heuristic == "cheeseman":
                self.graph[u] = self.sort_edges(u, path)
            if heuristic == "horn":
                self.graph[u] = self.sort_edges_low_order(u, path)
            if heuristic == "round_trip":
                self.graph[u] = self.sort_edges_heuristic(u, path)
            if heuristic == "unreachable_heuristic":
                self.graph[u] = self.unreachable_heuristic(u, path)
            if heuristic == "none":
                heuristic = "none"
            for i in self.graph[u]:
                if i not in path or len(path) == self.Vertices:
                    self.backtrack_function(i, d, visited_set, path, heuristic)
        path.pop()


    # Prints all paths from start to destination
    def printPaths(self, s, d, heuristic):
        # Mark all the vertices as not visited
        visited_set = set()
        # Create an array to store paths
        path = []
        # Call the recursive helper function to print all paths
        self.backtrack_function(s, d, visited_set, path, heuristic)

    #finds the min and max connected vertices in order to help our heuristics
    def find_connectivity(self):
        max_connectivity, min_connectivity = len(self.graph[1]), len(self.graph[1])
        max_connection, min_connection = 1,1
        for i in range(2, self.Vertices):
            if len(self.graph[i]) > max_connectivity:
                max_connectivity = len(self.graph[i])
                max_connection = i
            if len(self.graph[i]) < min_connectivity:
                min_connectivity = len(self.graph[i])
                min_connection = i
        return [min_connection, max_connection]


if __name__ == '__main__':

    #getting input
    heuristic = (sys.argv[1])
    graph_name = (sys.argv[2])

    # 12 sample graphs
    if graph_name == "graph_1":
        graph = {0: [1, 4], 1: [0, 2, 5], 2: [1, 3, 6], 3: [2, 7], 4: [0, 5, 8], 5: [1, 4, 6, 9],
                 6: [2, 5, 7, 10], 7: [3, 6, 11], 8: [4, 9, 12], 9: [5, 8, 10, 13], 10: [6, 9, 11, 14],
                 11: [7, 10, 15], 12: [8, 13], 13: [9, 12, 14], 14: [10, 13, 15], 15: [11, 14]}

    if graph_name == "graph_2":
        graph = {0: [1, 10, 11, 19], 1: [0, 2, 11, 12], 2: [1, 3, 11, 12], 3: [2, 4, 12, 13], 4: [3, 5, 13, 14],
                 5: [4, 6, 13, 14],
                 6: [5, 7, 14, 15], 7: [6, 8, 15, 16], 8: [7, 9, 16, 17], 9: [8, 10, 17, 18], 10: [0, 9, 18, 19],
                 11: [0, 1, 2, 19],
                 12: [1, 2, 3, 13], 13: [3, 4, 5, 12], 14: [4, 5, 6, 15], 15: [6, 7, 14, 16], 16: [7, 8, 15, 17],
                 17: [8, 9, 16, 18],
                 18: [9, 10, 17, 19], 19: [0, 10, 11, 18]}

    if graph_name == "graph_3":
        graph = {0: [1, 3, 5], 1: [0, 2, 5], 2: [1, 6, 7], 3: [0, 4, 8], 4: [0, 3, 5, 8], 5: [1, 4, 6, 9],
                 6: [2, 5, 7, 10],
                 7: [2, 6, 10], 8: [3, 4, 9], 9: [5, 8, 10], 10: [6, 7, 9]}

    if graph_name == "graph_4":
        graph = {0: [1, 3, 4, 5], 1: [0, 2, 5, 9], 2: [1, 3, 9, 10], 3: [0, 2, 4, 10], 4: [0, 3, 7, 11],
                 5: [0, 1, 6, 7], 6: [5, 7, 8, 9],
                 7: [4, 5, 6, 11], 8: [6, 9, 10, 11], 9: [1, 2, 6, 8], 10: [2, 3, 8, 11], 11: [4, 7, 8, 10]}

    if graph_name == "graph_5":
        graph = {0: [1, 4, 6, 9], 1: [0, 2, 5, 7], 2: [1, 3, 6, 8], 3: [2, 4, 7, 9], 4: [0, 3, 5, 8], 5: [1, 4, 10],
                 6: [0, 2, 10],
                 7: [1, 3, 10], 8: [2, 4, 10], 9: [0, 3, 10], 10: [5, 6, 7, 8, 9]}

    if graph_name == "graph_6":
        graph = {0: [1, 4, 13], 1: [0, 2, 11], 2: [1, 3, 9], 3: [2, 4, 7], 4: [0, 3, 5], 5: [4, 6, 14], 6: [5, 7, 16],
                 7: [3, 6, 8],
                 8: [7, 9, 17], 9: [2, 8, 10], 10: [9, 11, 18], 11: [1, 10, 12], 12: [11, 13, 19], 13: [0, 12, 14],
                 14: [5, 13, 15],
                 15: [14, 16, 19], 16: [6, 15, 17], 17: [8, 16, 18], 18: [10, 17, 19], 19: [12, 15, 18]}

    if graph_name == "graph_7":
        graph = {0: [1, 5, 7], 1: [0, 2, 7], 2: [1, 3, 8], 3: [2, 4, 8], 4: [3, 5, 6], 5: [0, 4, 6], 6: [4, 5, 11],
                 7: [0, 1, 10],
                 8: [2, 3, 9], 9: [8, 10, 11], 10: [7, 9, 11], 11: [6, 9, 10]}

    if graph_name == "graph_8":
        graph = {0: [1, 7, 8], 1: [0, 2, 9], 2: [1, 3, 9], 3: [2, 4, 10], 4: [3, 5, 10], 5: [4, 6, 11], 6: [5, 7, 11],
                 7: [0, 6, 8],
                 8: [0, 7, 12], 9: [1, 2, 16], 10: [3, 4, 19], 11: [5, 6, 23], 12: [8, 13, 14], 13: [12, 14, 15],
                 14: [12, 13, 22],
                 15: [13, 16, 17], 16: [9, 15, 17], 17: [15, 16, 18], 18: [17, 19, 20], 19: [10, 18, 20],
                 20: [18, 19, 21], 21: [10, 22, 13],
                 22: [14, 21, 23], 23: [11, 21, 22]}

    if graph_name == "graph_9":
        graph = {0: [1, 3, 4], 1: [0, 3, 7], 2: [1, 3, 10], 3: [0, 2, 13], 4: [0, 5, 15], 5: [4, 6, 16], 6: [5, 7, 17],
                 7: [1, 6, 8],
                 8: [7, 9, 17], 9: [8, 10, 18], 10: [2, 9, 11], 11: [10, 12, 18], 12: [11, 13, 19], 13: [3, 12, 14],
                 14: [13, 15, 19],
                 15: [4, 14, 16], 16: [5, 15, 20], 17: [6, 8, 21], 18: [9, 11, 22], 19: [12, 14, 23], 20: [16, 21, 23],
                 21: [17, 20, 22],
                 22: [18, 21, 23], 23: [19, 20, 22]}

    if graph_name == "graph_10":
        graph = {0: [1, 2, 3], 1: [0, 2, 4], 2: [0, 1, 5], 3: [0, 10, 11], 4: [1, 6, 7], 5: [2, 8, 9], 6: [4, 7, 11],
                 7: [4, 6, 9], 8: [5, 9, 10],
                 9: [5, 7, 8], 10: [3, 8, 11], 11: [3, 6, 10]}

    if graph_name == "graph_11":
        graph = {0: [1, 2, 3, 4, 5], 1: [0, 2, 3, 4], 2: [0, 1, 3], 3: [0, 1, 2], 4: [0, 1, 5], 5: [0, 4]}

    if graph_name == "graph_12":
        graph = {0: [1, 4, 5], 1: [0, 2, 7], 2: [1, 3, 8], 3: [2, 4, 9], 4: [0, 3, 11], 5: [0, 6, 11],
                         6: [5, 7, 10], 7: [1, 6, 8], 8: [2, 7, 9],
                         9: [3, 8, 10], 10: [6, 9, 11], 11: [4, 5, 10]}


    g = Graph(len(graph.keys()), graph)

    #we want to use the maximally connected as start/end vertex with Cheeeseman heuristic
    if heuristic == "cheeseman":
        s = g.max_conncted_vertex
        d = g.max_conncted_vertex

    # we want to use the minimimally connected as start/end vertex with Horn heuristic
    if heuristic == "horn":
        s = g.min_conncted_vertex
        d = g.min_conncted_vertex

    #this is our proposed heuristic -- "round trip." It starts/ends on the most conncted vertex to maximize its efficacy
    if heuristic == "round_trip":
        s = g.max_conncted_vertex
        d = g.max_conncted_vertex

    if heuristic == "unreachable_heuristic":
        s = g.max_conncted_vertex
        d = g.max_conncted_vertex

    if heuristic == "none":
        s = 0
        d = 0


    print(f'Following are all different paths from Node {s} back to {d}:')
    #this line simply randomizes the edge lists in the graph in order to ensure that a favorable ordering doesn't skew results:
    for node in g.graph:
        random_edges = random.sample(g.graph[node], len(g.graph[node]))
        g.graph[node] = random_edges
    g.printPaths(s, d, heuristic)
    print(f'Total number of paths: {g.counter}')



