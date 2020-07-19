# Classes


class State:

    def __init__(self, name_1):
        self.name = name_1

    def __repr__(self):
        return self.name

    def __eq__(self, other):
        if isinstance(other, State):
            return self.name == other.name
        else:
            return NotImplemented

    def __hash__(self):
        return hash(tuple(sorted(self.__dict__.items())))


class Node:

    def __init__(self, state, weight, parent):
        self.state = state
        self.weight = weight
        self.parent = parent

    def __repr__(self):
        if self.parent is not None:
            return "(" + self.state.__str__() + ", " + str(self.weight) + ", " + str(self.parent.state) + ")"
        else:
            return "(" + self.state.__str__() + ", " + str(self.weight) + ", None)"

    def __eq__(self, other):
        if isinstance(other, Node):
            if self.parent is not None and other.parent is not None:
                return (self.state.name == other.state.name) and (self.weight == other.weight) \
                       and (self.parent == other.parent)
            elif self.parent is None and other.parent is None:
                return (self.state.name == other.state.name) and (self.weight == other.weight)
            else:
                return False
        else:
            return NotImplemented

    def __hash__(self):
        return hash(tuple(sorted(self.__dict__.items())))


# Helper methods


def expand(node, successor_list):
    return [Node(successor[0], node.weight + 1, node) for successor in successor_list[node.state]]


def expand_depth_cost(node, successor_list):
    return [Node(successor[0], (node.weight[0] + 1, node.weight[1] + successor[1]), node) for successor in
            successor_list[node.state]]


def expand_with_cost(node, successor_list):
    return [Node(successor[0], node.weight + successor[1], node) for successor in successor_list[node.state]]


def get_cost(node_a, node_b):
    state_a = node_a.state
    state_b = node_b.state

    return edges[state_a, state_b]


def h(state, heuristic):
    return heuristic[state]


# Search algorithm implementations


def bfs(start, successors, goals):
    start_node = Node(start, 0, None)
    open = [start_node]
    visited = set()

    while open:
        n = open.pop(0)

        if n.state in goals:
            return start_node, n, len(visited)

        visited.add(n.state)

        for node in expand(n, successors):
            if node.state not in visited:
                open.append(node)

    return "fail"


def uniform_cost_search(start, successors, goals):
    start_node = Node(start, 0, None)
    open = [start_node]
    visited = set()

    while open:
        n = open.pop(0)

        if n.state in goals:
            return start_node, n, len(visited)

        visited.add(n.state)

        successor_nodes = expand_with_cost(n, successors)

        for node in successor_nodes:
            if node.state not in visited:
                open.append(node)
        open = sorted(open, key=lambda x: x.weight)

    return "fail"


def a_star_search(start, successors, goals, heuristic):
    start_node = Node(start, 0, None)
    open = [start_node]
    closed = set()
    visited = set()

    while open:
        n = open.pop(0)

        if n.state in goals:
            return start_node, n, len(visited)

        closed.add(n)
        visited.add(n.state)

        successor_nodes = expand_with_cost(n, successors)

        for node in successor_nodes:
            for other in open + list(closed):
                if other.state == node.state:
                    if other.weight < node.weight:
                        continue
                    else:
                        if other in open:
                            open.remove(other)
                        if other in closed:
                            closed.remove(other)

        for node in successor_nodes:
            if node.state not in closed and node.state not in visited:
                open.append(node)
        open = sorted(open, key=lambda x: x.weight + h(x.state, heuristic))

    return "fail"


def depth_limited_search(start, successors, goals, depth):
    start_node = Node(start, (0, 0), None)
    visited = set()
    open = [start_node]

    while open:
        n = open.pop()
        visited.add(n.state)

        if n.state in goals:
            return n.weight[1]

        if n.weight[0] < depth:
            for node in expand_depth_cost(n, successors):
                if node.state not in visited:
                    open.append(node)

    return "fail"


def iterative_deepening_search(start, successors, goals):
    for depth in range(1000000000):
        result = depth_limited_search(start, successors, goals, depth)
        if result != "fail":
            return result

    return "fail"


# Path reconstruction


