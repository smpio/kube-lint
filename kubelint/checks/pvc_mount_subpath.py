"""
All pods should mount PVCs with subPath.
"""

from kubelint import Issue
from kubernetes import client


def check(namespace):
    api = client.CoreV1Api()

    if namespace is None:
        resource = api.list_pod_for_all_namespaces()
    else:
        resource = api.list_namespaced_pod(namespace)

    for pod in resource.items:
        if not pod.spec.volumes:
            continue

        for v in pod.spec.volumes:
            if not v.persistent_volume_claim:
                continue
            for c in pod.spec.containers:
                if not c.volume_mounts:
                    continue
                for m in c.volume_mounts:
                    if m.name == v.name and not m.sub_path:
                        yield Issue(pod, 'should mount PVC with subPath', list_resource=resource)
