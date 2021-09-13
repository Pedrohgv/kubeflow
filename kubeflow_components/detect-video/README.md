This Kubeflow op, given a provided tensorflow tiny yolo model, subscribes to a kafka broker that will hold messages containing video ID's from a Kerberos Vault. It then downloads those videos and runs a object detection task, outputing timestamp and max number of detections for each batch (of frames) passed.

GPU to be used can be provided as input, as well as  detection threshold and batch size.

Based on this [repo](https://github.com/theAIGuysCode/tensorflow-yolov4-tflite).



### TO DO:

* Make frequency of reports (how frequent are number of objects detected reported) customizable.

* Implement GPU usage optimization (define allocation of memory for each task.)

* Implement device optimization for different operations (different tasks could be run simultaneously on diffente devices).

* Implement device and resource monitoring.

* Implement option to output video with detections.