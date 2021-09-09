# GPU Smoke 

Very simple kubeflow pipeline (and also standalone Kubernetes pod) that checks if GPU is accessible in the system. The `nvidia-smi` command used inside a tensorflow image and its output must be checked inside the logs of the container.