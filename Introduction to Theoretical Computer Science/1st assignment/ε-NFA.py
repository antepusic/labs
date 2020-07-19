import sys


class EpsilonNFA:

    def __init__(self, data):
        definition = [line.strip('\n') for line in data]

        inputs = [i.split(',') for i in definition[0].split('|')]
        self.inputs = inputs

        states = definition[1].split(',')
        self.states = states

        alphabet = definition[2].split(',')
        self.alphabet = alphabet

        accept_states = definition[3].split(',')
        self.acceptStates = accept_states

        initial_state = definition[4]
        self.initialState = initial_state
        self.currentStates = [initial_state]

        transitions = dict()
        for i in range(5, len(definition)):
            transition_line = definition[i].split('->')

            left_hand = tuple(transition_line[0].split(','))
            right_hand = transition_line[1].split(',')
            if right_hand != ['#']:
                transitions[left_hand] = right_hand
        self.transitions = transitions

    def simulate(self):
        output = str()

        for inputString in self.inputs:
            self.currentStates = [self.initialState]
            self.epsilon_closure()

            output += self.currentStates[0]
            for state in self.currentStates[1:]:
                output += ',' + state

            for character in inputString:
                self.next_states(character)

                output += '|' + self.currentStates[0]
                for state in self.currentStates[1:]:
                    output += ',' + state

            output += '\n'

        print(output)

    def next_states(self, character):
        if self.currentStates == ['#']:
            return

        self.epsilon_closure()

        next_states = list()
        keys = self.transitions.keys()
        for state in self.currentStates:
            if (state, character) in keys:
                for next_s in self.transitions[(state, character)]:
                    if next_s not in next_states:
                        next_states.append(next_s)

        if len(next_states) == 0:
            self.currentStates = ['#']
            return

        self.currentStates = next_states
        self.epsilon_closure()

    def epsilon_closure(self):
        if self.currentStates != ['#']:

            epsilon_closures = list()

            for state in self.currentStates:
                epsilon_closure = list()
                stack = list()

                stack.append(state)

                while len(stack) > 0:
                    state = stack.pop()

                    if state not in epsilon_closure:
                        epsilon_closure.append(state)

                        for combination in self.transitions.keys():
                            if combination[0] == state and combination[1] == '$':
                                for next_state in self.transitions[combination]:
                                    stack.append(next_state)
                                    if next_state not in epsilon_closures:
                                        epsilon_closures.append(next_state)

            for state in epsilon_closures:
                if state not in self.currentStates:
                    self.currentStates.append(state)

            self.currentStates.sort()


epsilonNFA = EpsilonNFA(sys.stdin)

epsilonNFA.simulate()
