
from absl import app, flags, logging
from absl.flags import FLAGS

def change_classes_file(folder='/tf_model'):
    # changes config.py file to point at the correct location for the obj.names file, which contains the classes names.
    # has to be here instead of utils.py because utils also use the cfg.YOLO.CLASSES attribute during the import

    pattern = "__C.YOLO.CLASSES"

    file_name = './src/core/config.py'

    # reads the file and stores its contents
    with open(file_name, 'rt') as cfg_file:
        data = cfg_file.read()

    # find the line that contains the path to the obj.names
    with open(file_name, 'rt') as cfg_file:
        for line in cfg_file:
            line = line.strip('\r\n')  # it's always a good behave to strip what you read from files
            if pattern in line:
                replace_line = line
                break
    
    # replaces the entire line in the previous loaded contents of file
    data = data.replace(
        replace_line,
        "__C.YOLO.CLASSES              = " + "'" + folder  + "/config/obj.names'"
    )

    # writes to the file
    with open(file_name, 'wt') as cfg_file:
        cfg_file.write(data)

flags.DEFINE_string('framework', 'tf', '(tf, tflite, trt')
flags.DEFINE_string('tf_model', './tf_model',
                    'path to folder containing tensorflow model files and a config folder containing the obj.names file.')
flags.DEFINE_integer('size', 416, 'resize images to')
flags.DEFINE_boolean('tiny', True, 'yolo or yolo-tiny')
flags.DEFINE_string('architecture', 'yolov4', 'yolov3 or yolov4')
flags.DEFINE_string('inputs', './input_videos', 'path to folder containing videos to be converted')
flags.DEFINE_string('outputs', './output_videos', 'path to output folder holding converted videos')
flags.DEFINE_string('output_format', 'XVID', 'codec used in VideoWriter when saving video to file')
flags.DEFINE_float('iou', 0.45, 'iou threshold')
flags.DEFINE_float('score', 0.5, 'score threshold')
flags.DEFINE_boolean('dont_show', True, 'dont show video output')
flags.DEFINE_integer('batch_size', 32, 'batch size to be used during prediction')

def main(_argv):

    # changes the config.py file to point at the right file for obj.names, according to the input folder provided in runtime
    change_classes_file(folder=FLAGS.tf_model)

    # imports must be done inside main function because input flag arguments (and by consequence the folder containing the obj.names file)
    # are only valid inside main funtion app.
    import time
    import datetime
    import tensorflow as tf
    physical_devices = tf.config.experimental.list_physical_devices('GPU')
    if len(physical_devices) > 0:
        tf.config.experimental.set_memory_growth(physical_devices[0], True)
    import core.utils as utils
    from core.yolov4 import filter_boxes
    from tensorflow.python.saved_model import tag_constants
    from PIL import Image
    import cv2
    import decord
    from decord import VideoReader
    from decord import cpu, gpu
    import numpy as np
    import os
    from tensorflow.compat.v1 import ConfigProto
    from tensorflow.compat.v1 import InteractiveSession

    # creates output folder
    print('Creating output folder...')
    os.makedirs(FLAGS.outputs, exist_ok=True)

    config = ConfigProto()
    config.gpu_options.allow_growth = True
    session = InteractiveSession(config=config)
    STRIDES, ANCHORS, NUM_CLASS, XYSCALE = utils.load_config(FLAGS)
    input_size = FLAGS.size

    videos = os.listdir(FLAGS.inputs)

    for video in videos:

        video_path = FLAGS.inputs + '/' + video
        output_path = FLAGS.outputs + '/' + 'detected_decord_' + video

        print('Loading model...')
        saved_model_loaded = tf.saved_model.load(FLAGS.tf_model, tags=[tag_constants.SERVING])
        infer = saved_model_loaded.signatures['serving_default']
        print('Model loaded.')
        
        ##############################################
        # loads video using decord
        decr_vid = VideoReader(video_path, ctx=cpu(0), height=input_size, width=input_size)
        decord.bridge.set_bridge('tensorflow')
        #############################################
        
        # capture video with openCv for FPS information
        try:
            vid = cv2.VideoCapture(int(video_path))
        except:
            vid = cv2.VideoCapture(video_path)

        fps = vid.get(cv2.CAP_PROP_FPS)
        print('FPS: {}'.format(fps))
        print('\nBeginning conversion of {}\n'.format(video))

        

        max_detections = 0
        total_frames = len(decr_vid)
        
        for i in range(0, total_frames, FLAGS.batch_size):

            # indexes of frames to get, relative to entire video
            indexes = np.arange(
                start=i,
                stop=min((i+FLAGS.batch_size), total_frames) 
            )
            batch_data_decr = decr_vid.get_batch(indexes) / 255

            pred_bbox = infer(batch_data_decr)

            for key, value in pred_bbox.items():
                boxes = value[:, :, 0:4]
                pred_conf = value[:, :, 4:]

            boxes, scores, classes, valid_detections = tf.image.combined_non_max_suppression(
                boxes=tf.reshape(boxes, (tf.shape(boxes)[0], -1, 1, 4)),
                scores=tf.reshape(
                    pred_conf, (tf.shape(pred_conf)[0], -1, tf.shape(pred_conf)[-1])),
                max_output_size_per_class=50,
                max_total_size=50,
                iou_threshold=FLAGS.iou,
                score_threshold=FLAGS.score
            )

            # indexes of max number of detections for this batch
            max_detections_on_batch_index = tf.math.argmax(valid_detections, axis=0)

            # seconds (relative to entire video) of occurence max number of detections for this batch
            seconds = tf.cast((i + max_detections_on_batch_index), tf.float32)/fps
            seconds=seconds.numpy().item()

            
            isec, fsec = divmod(round(seconds*1000000), 1000000)
            fsec = fsec/1000000
            detection_time = datetime.timedelta(seconds=isec)
            print(
                '{} objects detected at {}.{:02.0f}'.format(
                    valid_detections[max_detections_on_batch_index],
                    detection_time, fsec
                )
            )

if __name__ == '__main__':
    try:
        app.run(main)
    except SystemExit:
        pass
