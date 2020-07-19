import sys


class TS:

    def __init__(self, data):
        definition = [line.strip('\n') for line in data]

        self.states = definition[0].split(',')

        self.inputAlphabet = definition[1].split(',')

        self.tapeAlphabet = definition[2].split(',')

        self.empty = definition[3]

        self.tape = definition[4]

        self.acceptStates = definition[5].split(',')

        self.initialState = definition[6]

        self.index = int(definition[7])

        self.transitions = dict()
        for i in range(8, len(definition)):
            transition_line = definition[i].split('->')

            left_hand = tuple(transition_line[0].split(','))
            right_hand = tuple(transition_line[1].split(','))
            self.transitions[left_hand] = right_hand

    def simulate(self):
        current_state = self.initialState
        current_tape = self.tape
        i = self.index

        running = True

        while running:
            read = current_tape[i]

            if (current_state, read) not in self.transitions.keys():
                running = False
            else:
                next_state = self.transitions[(current_state, read)][0]
                write = self.transitions[(current_state, read)][1]
                direction = self.transitions[(current_state, read)][2]

                if (i == 0 and direction == 'L') or (i == 69 and direction == 'R'):
                    running = False
                else:
                    current_state = next_state
                    current_tape = current_tape[0:i] + write + current_tape[i+1:]
                    if direction == 'L':
                        i -= 1
                    elif direction == 'R':
                        i += 1

        self.output(current_state, i, current_tape)

    def output(self, state, i, tape):
        accepted = '0'

        if state in self.acceptStates:
            accepted = '1'

        print(state + '|' + str(i) + '|' + tape + '|' + accepted)

TS = TS(sys.stdin)
TS.simulate()