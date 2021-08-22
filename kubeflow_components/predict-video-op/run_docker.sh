#echo -n "Enter your tensorflow model absolute path (folder containing tensorflow model files and config/obj.names):" 
#read tf_model

#echo -n "Enter the path for the input folder (folder will contain the videos to be run the detection task on):" 
#read input_videos

#echo -n "Enter the path for the output folder (folder will hold videos with object detection):" 
#read output_videos

tf_model="$HOME/Desktop/kubeflow/kubeflow_components/predict-video-op/tf_model"
input_videos="$HOME/Desktop/kubeflow/kubeflow_components/predict-video-op/input_videos"
output_videos="$HOME/Desktop/kubeflow/kubeflow_components/predict-video-op/output_videos"
mount="$HOME/Desktop/kubeflow/kubeflow_components/predict-video-op"
docker run --runtime=nvidia --rm -it -v $mount:/mount -v $tf_model:/tf_model -v $input_videos:/input_videos -v $output_videos:/output_videos pedrohgv/predict-video-op:latest python /src/detect_video.py --score 0.7
