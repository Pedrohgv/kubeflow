docker run --rm --runtime=nvidia -it \
-v /home/pedro/Desktop/kubeflow/kubeflow_components/predict-metadata-op:/mount \
-v /home/pedro/Desktop/kubeflow/kubeflow_components/predict-metadata-op/tf_model:/tf_model  \
-v /home/pedro/Desktop/kubeflow/kubeflow_components/predict-metadata-op/input_videos:/input_videos \
-v /home/pedro/Desktop/kubeflow/kubeflow_components/predict-metadata-op/output_videos:/output_videos \
pedrohgv/predict-metadata-op:latest python mount/src/detect_video.py --score 0.7 --batch_size 32
