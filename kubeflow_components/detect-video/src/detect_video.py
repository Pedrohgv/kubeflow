
from absl import app, flags, logging
from absl.flags import FLAGS
import time
import datetime
import tensorflow as tf
import core.utils as utils
from core.yolov4 import filter_boxes
from core.vault import CreateQueue, download_video
from core.metrics import counter, start_prometheus_exposure
import json
from tensorflow.python.saved_model import tag_constants
from PIL import Image
import cv2
import decord
from decord import VideoReader
from decord import cpu, gpu
import numpy as np
import os
import gc
from tensorflow.compat.v1 import ConfigProto
from tensorflow.compat.v1 import InteractiveSession

flags.DEFINE_string('framework', 'tf', '(tf, tflite, trt')
flags.DEFINE_string('tf_model', '/tf_model',
                    'path to folder containing tensorflow model files and a config folder containing the obj.names file.')
flags.DEFINE_integer('size', 416, 'resize images to')
flags.DEFINE_string('architecture', 'yolov4', 'yolov3 or yolov4')
flags.DEFINE_string('inputs', '/input_videos', 'path to folder containing videos to be converted')
flags.DEFINE_float('iou', 0.45, 'iou threshold')
flags.DEFINE_float('score', 0.7, 'score threshold')
flags.DEFINE_boolean('dont_show', True, 'dont show video output')
flags.DEFINE_integer('batch_size', 32, 'batch size to be used during prediction')
flags.DEFINE_integer('gpu', 0, 'integer representing GPU to be used')


# variables needed to configure interface with kafka
flags.DEFINE_string('bootstrap_servers', None, 'bootstrap server of kafka broker')
flags.DEFINE_string('kafka_topic', None, 'topic of kafka broker to listen to')
flags.DEFINE_string('kafka_username', None, 'sasl username for kafka')
flags.DEFINE_string('kafka_password', None, 'sasl password for kafka')

# variables needed to configure interface with kerberos vault
flags.DEFINE_string('vault_api_address', None, 'kerberos API address from which videos will be downloaded from')
flags.DEFINE_string('vault_access_key', None, 'kerberos vault access key')
flags.DEFINE_string('vault_secret_access_key', None, 'kerberos vault secret access key')

def main(_argv):

    physical_devices = tf.config.experimental.list_physical_devices('GPU')
    if len(physical_devices) > FLAGS.gpu:
        print()
        print('Using GPU {}'.format(FLAGS.gpu))
        print()
        tf.config.experimental.set_memory_growth(physical_devices[FLAGS.gpu], True)

    elif len(physical_devices) > 0:
        print()
        print('Specified GPU not found. Running ops on automatically choosen GPU.')
        print()
        tf.config.experimental.set_memory_growth(physical_devices[0], True)
    else:
        print('No GPUs found. Running ops on CPU instead.')
    
    # Lets tensorflow choose another device if the one specified doesn't exist.
    tf.config.set_soft_device_placement(True)

    # Selects specified device.
    with tf.device('/device:GPU:{}'.format(FLAGS.gpu)):

        config = ConfigProto()
        session = InteractiveSession(config=config)
        input_size = FLAGS.size

        print()
        print('Loading model...')
        saved_model_loaded = tf.saved_model.load(FLAGS.tf_model, tags=[tag_constants.SERVING])
        infer = saved_model_loaded.signatures['serving_default']
        print('Model loaded.')
        print()

        # creates kafka object
        kafkaQueue = CreateQueue(bootstrap_servers=FLAGS.bootstrap_servers,
                                    topic=FLAGS.kafka_topic,
                                    mechanism='PLAIN',
                                    security='SASL_SSL',
                                    username= FLAGS.kafka_username,
                                    password=FLAGS.kafka_password)
        
        start_prometheus_exposure(8000)

        detection_counter = counter(
            name='detection_counter',
            description='counts number of detections at each batch pass'
        )

        while True:
            
            try:
                print('Listening...')

                # gets message from kafka broker
                messages = kafkaQueue.ReceiveMessages()
                    
                # iterate through messages
                for message in messages:

                    # starts couting time of download
                    start = time.time()

                    print('Downloading video...')
                    download_video(
                        api_address=FLAGS.vault_api_address,
                        access_key=FLAGS.vault_access_key,
                        secret_access_key=FLAGS.vault_secret_access_key,
                        message=message,
                        video_folder=FLAGS.inputs
                    )
                    # time to download video
                    download_time = time.time() - start

                    video_path = FLAGS.inputs + '/video.mp4'

                    ##############################################
                    # loads video using decord
                    decr_vid = VideoReader(video_path, ctx=cpu(0), height=input_size, width=input_size)
                    #############################################
                    
                    # capture video with openCv for FPS information
                    try:
                        vid = cv2.VideoCapture(int(video_path))
                    except:
                        vid = cv2.VideoCapture(video_path)

                    fps = vid.get(cv2.CAP_PROP_FPS)
                    print('Beginning detection on video...')

                    # start counting time of detection
                    detection_start = time.time()

                    total_frames = len(decr_vid)
                    
                    for i in range(0, total_frames, FLAGS.batch_size):

                        # indexes of frames to get, relative to entire video
                        indexes = np.arange(
                            start=i,
                            stop=min((i+FLAGS.batch_size), total_frames) 
                        )

                        batch_data_decr = decr_vid.get_batch(indexes).asnumpy() / 255
                        batch_data_decr = tf.constant(batch_data_decr, dtype=tf.float32)
                        
            

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

                        max_detections = valid_detections[max_detections_on_batch_index]

                        detection_counter.set(value=max_detections)
                        
                        print(
                            '{} objects detected at {}.{:02.0f}'.format(
                                max_detections,
                                detection_time, fsec
                            )
                        )
                    print('Download time: {:.2f}'.format(download_time))
                    print('Detection time: {:.2f}'.format(time.time() - detection_start))
                    print('Total time: {:.2f}'.format(time.time() - start))
                    print()
        

            except Exception as e:
                print("error..")
                print(e)
                pass
            
if __name__ == '__main__':
    try:
        app.run(main)
    except SystemExit:
        pass
