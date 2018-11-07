# -*- coding: utf-8 -*-

"""
{
    "model" : {
        "anchors":              [10,13, 16,30, 33,23, 30,61, 62,45, 59,119, 116,90, 156,198, 373,326],
        "labels":               ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"],
        "net_size":               288
    },
    "pretrained" : {
        "keras_format":             "",
        "darknet_format":           "yolov3.weights"
    },
    "train" : {
        "min_size":             288,
        "max_size":             288,
        "num_epoch":            35,
        "train_image_folder":   "../dataset/svhn/train_imgs",
        "train_annot_folder":   "../dataset/svhn/voc_format_annotation/train",
        "valid_image_folder":   "../dataset/svhn/train_imgs",
        "valid_annot_folder":   "../dataset/svhn/voc_format_annotation/train",
        "batch_size":           16,
        "learning_rate":        1e-4,
        "save_folder":         "configs/svhn",
        "jitter":               false
    }
}
"""

import json
import os
import glob
from yolo.net import Yolonet
from yolo.dataset.generator import BatchGenerator
from yolo.utils.utils import download_if_not_exists


class ConfigParser(object):
    def __init__(self, config_file):
        with open(config_file) as data_file:    
            config = json.load(data_file)
        
        self._model_config = config["model"]
        self._pretrained_config = config["pretrained"]
        self._train_config = config["train"]
        
    def create_model(self):
        model = Yolonet(n_classes=len(self._model_config["labels"]))
        if os.path.exists(self._pretrained_config["keras_format"]):
            model.load_weights(self._pretrained_config["keras_format"])
        else:
            download_if_not_exists(self._pretrained_config["darknet_format"],
                                   "https://pjreddie.com/media/files/yolov3.weights")

            model.load_darknet_params(self._pretrained_config["darknet_format"], skip_detect_layer=True)

        return model

    def create_generator(self):
        train_ann_fnames = glob.glob(os.path.join(self._train_config["train_annot_folder"], "*.xml"))
        valid_ann_fnames = glob.glob(os.path.join(self._train_config["valid_annot_folder"], "*.xml"))
    
        train_generator = BatchGenerator(train_ann_fnames,
                                         self._train_config["train_image_folder"],
                                         batch_size=self._train_config["batch_size"],
                                         labels=self._model_config["labels"],
                                         anchors=self._model_config["anchors"],
                                         min_net_size=self._train_config["min_size"],
                                         max_net_size=self._train_config["max_size"],
                                         jitter=self._train_config["jitter"],
                                         shuffle=True)
        if len(valid_ann_fnames) > 0:
            valid_generator = BatchGenerator(valid_ann_fnames,
                                               self._train_config["valid_image_folder"],
                                               batch_size=self._train_config["batch_size"],
                                               labels=self._model_config["labels"],
                                               anchors=self._model_config["anchors"],
                                               min_net_size=self._model_config["net_size"],
                                               max_net_size=self._model_config["net_size"],
                                               jitter=False,
                                               shuffle=False)
        else:
            valid_generator = None
        print("Training samples : {}, Validation samples : {}".format(len(train_ann_fnames), len(valid_ann_fnames)))
        return train_generator, valid_generator

    def get_train_params(self):
        learning_rate=self._train_config["learning_rate"]
        save_dname=self._train_config["save_folder"]
        num_epoches=self._train_config["num_epoch"]
        return learning_rate, save_dname, num_epoches

