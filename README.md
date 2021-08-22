# Kubeflow Kerberos.io

## Structure

- All Kubeflow components, their source code, `.yaml` and `Dockerfile` files are in the `kubeflow_components` folder.
- Each pipeline folder only holds the `.yaml` files for each component it needs. The pipelines are built by the `make_pipeline.py` python script.

 ## Hints

 * Disable/Enable caching for inputs/outputs of runs run previously (described [here](https://www.kubeflow.org/docs/components/pipelines/caching/)):
    - Disable:

        `export NAMESPACE=kubeflow`

        ( to make sure `mutatingwebhookconfiguration` exists in your cluster):

        `kubectl get mutatingwebhookconfiguration cache-webhook-${NAMESPACE}`

        ```kubectl patch mutatingwebhookconfiguration cache-webhook-${NAMESPACE} --type='json' -p='[{"op":"replace", "path": "/webhooks/0/rules/0/operations/0", "value": "DELETE"}]'```

    - Enable:

        `export NAMESPACE=kubeflow`

        ( to make sure `mutatingwebhookconfiguration` exists in your cluster):

        `kubectl get mutatingwebhookconfiguration cache-webhook-${NAMESPACE}`

        ```kubectl patch mutatingwebhookconfiguration cache-webhook-${NAMESPACE} --type='json' -p='[{"op":"replace", "path": "/webhooks/0/rules/0/operations/0", "value": "CREATE"}]'```

* If Kafka deployment fails to start and logs show 
    ```mkdir: cannot create directory '/bitnami/kafka/data': Permission denied```:

    - run:
    
        ```helm upgrade kafka bitnami/kafka --set volumePermissions.enabled=true``` 

        and
    
        ```helm upgrade kafka bitnami/kafka --set zookeeper.volumePermissions.enabled=true```