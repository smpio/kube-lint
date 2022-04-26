"""
All namespaces should have `critical-priority` ResourceQuota.
"""

from kubelint import Issue, multi_resource_spec


@multi_resource_spec(
    namespaces={'group': '', 'kind': 'Namespace'},
    quotas={'group': '', 'kind': 'ResourceQuota'}
)
def check(namespaces, quotas):
    namespaces_with_quota = {q.metadata.namespace for q in quotas if q.metadata.name == 'critical-priority'}
    for ns in namespaces:
        if ns.metadata.name not in namespaces_with_quota:
            yield Issue(ns, 'no `critical-priority` ResourceQuota')
