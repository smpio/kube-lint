"""
All pods should mount PVCs with subPath.
"""

from kubelint import Issue, resource_spec


@resource_spec(group='', kind='Pod')
def check(pod):
    if not pod.spec.volumes:
        return

    for v in pod.spec.volumes:
        if not v.persistentVolumeClaim:
            continue
        for c in pod.spec.containers:
            for m in c.volumeMounts:
                if m.name == v.name and not m.subPath:
                    yield Issue(pod, 'should mount PVC with subPath')
