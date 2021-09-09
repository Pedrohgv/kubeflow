

input_path="$HOME/Desktop/nvidia-gpu-kubernetes/kubeflow_components/convert-darknet-2-tf-op/darknet_model"
output_path="$HOME/Desktop/nvidia-gpu-kubernetes/kubeflow_components/convert-darknet-2-tf-op/tf_model"
mount_path="$HOME/Desktop/nvidia-gpu-kubernetes/kubeflow_components/convert-darknet-2-tf-op"

#docker run --runtime=nvidia --rm -it \
docker run --rm -it \
-v $input_path:/darknet_model \
-v $output_path:/tf_model \
-v $mount_path:/mount \
pedrohgv/convert-darknet-2-tf-op:latest python /mount/src/save_model.py
