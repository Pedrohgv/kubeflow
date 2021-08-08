docker run --rm --runtime=nvidia -it \
-v /home/pedro/Desktop/kubeflow/kubeflow_components/predict-metadata-op:/mount \
-v /home/pedro/Desktop/kubeflow/kubeflow_components/predict-metadata-op/tf_model:/tf_model  \
-v /home/pedro/Desktop/kubeflow/kubeflow_components/predict-metadata-op/darknet_model:/darknet_model \
pedrohgv/predict-metadata-op:latest python mount/src/save_model.py