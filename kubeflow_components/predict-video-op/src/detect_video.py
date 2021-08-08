from absl import app, flags, logging
from absl.flags import FLAGS

def change_classes_file(folder='/tf_model'):
    # changes config.py file to point at the correct location for the obj.names file, which contains the classes names.
    # ha to be here instead of utils.py because utils also use the cfg.YOLO.CLASSES attribute duting the import

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
flags.DEFINE_string('tf_model', '/tf_model',
                    'path to folder containing tensorflow model files and a config folder containing the obj.names file.')
flags.DEFINE_integer('size', 416, 'resize images to')
flags.DEFINE_boolean('tiny', True, 'yolo or yolo-tiny')
flags.DEFINE_string('architecture', 'yolov4', 'yolov3 or yolov4')
flags.DEFINE_string('inputs', '/input_videos', 'path to folder containing videos to be converted')
flags.DEFINE_string('outputs', '/output_videos', 'path to output folder holding converted videos')
flags.DEFINE_string('output_format', 'XVID', 'codec used in VideoWriter when saving video to file')
flags.DEFINE_float('iou', 0.45, 'iou threshold')
flags.DEFINE_float('score', 0.25, 'score threshold')
flags.DEFINE_boolean('dont_show', True, 'dont show video output')

def main(_argv):

    # changes the config.py file to point at the right file for obj.names, according to the input folder provided in runtime
    change_classes_file(folder=FLAGS.tf_model)

    # imports must be done inside main function because input flag arguments (and by consequence the folder containing the obj.names file)
    # are only valid inside main funtion app.
    import time
    import tensorflow as tf
    physical_devices = tf.config.experimental.list_physical_devices('GPU')
    if len(physical_devices) > 0:
        tf.config.experimental.set_memory_growth(physical_devices[0], True)
    import core.utils as utils
    from core.yolov4 import filter_boxes
    from tensorflow.python.saved_model import tag_constants
    from PIL import Image
    import cv2
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

    if FLAGS.framework == 'tflite':
        interpreter = tf.lite.Interpreter(model_path=FLAGS.tf_model)
        interpreter.allocate_tensors()
        input_details = interpreter.get_input_details()
        output_details = interpreter.get_output_details()
        print(input_details)
        print(output_details)
    else:
        saved_model_loaded = tf.saved_model.load(FLAGS.tf_model, tags=[tag_constants.SERVING])
        infer = saved_model_loaded.signatures['serving_default']    
        

    videos = os.listdir(FLAGS.inputs)

    for video in videos:

        video_path = FLAGS.inputs + '/' + video
        output_path = FLAGS.outputs + '/' + 'detected_' + video
        
        # begin video capture
        try:
            vid = cv2.VideoCapture(int(video_path))
        except:
            vid = cv2.VideoCapture(video_path)

        out = None

        if FLAGS.outputs:
            # by default VideoCapture returns float instead of int
            width = int(vid.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(vid.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = int(vid.get(cv2.CAP_PROP_FPS))
            codec = cv2.VideoWriter_fourcc(*FLAGS.output_format)
            out = cv2.VideoWriter(output_path, codec, fps, (width, height))

        print('\nBeginning conversion of {}\n'.format(video))

        fpss = []   # list of fpss
        while True:
            return_value, frame = vid.read()
            if return_value:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                image = Image.fromarray(frame)
            else:
                print('Video has ended or failed, try a different video format!')
                break
        
            frame_size = frame.shape[:2]
            image_data = cv2.resize(frame, (input_size, input_size))
            image_data = image_data / 255.
            image_data = image_data[np.newaxis, ...].astype(np.float32)
            start_time = time.time()

            if FLAGS.framework == 'tflite':
                interpreter.set_tensor(input_details[0]['index'], image_data)
                interpreter.invoke()
                pred = [interpreter.get_tensor(output_details[i]['index']) for i in range(len(output_details))]
                if FLAGS.architecture == 'yolov3' and FLAGS.tiny == True:
                    boxes, pred_conf = filter_boxes(pred[1], pred[0], score_threshold=0.25,
                                                    input_shape=tf.constant([input_size, input_size]))
                else:
                    boxes, pred_conf = filter_boxes(pred[0], pred[1], score_threshold=0.25,
                                                    input_shape=tf.constant([input_size, input_size]))
            else:
                batch_data = tf.constant(image_data)
                pred_bbox = infer(batch_data)
                for key, value in pred_bbox.items():
                    boxes = value[:, :, 0:4]
                    pred_conf = value[:, :, 4:]
                #boxes = pred_bbox[:, :, 0:4]
                #pred_conf = pred_bbox[:, :, 4:]
            boxes, scores, classes, valid_detections = tf.image.combined_non_max_suppression(
                boxes=tf.reshape(boxes, (tf.shape(boxes)[0], -1, 1, 4)),
                scores=tf.reshape(
                    pred_conf, (tf.shape(pred_conf)[0], -1, tf.shape(pred_conf)[-1])),
                max_output_size_per_class=50,
                max_total_size=50,
                iou_threshold=FLAGS.iou,
                score_threshold=FLAGS.score
            )
            pred_bbox = [boxes.numpy(), scores.numpy(), classes.numpy(), valid_detections.numpy()]
            image = utils.draw_bbox(frame, pred_bbox)
            fps = 1.0 / (time.time() - start_time)
            print("FPS: %.2f" % fps)
            fpss.append(fps)
            result = np.asarray(image)
            #cv2.namedWindow("result", cv2.WINDOW_AUTOSIZE)  # this should be commented out when running on container
            result = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            if FLAGS.outputs:
                out.write(result)
            if cv2.waitKey(1) & 0xFF == ord('q'): break
        print('\n')
        print('Average FPS: {}'.format(np.mean(fpss)))
        print('\n')
    #cv2.destroyAllWindows()

if __name__ == '__main__':
    try:
        app.run(main)
    except SystemExit:
        pass
