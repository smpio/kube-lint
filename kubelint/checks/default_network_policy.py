"""
All namespaces should have `default` NetworkPolicy.
"""

from kubelint import Issue, multi_resource_spec


@multi_resource_spec(
    namespaces={'group': '', 'kind': 'Namespace'},
    policies={'group': 'networking.k8s.io', 'kind': 'NetworkPolicy'}
)
def check(namespaces, policies):
    namespaces_with_default_policy = {p.metadata.namespace for p in policies if p.metadata.name == 'default'}
    for ns in namespaces:
        if ns.metadata.name not in namespaces_with_default_policy:
            yield Issue(ns, 'no default NetworkPolicy')
