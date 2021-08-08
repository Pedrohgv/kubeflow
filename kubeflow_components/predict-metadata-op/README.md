This Kubeflow op, given a provided tensorflow yolo model, run a object detection task on a provided video and outputs timestamp and max number of detections for each patch (of frames) passed.

Based on this [repo](https://github.com/theAIGuysCode/tensorflow-yolov4-tflite).

NOTES: model is loaded each time operation is called. When turning into a service, model should be loaded in initialization of service.
### TO DO:

* Implement correct FPS calculation