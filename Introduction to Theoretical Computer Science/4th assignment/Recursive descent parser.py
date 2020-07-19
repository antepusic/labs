import sys


class Grammar:
    inputString = str()
    length = int()
    output = str()

    def __init__(self):
        self.i = 0

    def test(self, data):
        self.inputString = data.readline().strip('\n')
        self.length = len(self.inputString)

        self.s()

        if self.i < self.length:
            print(self.output + '\nNE')
        else:
            print(self.output + '\nDA')

    def s(self):
        self.output += 'S'

        character = ''
        if self.i < self.length:
            character = self.inputString[self.i]

        if character in ('a', 'b'):
            self.i += 1

        if character == 'a':
            self.a()
            self.b()
        elif character == 'b':
            self.b()
            self.a()
        else:
            print(self.output + '\nNE')
            exit(1)

    def a(self):
        self.output += 'A'

        character = ''
        if self.i < self.length:
            character = self.inputString[self.i]

        if character in ('a', 'b'):
            self.i += 1

        if character == 'a':
            if self.i > self.length:
                print(self.output + '\nDA')
                exit(1)
        elif character == 'b':
            self.c()
        else:
            print(self.output + '\nNE')
            exit(1)

    def b(self):
        self.output += 'B'

        string = ''
        if self.i + 1 < self.length:
            string = self.inputString[self.i: self.i + 2]

        if string == 'cc':
            self.i += 2

            self.s()

            string = ''
            if self.i + 1 < self.length:
                string = self.inputString[self.i: self.i + 2]

            if string == 'bc':
                self.i += 2

            else:
                print(self.output + '\nNE')
                exit(1)
        else:
            pass

    def c(self):
        self.output += 'C'

        self.a()
        self.a()


grammar = Grammar()

grammar.test(sys.stdin)
