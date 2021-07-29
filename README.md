# Kubeflow Kerberos.io

## Structure

- All Kubeflow components, their source code, `.yaml` and `Dockerfile` files are in the `kubeflow_components` folder.
- Each pipeline folder only holds the `.yaml` files for each component it needs. The pipelines are built by the `make_pipeline.py` python script.