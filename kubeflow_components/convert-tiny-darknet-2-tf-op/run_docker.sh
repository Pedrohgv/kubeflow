#echo -n "Enter your tiny-yolo model (darknet framework) absolute path (folder containing darknet-tiny.weights and config/obj.names): " 
#read input_path

#echo -n "Enter the path for the output folder (folder will contain the converted tensorflow model files as well as the config folder): " 
#read output_path

input_path="/home/pedro/Desktop/kubeflow/kubeflow_components/convert-tiny-darknet-2-tf-op/darknet_model"
output_path="/home/pedro/Desktop/kubeflow/kubeflow_components/convert-tiny-darknet-2-tf-op/tf_model"

docker run --runtime=nvidia --rm -it -v $input_path:/darknet_model -v $output_path:/tf_model pedrohgv/convert-tiny-darknet-2-tf-op:latest
