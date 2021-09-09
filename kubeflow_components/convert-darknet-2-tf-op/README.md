This Kubeflow op transforms a model in the **Darknet framework** format to **Tensorflow** format.

The op also outputs the config folder located at the input folder.

**IMPORTANT:**

The input folder must contain the model weights named as `darknet-tiny.weights` and also contain a `config` folder holding a `obj.names` file, which contains the classes names.
