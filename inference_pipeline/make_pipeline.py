import kfp
import kfp.components as comp
from kfp import dsl

downloader_op = comp.load_component_from_file('./download_and_extract_google_drive_op.yaml')
predict_video_metadata_op = comp.load_component_from_file('./predict_metadata_op.yaml')

@dsl.pipeline(name='metadata_inference_pipeline')
def metadata_inference_pipeline(
    tf_model_gd_id,
    gpu,
    batch_size,
    score,
    bootstrap_servers,
    kafka_topic,
    kafka_username,
    kafka_password,
    vault_api_address,
    vault_access_key,
    vault_secret_access_key
):
    
    # download model task
    download_tf_model_task = downloader_op(google_drive_id=tf_model_gd_id)


    predict_video_task = predict_video_metadata_op(
        tensorflow_model=download_tf_model_task.output,
        gpu=gpu,
        batch_size=batch_size,
        score=score,
        bootstrap_servers=bootstrap_servers,
        kafka_topic=kafka_topic,
        kafka_username=kafka_username,
        kafka_password=kafka_password,
        vault_api_address=vault_api_address,
        vault_access_key=vault_access_key,
        vault_secret_access_key=vault_secret_access_key
        )

kfp.compiler.Compiler().compile(
    pipeline_func=metadata_inference_pipeline,
    package_path='pipeline.yaml')