def get_path(start, end):
    cost = 0
    path = [end]

    while path[-1] != start:
        cost += get_cost(path[-1].parent, path[-1])
        path.append(path[-1].parent)

    path.reverse()
    return path, cost


# Data loaders


def load_state_space():
    states = list()
    successors_list = dict()
    edges = dict()

    start = None
    goals = None

    state_space_descriptor = open(
        "C:/Users/Ante/Documents/C/6. semestar/Umjetna inteligencija/Laboratorijske vježbe/1. "
        "laboratorijska vježba/lab1_state_spaces_and_heuristics[1]/ai.txt", "r",
        encoding="utf-8")

    for line in state_space_descriptor:

        if line[0] == '#':
            continue

        if start is None:
            name = line.strip('\n')
            start = State(name)
            states.append(start)
            continue

        if goals is None:
            names = line.strip('\n').split(' ')
            goals = list()
            for name in names:
                goal = State(name)

                goals.append(name)
                states.append(name)
            continue

        line = line.strip('\n').split(':')

        name = line[0]
        if line[1] != '':
            paths = [[State(path.split(',')[0]), int(path.split(',')[1])] for path in line[1].strip().split(' ')]

        state = State(name)

        if line[1] != '':
            for edge in line[1].strip().split(' '):
                edge = edge.split(',')
                other = State(edge[0])
                edges[state, other] = int(edge[1])

        if state != start and state not in goals:
            states.append(state)

        successors_list[state] = paths

    return states, successors_list, edges


def load_heuristic():
    heuristic_descriptor = open("C:/Users/Ante/Documents/C/6. semestar/Umjetna inteligencija/Laboratorijske vježbe/1. "
                                "laboratorijska vježba/lab1_state_spaces_and_heuristics[1]/ai_fail.txt", "r",
                                encoding="utf-8")

    heuristic = dict()

    for line in heuristic_descriptor:
        line = line.strip('\n').split(": ")
        heuristic[State(line[0])] = int(line[1])

    return heuristic


# Output


def output(start, goals, search_type, **kwargs):
    if search_type == "bfs":
        out = bfs(start, successors_list, goals)
    elif search_type == "ucs":
        out = uniform_cost_search(start, successors_list, goals)
    elif search_type == "a*":
        heuristic = kwargs.get('h', None)
        out = a_star_search(start, successors_list, goals, heuristic)

    if out == "fail":
        print("Search failed\n")

        return

    start = out[0]
    goal = out[1]
    visited = out[2]

    path, total_cost = get_path(start, goal)
    length = len(path)

    print("States visited = " + str(visited))
    print("Found path of length " + str(length) + " with total cost " + str(total_cost) + ":")
    print(" =>".join(path))
    print("\n")

    return


# Work code

states, successors_list, edges = load_state_space()
heuristic = load_heuristic()

s = State("enroll_artificial_intelligence")
e = [State("pass_course"), State("fail_course")]

print("BFS")
output(s, e, "bfs")

print("Uniform cost search")
output(s, e, "ucs")

print("A* search")
output(s, e, "a*", h=heuristic)

print("Checking if heuristic is optimistic.")

admissible = True
for state in states:
    if state in heuristic.keys():
        h_star = iterative_deepening_search(state, successors_list, e)
        h_est = h(state, heuristic)
        if h_est > h_star:
            admissible = False
            print("  [ERR] h(" + state.name + ") > h*: " + str(h_est + 0.0) + " > " + str(h_star + 0.0))
if admissible:
    print("Heuristic is optimistic")
elif not admissible:
    print("Heuristic is not optimistic")

print("Checking if heuristic is consistent.")

consistent = True
for state in states:
    if state in heuristic.keys():
        h_state = h(state, heuristic)
        for edge in successors_list[state]:
            successor = edge[0]
            cost = edge[1]
            h_successor = h(successor, heuristic)

            if h_state > (h_successor + cost):
                print ("  [ERR] h(" + str(state) + ") > h(" + str(successor) + ") + c: " + str(h_state + 0.0) + " > "
                       + str(h_successor + 0.0) + " + " + str(cost + 0.0))
                consistent = False
if consistent:
    print("Heuristic is consistent")
elif not admissible:
    print("Heuristic is not consistent")
