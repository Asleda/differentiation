"""
[main.py](main.html) |
[graph.py](graph.html) |
[tensor.py](tensor.html) |
[ops.py](ops.html) |
[session.py](session.html)
"""

from __future__ import absolute_import
from __future__ import print_function
from __future__ import division

import numpy as np

class BaseOp(object):
    """
    `BaseOp` represents an operation that performs computation on tensors. Every operation consists of the following:

      - A list of `inputs`, each converted to ensure they're all tensors.
      - An output tensor to represent the result of the operation (which might be `None`.)
      - A reference to the graph so that each operation can generate new operations when constructing gradients.

    [Previous: Tensors](tensor.html) | [Next: The Session](session.html)
    """

    def __init__(self, inputs, graph):
        self.inputs = [graph.convert(input_) for input_ in inputs]
        self.output = graph.tensor(op=self)
        self.graph = graph

    def compute(self, sess, *args):
        """
        The compute method receives as input the _evaluated_ input tensors and returns the
        result of performing its operation on the inputs.
        """
        raise NotImplementedError()

    def gradient(self, grad):
        """
        The gradient method computes the gradient of the output w.r.t. each of its inputs as new tensors. (Most of the gradients come from [Wikipedia](https://en.wikipedia.org/wiki/Differentiation_rules).)
        """
        raise NotImplementedError()

class AddOp(BaseOp):
    """
    `AddOp` adds a tensor to another tensor.
    """

    def compute(self, sess, a, b):
        return a + b

    def gradient(self, grad):
        return [grad, grad]

class SubOp(BaseOp):
    """
    `SubOp` subtracts a tensor from another tensor.
    """

    def compute(self, sess, a, b):
        return a - b

    def gradient(self, grad):
        return [grad, -grad]

class MulOp(BaseOp):
    """
    `MulOp` multiplies a tensor by another tensor.
    """

    def compute(self, sess, a, b):
        return a * b

    def gradient(self, grad):
        a, b = self.inputs
        return [grad * b, grad * a]

class DivOp(BaseOp):
    """
    `DivOp` divides a tensor by another tensor.
    """

    def compute(self, sess, a, b):
        return a / b

    def gradient(self, grad):
        a, b = self.inputs
        return [grad / b, grad * (-a / self.graph.square(b))]

class NegOp(BaseOp):
    """
    `NegOp` negates a tensor.
    """

    def compute(self, sess, x):
        return -x

    def gradient(self, grad):
        return [-grad]

class DotOp(BaseOp):
    """
    `DotOp` computes the dot product between two tensors.
    """

    def compute(self, sess, a, b):
        return np.dot(a, b)

    def gradient(self, grad):
        a, b = self.inputs
        aT = self.graph.transpose(a)
        bT = self.graph.transpose(b)
        return [
            self.graph.dot(grad, bT),
            self.graph.dot(aT, grad),
        ]

class SquareOp(BaseOp):
    """
    `SquareOp` squares a tensor.
    """

    def compute(self, sess, x):
        return np.square(x)

    def gradient(self, grad):
        x = self.inputs[0]
        return [grad * (2 * x)]

class TransposeOp(BaseOp):
    """
    `TransposeOp` tranposes a tensor.
    """

    def compute(self, sess, x):
        return np.transpose(x)

    def gradient(self, grad):
        return [self.graph.transpose(grad)]

class SigmoidOp(BaseOp):
    """
    `SigmoidOp` implements the [sigmoid function](https://en.wikipedia.org/wiki/Sigmoid_function) and its derivative.
    """

    def compute(self, sess, x):
        return 1 / (1 + np.exp(-x))

    def gradient(self, grad):
        y = self.output
        return [grad * (y * (1 - y))]

class MeanOp(BaseOp):
    """
    `MeanOp` computes the mean of a tensor. The gradient here is intentially incorrect because computing it requires knowing the shape of the input and output tensors. Fortunately, gradients are fairly malleable in optimization.
    """

    def compute(self, sess, x):
        return np.mean(x)

    def gradient(self, grad):
        factor = 1
        return [grad / factor]

class GroupOp(BaseOp):
    """
    `GroupOp` exploits the fact that each input to the operation is automatically evaluated before computing the operation's output, allowing us to group together the evaluation of multiple operations.
    """

    def compute(self, sess, *args):
        return None

    def gradient(self, grad):
        return [grad for inp in self.inpus]

class AssignOp(BaseOp):
    """
    `AssignOp` updates the session's current state for a tensor.
    """

    def compute(self, sess, a, b):
        sess.state[self.inputs[0]] = b
        return b
