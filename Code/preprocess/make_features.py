# -*- coding: utf-8 -*-
"""
Created on Mon Oct 22 17:30:52 2018

@author: Pooventhiran Naveen
"""
import numpy as np
import os
from re import match
from imageio import imread
from skimage.transform import resize
from scipy import misc
from sklearn.preprocessing import (
    LabelEncoder as sk_LabelEncoder,
    OneHotEncoder as sk_OneHotEncoder,
)
from numpy import array as np_array


class FeatureGen:
    def __init__(self, type_):
        if type_ not in ("words", "phrases"):
            raise ValueError("unsupported type")
        self.type = type_
        self.X = np_array(eval("[[[[0.0]*48]*30]*35]*1500"))
        self.Y = np_array(eval('["01"]*1500'))

    def get_color_images(self, images):
        return list(
            filter(lambda file: bool(match("^color__\d{3}\.jpg$", file)), images)
        )

    def make_features(self, in_path, verbose=True):
        i = 0
        cwd = os.getcwd()
        self.type = "words"
        self.in_path = in_path
        print("in path", in_path)
        os.chdir(in_path)
        speakers = os.listdir(os.getcwd())
        for spk in speakers:
            contents = os.listdir(spk + ("/words"))
            print("Words")
            for content in contents:
                if verbose == True:
                    pass
                utterances = os.listdir(os.path.join(spk, self.type, content))
                for utterance in utterances:
                    if verbose == True:
                        # print('Reading utterance', utterance)
                        print(".", end="")
                    images_list = self.get_color_images(
                        os.listdir(os.path.join(spk, self.type, content, utterance))
                    )
                    n_frames = len(images_list)
                    self.X[i], index = self.append_frames(self.X[i], 15, n_frames)
                    for image in images_list:
                        try:
                            self.X[i][index] = (
                                resize(
                                    imread(
                                        os.path.join(
                                            spk, self.type, content, utterance, image
                                        )
                                    ),
                                    (30, 48),
                                )
                                / 255
                            )
                            index += 1
                        except IndexError:
                            break
                    self.Y[i] = content
                    i += 1
        os.chdir(cwd)
        return (self.X, self.Y)

    def append_frames(self, im_seq, max_frame, n_frames):
        dummy_viseme = (
            resize(imread(os.path.join(self.in_path, "..", "dummy.jpg")), (30, 48))
            / 255
        )
        dummy_count = max_frame - n_frames
        for i in range(0, dummy_count // 2):
            im_seq[i] = dummy_viseme
        for i in range(dummy_count - (dummy_count // 2), max_frame):
            im_seq[i] = dummy_viseme
        return im_seq, dummy_count // 2

    def make_one_hot_encoding(self, Y):
        label_encoder = sk_LabelEncoder()
        integer_encoded = label_encoder.fit_transform(Y)
        onehot_encoder = sk_OneHotEncoder(sparse=False)
        integer_encoded = integer_encoded.reshape(len(integer_encoded), 1)
        onehot_encoded = onehot_encoder.fit_transform(integer_encoded)
        """
        print('Label', label_encoder.inverse_transform([np.argmax(onehot_encoded[0, :])]))
        """
        return onehot_encoded, label_encoder

    def decode_one_hot(self, predictions, label_encoder):
        dec = []
        for i in range(len(predictions)):
            dec.append(label_encoder.inverse_transform([np.argmax(predictions[i])]))
        return np.array(dec)
