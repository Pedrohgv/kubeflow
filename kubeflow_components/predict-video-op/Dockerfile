FROM tensorflow/tensorflow:2.4.2-gpu

# install video libraries
RUN apt-get update
RUN apt-get install ffmpeg libsm6 libxext6  -y

# install requirements
COPY ./requirements-gpu.txt .
RUN pip3 install -r requirements-gpu.txt

# source code
COPY ./src /src

# creates folder to be used with docker engine containing the tensorflow model to be used for prediction
RUN mkdir /tf_model

# creates folder that will contain the video to be predicted. must be named 'input.mp4'
RUN mkdir /input_videos

# creates folder that will hold the predicted video, named 'output.avi'
RUN mkdir /output_videos

CMD python ./src/detect_video.py --tf_model /tf_model --inputs /input_videos --outputs /output_videos
