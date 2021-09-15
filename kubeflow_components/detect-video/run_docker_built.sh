docker run --rm --runtime=nvidia -it \
-v $HOME/Desktop/nvidia-gpu-kubernetes/kubeflow_components/detect-video/tf_model:/tf_model  \
-v $HOME/Desktop/nvidia-gpu-kubernetes/kubeflow_components/detect-video/input_videos:/input_videos \
\
pedrohgv/detect-video:latest python /src/detect_video.py \
\
--score 0.7 \
--gpu 0 \
--batch_size 32 \
\
--bootstrap_servers "pkc-ldjyd.southamerica-east1.gcp.confluent.cloud:9092" \
--kafka_topic "kubeflow" \
--kafka_username "KUYE7CHLZJF6DCC7" \
--kafka_password "CCfiCkB2GmLb0ARAavO2X92jNE5FJYX3hhw94VHaajNA0NfJ4J4744fuDywOIBQB" \
\
--vault_api_address "https://staging.api.vault.kerberos.live/storage/blob" \
--vault_access_key "ABCDEFGHI!@#$%12345" \
--vault_secret_access_key "JKLMNOPQRSTUVWXYZ!@#$%67890" \
\
--detection_counter_name 'detection_counter_GPU_0'
