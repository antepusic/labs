from sys import argv
from itertools import product


class Literal:

    def __init__(self, string):
        self.no = True if string[0] == "~" else False
        self.string = string[1:] if string[0] == "~" else string

    def __repr__(self):
        return self.string if self.no is False else "~" + self.string

    def __str__(self):
        return self.__repr__()

    def __eq__(self, other):
        return self.no == other.no and self.string == other.string

    def __hash__(self):
        return hash((self.no, self.string))

    def complement(self):
        if self.no is True:
            return Literal(self.string)
        elif self.no is False:
            return Literal("~" + self.string)


class Clause:

    def __init__(self, literal_list):
        self.literals = literal_list

    def __repr__(self):
        output = ""
        for literal in self.literals:
            output += str(literal) + " v "
        output = output.rstrip(" v ")
        return output

    def __str__(self):
        return self.__repr__()

    def __eq__(self, other):
        return self.literals == other.literals

    def __hash__(self):
        return hash(tuple(self.literals))


def data_loader():
    length = len(argv)

    _flag = argv[1]
    clause_list_path = argv[2]
    _clauses = get_clauses(clause_list_path)
    _commands = None
    _verbose = False

    if length == 3:
        pass
    elif length == 4:
        if argv[3] != "verbose":
            command_list_path = argv[3]

            _commands = get_commands(command_list_path)
        elif argv[3] == "verbose":
            _verbose = True
    elif length == 5:
        command_list_path = argv[3]
        _commands = get_commands(command_list_path)
        _verbose = True

    return _flag, _clauses, _commands, _verbose


def get_clauses(file_path):
    _clauses = list()
    with open(file_path, mode="r", encoding="utf-8") as clause_list:
        for line in clause_list:
            # SKIP COMMENTS
            if line[0] == "#":
                continue

            line = line.rstrip("\n").split(" ")

            new_clause = list()
            for item in line:
                if item not in ("v", "V"):
                    new_clause.append(Literal(item))
            _clauses.append(Clause(new_clause))

    return _clauses


def get_commands(file_path):
    _commands = list()
    if file_path is not None:
        with open(file_path, mode="r", encoding="utf-8") as command_list:

            for _line in command_list:
                _commands.append(get_command(_line))

    return _commands


def get_command(_line):
    _line = _line.rstrip("\n").split(" ")

    if _line == "exit":
        return {"symbol": _line, "clause": None}
    else:
        new_command = {"symbol": _line.pop(), "clause": Clause([Literal(i) for i in _line if i not in ("v", "V")])}
        return new_command


def refutation_resolution(_premises, _goal):

    # GOAL NEGATION
    negated_goal = list()
    for _ in _goal.literals:
        negated_goal.append(Clause([_.complement()]))

    _sos = negated_goal[:]
    _clauses = _premises + _sos
    _new = list()
    used = list()

    i = 1
    numbers = dict()
    output = str()
    if verbose:
        numbers = dict()
        i = 1
        for _clause in _clauses:
            numbers[_clause] = str(i)
            i += 1

        output = str()
        for _clause in _premises:
            output += numbers[_clause] + ". " + str(_clause) + "\n"
        output += "=\n"
        for _clause in _sos:
            output += numbers[_clause] + ". " + str(_clause) + "\n"
        output += "=\n"

    while True:
        selection = select_sos(_premises, _sos)
        if len(selection) > 0:
            for combination in selection:

                if set(combination) in used:
                    continue
                else:
                    used.append(set(combination))

                resolvents = resolve(combination[0], combination[1])

                # FACTORIZATION
                for resolvent in resolvents:
                    factorized = set(resolvent.literals)
                    resolvent.literals = list(factorized)

                # REDUNDANT CLAUSE REMOVAL
                simplified = _sos[:]
                for resolvent in resolvents:
                    for _clause in _sos:
                        if set(resolvent.literals) <= set(_clause.literals):
                            if _clause in simplified:
                                simplified.remove(_clause)
                            if _clause in _new:
                                _new.remove(_clause)
                _sos = simplified[:]

                # IRRELEVANT CLAUSE REMOVAL
                relevant = resolvents[:]
                for r in resolvents:
                    for a, b in product(r.literals, r.literals):
                        if a == b.complement():
                            if r in relevant:
                                relevant.remove(r)
                                break
                resolvents = relevant[:]

                if verbose:
                    for resolvent in resolvents:
                        numbers[resolvent] = str(i)
                        output += str(i) + ". " + str(resolvent) + " (" + numbers[combination[0]] + ", "\
                            + numbers[combination[1]] + ")\n"
                        i += 1

                nil = Clause([Literal("NIL")])
                for resolvent in resolvents:
                    if nil == resolvent:
                        if verbose: print_verbose(output)
                        print(str(_goal) + " is true")
                        return True

                _new += resolvents
                _sos += resolvents

            if set(_new) <= set(_clauses):
                if verbose: print_verbose(output)
                print(str(_goal) + " is unknown")
                return False
            _clauses += _new
        else:
            if verbose: print_verbose(output)
            print(str(_goal) + " is unknown")
            return False


def select_sos(_premises, _sos):
    selection = list()
    for first, second in product(_sos[::-1], _premises + _sos):
        for thesis, antithesis in product(first.literals, second.literals):
            if thesis == antithesis.complement():
                selection.append((first, second))
                continue

    return selection


def resolve(_first: Clause, _second: Clause):
    _first = _first.literals
    _second = _second.literals

    _resolvents = list()
    pairs = list()
    for pair in product(_first, _second):
        if pair[0] == pair[1].complement():
            pairs.append(tuple(pair))

    if len(pairs) == 0:
        union = _first + _second
        _resolvents.append(Clause(union))
    else:
        for pair in pairs:
            union = _first + _second
            union.remove(pair[0])
            union.remove(pair[1])
            if len(union) == 0:
                _resolvents.append(Clause([Literal("NIL")]))
            else:
                _resolvents.append(Clause(union))

    return _resolvents


def print_verbose(output):
    output += "=\n"
    max_length = max(len(line) for line in output.split("\n"))
    print(output.replace("=", max_length * "="), end='')


flag, clauses, commands, verbose = data_loader()

if flag == "resolution":
    goal = clauses.pop()

    refutation_resolution(clauses, goal)

elif flag == "cooking_interactive":
    while True:
        command = get_command(input())
        symbol = command["symbol"]
        clause = command["clause"]

        if symbol == "?":
            refutation_resolution(clauses, clause)
        elif symbol == "+":
            clauses.append(clause)
            if verbose:
                print("added", str(clause))
        elif symbol == "-":
            clauses.remove(clause)
            if verbose:
                print("removed", str(clause))
        elif symbol == "exit":
            exit(0)

elif flag == "cooking_test":
    for command in commands:
        symbol = command["symbol"]
        clause = command["clause"]

        if symbol == "?":
            refutation_resolution(clauses, clause)
        elif symbol == "+":
            clauses.append(clause)
            if verbose:
                print("added", str(clause))
        elif symbol == "-":
            clauses.remove(clause)
            if verbose:
                print("removed", str(clause))
