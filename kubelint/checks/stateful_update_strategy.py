"""
Checks whether stateful deployment (i.e. deployment with PVC volume) has Recreate update strategy.
"""

from kubelint import Issue
from kubernetes import client


def check(namespace):
    api = client.AppsV1beta1Api()

    if namespace is None:
        resource = api.list_deployment_for_all_namespaces()
    else:
        resource = api.list_namespaced_deployment(namespace)

    for deploy in resource.items:
        if deploy.spec.strategy.type == 'Recreate':
            continue
        if not deploy.spec.template.spec.volumes:
            continue
        if any(v.persistent_volume_claim for v in deploy.spec.template.spec.volumes):
            yield Issue(deploy, 'Stateful Deployment should have `Recreate` update strategy', list_resource=resource)
