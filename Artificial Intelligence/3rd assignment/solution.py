from sys import argv
import math
from itertools import product
from copy import deepcopy


class ID3:

    max_depth = -1

    def __init__(self, config):
        hyperparameters = load_config(config)
        if "mode" in hyperparameters.keys():
            self.mode = hyperparameters["mode"]
        if "model" in hyperparameters.keys():
            self.model = hyperparameters["model"]
        if "max_depth" in hyperparameters.keys():
            self.max_depth = int(hyperparameters["max_depth"])
        self.training = None
        self.tree = None
        self.testing = None

    def fit(self, data):
        self.training = load_dataset(data)

        data = self.training.data
        features = self.training.features
        label = self.training.label
        mode = self.mode
        depth = 0
        max_depth = self.max_depth

        self.tree = id3f(data, data, features, label, mode, depth, max_depth)

        bfs(self.tree)

    def predict(self, dataset):
        self.testing = load_dataset(dataset)

        tests = deepcopy(self.testing.data)

        confusion_matrix = dict()
        classes = set()
        for point in self.training.data:
            classes.add(point[-1])
        classes = list(classes)
        for v1, v2 in product(classes, classes):
            confusion_matrix[(v1, v2)] = 0

        correct = 0
        count = len(tests)
        predictions = str()
        for point in tests:
            examples = deepcopy(self.training.data)
            features = deepcopy(self.training.features)
            node = self.tree

            example = deepcopy(point)
            expected = point[-1]

            while True:
                if type(node) == Leaf:
                    predicted = node.c
                    confusion_matrix[(expected, predicted)] += 1
                    predictions += "{} ".format(predicted)
                    if predicted == expected:
                        correct += 1
                    break

                feature = node.feature
                i = features.index(feature)
                value = example[i]

                if value not in node.children.keys():
                    # ARGMAX
                    classes = set([x[-1] for x in examples])
                    frequencies = {c: 0 for c in classes}
                    for x in examples:
                        frequencies[x[-1]] += 1
                    argmax = None
                    for c, f in frequencies.items():
                        if argmax is None:
                            argmax = c
                        else:
                            # ALPHABETICALLY ORDERED
                            if f > frequencies[argmax] or c < argmax and f == frequencies[argmax]:
                                argmax = c

                    predicted = argmax
                    confusion_matrix[(expected, predicted)] += 1
                    predictions += "{} ".format(predicted)
                    if predicted == expected:
                        correct += 1
                    break

                node = node.children[value]

                example.pop(i)
                new_examples = [p[0:i] + p[i+1:] for p in examples if p[i] == value]
                examples = new_examples.copy()
                features.pop(i)

        predictions = predictions.rstrip(" ")
        print(predictions)
        accuracy = correct / count
        print("{:07.5f}".format(accuracy))

        confusion = str()
        for c1 in sorted(classes):
            for c2 in sorted(classes):
                confusion += "{} ".format(confusion_matrix[c1, c2])
            confusion = confusion.rstrip(" ") + "\n"
        confusion = confusion.rstrip("\n")
        print(confusion)


class Dataset:
    def __init__(self, data, features, label):
        self.data = data
        self.features = features
        self.label = label


class Node:
    def __init__(self, feature, children):
        self.feature = feature
        self.children = children

    def __repr__(self):
        return self.feature


class Leaf:
    def __init__(self, c):
        self.c = c


def id3f(data, parent_data, features, label, mode, depth, max_depth):
    # END #1
    if not data:
        # ARGMAX
        values = set([point[-1] for point in parent_data])
        frequencies = {v: 0 for v in values}
        for point in parent_data:
            frequencies[point[-1]] += 1
        argmax = None
        for v, f in frequencies.items():
            if argmax is None:
                argmax = v
            else:
                # ALPHABETICALLY ORDERED
                if f > frequencies[argmax] or v < argmax and f == frequencies[argmax]:
                    argmax = v

        return Leaf(argmax)

    # ARGMAX
    classes = set([point[-1] for point in data])
    frequencies = {c: 0 for c in classes}
    for point in data:
        frequencies[point[-1]] += 1
    argmax = None
    for c, f in frequencies.items():
        if argmax is None:
            argmax = c
        else:
            # ALPHABETICALLY ORDERED
            if f > frequencies[argmax] or c < argmax and f == frequencies[argmax]:
                argmax = c

    # END #2
    if len(features) == 0 or len(classes) == 1 or depth == max_depth:
        return Leaf(argmax)

    # END #3
    chosen = 0
    max_gain = 0

    debug = str()
    for i in range(len(features)):
        values = set([point[i] for point in data])

        # ENTROPY
        count = {c: 0 for c in classes}
        for point in data:
            count[point[-1]] += 1
        total = len(data)
        entropy = - sum(count[c] / total * log2(count[c] / total) for c in classes)

        # INFORMATION GAIN
        gain = entropy
        for v in values:
            count = {c: 0 for c in classes}
            for point in data:
                if point[i] == v:
                    count[point[-1]] += 1
            subtotal = len([point for point in data if point[i] == v])

            partial_entropy = - subtotal / total * sum(count[c] / subtotal * log2(count[c] / subtotal) for c
                                                       in classes)
            gain -= partial_entropy

        debug += "IG({})={:06.4f} ".format(features[i], gain)

        if gain > max_gain or (gain == max_gain and features[i] < features[chosen]):
            max_gain = gain
            chosen = i

    if mode != "test":
        print(debug.rstrip(" "))

    children = dict()
    values2 = set([point[chosen] for point in data])
    for v2 in values2:
        new_data = list()
        for point in data:
            if point[chosen] == v2:
                new_point = point.copy()
                new_point.pop(chosen)
                new_data.append(new_point)
        new_features = features.copy()
        new_features.pop(chosen)
        t = id3f(new_data, data, new_features, label, mode, depth + 1, max_depth)
        children[v2] = t
    return Node(features[chosen], children)


def log2(x):
    return math.log2(x) if x != 0 else 0


def bfs(source):
    output = str()

    queue = [(source, 0)]
    while queue:
        node, depth = queue.pop(0)
        if type(node) == Node:
            output += "{}:{}, ".format(depth, node.feature)

            for v in node.children.values():
                if type(v) == Node:
                    queue.append((v, depth + 1))

    output = output.rstrip(", ")
    print(output)


def load_config(path):

    hyperparameters = dict()

    with open(path, mode="r", encoding="utf-8") as config:
        for line in config:
            line = line.rstrip("\n").split("=")
            hyperparameters[line[0]] = line[1]

    return hyperparameters


def load_dataset(path):

    data = list()
    header = None

    with open(path, mode="r", encoding="utf-8") as dataset:
        for line in dataset:
            line = line.rstrip("\n").split(",")
            if header is None:
                header = line
            else:
                data_point = list()
                for feature, value in zip(header, line):
                    data_point.append(value)
                data.append(data_point)

    label = header.pop()

    return Dataset(data, header, label)


def demo(args):
    train_dataset, test_dataset, config = args[1:4]

    model = ID3(config)
    model.fit(train_dataset)
    model.predict(test_dataset)


demo(argv)
