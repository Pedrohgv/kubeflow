FROM tensorflow/tensorflow:2.3.0rc0-gpu

COPY ./src /src

RUN apt-get update
RUN apt-get install ffmpeg libsm6 libxext6  -y

# install requirements
COPY ./requirements-gpu.txt .
RUN pip3 install -r requirements-gpu.txt

# creates folder to be used with docker engine containing the darknet model to be transformed
RUN mkdir /darknet_model

# creates folder that will hold the converted tensorflow model
RUN mkdir /tf_model

CMD python ./src/save_model.py --input /darknet_model --output /tf_model
