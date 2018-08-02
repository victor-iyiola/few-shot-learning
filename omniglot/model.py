"""Helper class for building Siamese model for One-shot learning.

   @description
     For training, validating/evaluating & predictions with SiameseNetwork.

   @author
     Victor I. Afolabi
     Artificial Intelligence & Software Engineer.
     Email: javafolabi@gmail.com
     GitHub: https://github.com/victor-iyiola/

   @project
     File: model.py
     Package: omniglot
     Created on 13 July, 2018 @ 9:10 PM.

   @license
     MIT License
     Copyright (c) 2018. Victor I. Afolabi. All rights reserved.
"""

import tensorflow as tf
from tensorflow import keras

from omniglot import BaseNetwork, Dataset


class SiameseNetwork(BaseNetwork):
    """Siamese Neural network for few shot learning."""

    # noinspection SpellCheckingInspection
    def __init__(self, num_classes: int = 1, **kwargs):
        """Implementation of "__Siamese Network__" with parameter specifications as proposed in [this paper](http://www.cs.cmu.edu/~rsalakhu/papers/oneshot1.pdf) by Gregory Koch, Richard Zemel and Ruslan Salakhutdinov.

        Args:
            num_classes (int, optional): Defaults to 1. Number of output classes
                in the last layer (prediction layer).

        Keyword Args:
            input_shape (tuple, optional): Defaults to (105, 105, 1). Input shape
                for a single image. Shape in the form: `(width, height, channel)`.
        """

        super(SiameseNetwork, self).__init__(**kwargs)

    def build(self, **kwargs):
        # Optional Keyword arguments.
        num_classes = kwargs.get('num_classes', 1)

        # Build a sequential model.
        model = keras.models.Sequential()

        # 1st layer (64@10x10)
        model.add(keras.layers.Conv2D(filters=64, kernel_size=(10, 10),
                                      input_shape=self.in_shape,
                                      activation='relu'))
        model.add(keras.layers.MaxPool2D(pool_size=(2, 2)))

        # 2nd layer (128@7x7)
        model.add(keras.layers.Conv2D(filters=128, kernel_size=(7, 7),
                                      activation=tf.'relu'))
        model.add(keras.layers.MaxPool2D(pool_size=(2, 2)))

        # 3rd layer (128@4x4)
        model.add(keras.layers.Conv2D(filters=128, kernel_size=(4, 4),
                                      activation='relu'))
        model.add(keras.layers.MaxPool2D(pool_size=(2, 2)))

        # 4th layer (265@4x4)
        model.add(keras.layers.Conv2D(filters=256, kernel_size=(4, 4),
                                      activation='relu'))
        model.add(keras.layers.MaxPool2D(pool_size=(2, 2)))

        # 5th layer  (9216x4096)
        model.add(keras.layers.Flatten())
        model.add(keras.layers.Dense(units=4096,
                                     activation='sigmoid'))

        # 6th - L1 layer -distance layer.
        model.add(keras.layers.Lambda(self.dist_func))

        # Output layer (4096x1)
        model.add(keras.layers.Dense(units=num_classes,
                                     activation='sigmoid'))

        return model

    def call(self, inputs, **kwargs):
        """Calls the model on new inputs.

        In this case `call` just reapplies all ops in the graph to the new inputs
        (e.g. build a new computational graph from the provided inputs).

        Args:
            inputs: A tensor or list of tensors.

        Keyword Args:
            training: Boolean or boolean scalar tensor, indicating whether to run
            the `Network` in training mode or inference mode.
            mask: A mask or list of masks. A mask can be
                either a tensor or None (no mask).

        Returns:
            A tensor if there is a single output, or
            a list of tensors if there are more than one outputs.
        """

        # Sister networks.
        first = self.__encoder(inputs[0])
        second = self.__encoder(inputs[1])

        # L1 distance.
        distance = self.distance((first, second))

        # Prediction.
        pred = self.prediction(distance)

        # Returns distance and prediction if not in training mode.
        # return pred if training else distance, pred
        return pred


if __name__ == '__main__':
    import numpy as np

    net = SiameseNetwork(loss_func=SiameseNetwork.triplet_loss)

    # Image pairs in `np.ndarray`.
    first = np.random.randn(1, 105, 105, 1)
    second = np.random.randn(1, 105, 105, 1)

    # Converted to `tf.Tensor`.
    pairs = [tf.constant(first), tf.constant(second)]

    net(pairs)

    net.summary()
