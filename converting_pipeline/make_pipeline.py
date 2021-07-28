import kfp
import kfp.components as comp
from kfp import dsl

downloader_op = comp.load_component_from_file('./download-and-extract-google-drive-op/component.yaml')
convert_tiny_darknet_2_tf_op = comp.load_component_from_file('./convert-tiny-darknet-2-tf-op/component.yaml')

# prints contents of output folder form last component
check_pipeline_output_op = comp.load_component_from_file('./check-pipeline-output-op/component.yaml')

@dsl.pipeline(name='convert-tiny-darknet-2-tf-op')
def test_pipeline(google_drive_id, score_threshold):

    download_task = downloader_op(google_drive_id=google_drive_id)

    convert_tiny_darknet_2_tf_task = convert_tiny_darknet_2_tf_op(darknet_model=download_task.output)

    
    last_op = convert_tiny_darknet_2_tf_task
    check_pipeline_output_task = check_pipeline_output_op(previous_output_folder=last_op.output)


kfp.compiler.Compiler().compile(
    pipeline_func=test_pipeline,
    package_path='pipeline.yaml')