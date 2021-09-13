# Kerberos.io ML Integration

This repository is meant to demonstrate how to set up a Computer Vision application on Kubernetes, making use of Nvidia GPU acceleration for Machine Learning workloads. It integrates with the robust and scalable surveillance solution at [kerberos.io](https://kerberos.io/).

## Setup
In order to run the examples, one needs to have a running Kubernetes cluster, the correct Nvidia Drivers, and the [Nvidia-Container-Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html) properly installed. A running instance of Kerberos Vault is also needed.

## Kubeflow
Some examples have been built to be run as [Kubeflow](https://www.kubeflow.org/) pipelines. Kubeflow is a tool developed for MLOps and Kubernetes and helps Machine Learning Engineers track their training sessions and experiments with different parameters and inputs.
