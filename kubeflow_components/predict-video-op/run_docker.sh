echo -n "Enter your tensorflow model absolute path (folder containing tensorflow model files and config/obj.names):" 
read tf_model

echo -n "Enter the path for the input folder (folder will contain the videos to be run the detection task on):" 
read input_videos

echo -n "Enter the path for the output folder (folder will hold videos with object detection):" 
read output_videos

docker run --rm --runtime=nvidia -it -v $tf_model:/tf_model -v $input_videos:/input_videos -v $output_videos:/output_videos pedrohgv/predict-video-op:latest
