import kfp
import kfp.components as comp
from kfp import dsl

downloader_op = comp.load_component_from_file('./download-and-extract-google-drive-op/component.yaml')
merge_files_op = comp.load_component_from_file('./merge-files-op/component.yaml')
convert_pascal_2_yolo_op = comp.load_component_from_file('./convert-pascal-2-yolo-op/component.yaml')

# prints contents of output folder form last component
check_pipeline_output_op = comp.load_component_from_file('./check-pipeline-output-op/component.yaml')

@dsl.pipeline(name='test_1')
def test_pipeline(google_drive_id, classes):

    download_task = downloader_op(google_drive_id=google_drive_id)

    merge_files_task = merge_files_op(nested_folder=download_task.output)

    convert_pascal_2_yolo_task = convert_pascal_2_yolo_op(
        pascal_folder=merge_files_task.output,
        classes=classes
    )
    
    last_op = convert_pascal_2_yolo_task
    check_pipeline_output_task = check_pipeline_output_op(previous_output_folder=last_op.output)


kfp.compiler.Compiler().compile(
    pipeline_func=test_pipeline,
    package_path='pipeline.yaml')