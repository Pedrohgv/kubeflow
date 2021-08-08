import kfp
from kfp import dsl

def gpu_smoking_check_op():
    return dsl.ContainerOp(
        name='check',
        image='tensorflow/tensorflow:2.4.2-gpu',
        command=['sh', '-c'],
        arguments=['nvidia-smi']
    ).set_gpu_limit(1)

@dsl.pipeline(
    name='GPU smoke check',
    description='smoke check as to whether GPU env is ready.'
)
def gpu_pipeline():
    gpu_smoking_check = gpu_smoking_check_op()

if __name__ == '__main__':
    kfp.compiler.Compiler().compile(gpu_pipeline, 'gpu_smoking_pipeline.yaml')
