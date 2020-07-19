import sys


class DFA:

    def __init__(self, data):
        definition = [line.strip('\n') for line in data]

        states = definition[0].split(',')
        self.states = states

        alphabet = definition[1].split(',')
        self.alphabet = alphabet

        accept_states = definition[2].split(',')
        self.acceptStates = accept_states

        initial_state = definition[3]
        self.initialState = initial_state

        transitions = dict()
        for i in range(4, len(definition)):
            transition_line = definition[i].split('->')

            left_hand = tuple(transition_line[0].split(','))
            right_hand = transition_line[1]
            transitions[left_hand] = right_hand
        self.transitions = transitions

    def __str__(self):

        output = str()

        output += self.states[0]
        for state in self.states[1:]:
            output += ',' + state
        output += '\n'

        output += self.alphabet[0]
        for character in self.alphabet[1:]:
            output += ',' + character
        output += '\n'

        if len(self.acceptStates) > 0:
            output += self.acceptStates[0]
            for state in self.acceptStates[1:]:
                output += ',' + state
        output += '\n'

        output += self.initialState
        output += '\n'

        for combination in self.transitions.keys():
            output += combination[0] + ',' + combination[1] + '->' + self.transitions[combination] + '\n'
        output.strip('\n')

        return output

    def minimize(self):
        states = self.get_reached_states()
        reached_states = states

        minimization_table = dict()
        for i in range(len(states) - 1):
            for j in range(i + 1, len(states)):
                one = states[i]
                other = states[j]
                if (one in self.acceptStates and other in self.acceptStates) \
                        or (one not in self.acceptStates and other not in self.acceptStates):
                    minimization_table[(one, other)] = True
                else:
                    minimization_table[(one, other)] = False

        while True:
            copy = minimization_table

            for combination in minimization_table.keys():
                for character in self.alphabet:
                    next1 = self.transitions[(combination[0], character)]
                    next2 = self.transitions[(combination[1], character)]

                    if next1 < next2:
                        if not minimization_table[(next1, next2)]:  # if minimization_table[(smaller, larger)] == False:
                            minimization_table[combination] = False
                    elif next1 > next2:
                        if not minimization_table[(next2, next1)]:
                            minimization_table[combination] = False
                    else:
                        continue

            if copy == minimization_table:
                break

        equivalence_table = {state: [] for state in states}
        for state in equivalence_table.keys():
            stack = [state]

            while stack:
                possible_equivalent = stack.pop()

                accounted = False

                for key in equivalence_table.keys():
                    if possible_equivalent in equivalence_table[key]:
                        accounted = True

                if not accounted:
                    equivalence_table[state].append(possible_equivalent)

                    for key in minimization_table.keys():
                        if key[0] == possible_equivalent and minimization_table[key] is True:
                            stack.append(key[1])
                        elif key[1] == possible_equivalent and minimization_table[key] is True:
                            stack.append(key[0])

        copy = dict()
        for combination in equivalence_table.keys():
            if len(equivalence_table[combination]) > 0:
                copy[combination] = equivalence_table[combination]
        equivalence_table = copy

        minimized_states = list()
        for state in states:
            if state in equivalence_table.keys():
                minimized_states.append(state)
        self.states = minimized_states

        minimized_accept_states = list()
        for state in self.acceptStates:
            if state in equivalence_table.keys():
                minimized_accept_states.append(state)
        self.acceptStates = minimized_accept_states

        minimized_initial_state = self.initialState
        if self.initialState not in minimized_states:
            for state in equivalence_table:
                if self.initialState in equivalence_table[state] and state in minimized_states:
                    minimized_initial_state = state
        self.initialState = minimized_initial_state

        minimized_transitions = dict()
        for state in minimized_states:
            for character in self.alphabet:
                minimized_transitions[(state, character)] = None

        for combination in self.transitions.keys():
            state = combination[0]
            character = combination[1]

            if state not in reached_states:
                continue

            if state not in minimized_states:
                for equivalent in equivalence_table.keys():
                    if state in equivalence_table[equivalent]:
                        state = equivalent

            next_state = self.transitions[(state, character)]
            if next_state not in minimized_states:
                for equivalent in equivalence_table.keys():
                    if next_state in equivalence_table[equivalent]:
                        next_state = equivalent

            minimized_transitions[(state, character)] = next_state
        self.transitions = minimized_transitions

    def get_reached_states(self):
        reached_states = list()
        stack = [self.initialState]

        while stack:
            state = stack.pop()
            if state not in reached_states:
                reached_states.append(state)
                for key in self.transitions.keys():
                    if key[0] == state:
                        stack.append(self.transitions[key])

        reached_states.sort()

        return reached_states


DFA = DFA(sys.stdin)
DFA.minimize()
print(DFA)
