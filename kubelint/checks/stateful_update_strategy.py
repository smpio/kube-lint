"""
Checks whether stateful deployment (i.e. deployment with PVC volume) has Recreate update strategy.
"""

from kubelint import Issue, resource_spec


@resource_spec(group='apps', kind='Deployment')
def check(deploy):
    if deploy.spec.strategy.type == 'Recreate':
        return
    if not deploy.spec.template.spec.volumes:
        return
    if any(v.persistentVolumeClaim for v in deploy.spec.template.spec.volumes):
        yield Issue(deploy, 'Stateful Deployment should have `Recreate` update strategy')
