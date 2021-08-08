import kfp
import kfp.components as comp
from kfp import dsl

gpu_print_op = comp.load_component_from_file('./hello-world-gpu.yaml')

@dsl.pipeline(name='gpu_check_pipeline')
def gpu_check_pipeline():
    
    gpu_print_task = gpu_print_op()


kfp.compiler.Compiler().compile(
    pipeline_func=gpu_check_pipeline,
    package_path='gpu_check_pipeline.yaml')