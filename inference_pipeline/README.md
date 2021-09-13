# Object Detection with Kubernetes and Kerberos.io


## Prometheus setup
In order to collect and display metadata from our detections (as well as resource metrics from our node), we will employ a widely used tool in DevOps called [Prometheus](https://prometheus.io/docs/introduction/overview/). Prometheus will provide out-of-the-box monitoring tools for our node, as well as the ability to set up custom metrics (in our case, we'll be collecting the max number of detected objects at each batch of frames in the videos).

There are several options for installing Prometheus; fortunately, a Helm Chart is available with all the required components needed (including [Grafana](https://grafana.com/), a dashboard visualization tool) that can be easily installed with:

	helm repo add prometheus-community https://prometheus-						  	community.github.io/helm-charts
	helm repo update
	helm install [RELEASE_NAME] prometheus-community/kube-prometheus-stack

Where `[RELEASE_NAME]` should be replaced by how you want to call your Prometheus deployment. Once you have deployed the stack, you should wait for it to finish the initialization. To check the `READY` status on all Kubernetes resources in the `default` namespace, type:

    kubectl get all -n default

 You should see something like this:

![k8s_resources](https://user-images.githubusercontent.com/27008096/132860852-3718cdc3-6461-48c6-aa33-cb789050ddf1.png)

## Grafana access
To see the Grafana dashboard, the UI must be exposed to the host, so we can access it through the browser. We can do that by port-forwarding the right port on the Grafana Kubernetes service to a port  on the host, like:
	kubectl port-forward service/prometheus-stack-grafana 3000:80

You should be able to see the dashboard on `https://localhost:3000` in the browser:

![grafana_dashboard](https://user-images.githubusercontent.com/27008096/132876950-c4da4e28-d670-4fab-8a99-278d1fc70887.png)









