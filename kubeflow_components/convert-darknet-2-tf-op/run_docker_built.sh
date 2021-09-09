

input_path="$HOME/Desktop/nvidia-gpu-kubernetes/kubeflow_components/convert-darknet-2-tf-op/darknet_model"
output_path="$HOME/Desktop/nvidia-gpu-kubernetes/kubeflow_components/convert-darknet-2-tf-op/tf_model"

#docker run --runtime=nvidia --rm -it \
docker run --rm -it \
-v $input_path:/darknet_model \
-v $output_path:/tf_model \
pedrohgv/convert-darknet-2-tf-op:latest
