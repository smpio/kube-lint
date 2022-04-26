import logging

import raven
from kubernetes.client import ApiClient
from kubernetes.dynamic import DynamicClient

log = logging.getLogger(__name__)


class Scanner:
    def __init__(self, checks):
        self.checks = checks
        self.sentry = None
        self.client = DynamicClient(ApiClient())
        self.resources_cache = {}

    def scan(self, namespace=None):
        for check in self.checks:
            log.info('Scanning using %s', check)
            try:
                resource_spec = check._kubelint_resource_spec
            except AttributeError:
                log.error('Invalid check %s: no decorator', check)
                continue
            resources = self.client.resources.search(**resource_spec)
            if not resources:
                log.error('Invalid check %s: no resources matching %s', check, resource_spec)
                continue
            log.debug('Selector %s matches %s', resource_spec, resources)
            resource = resources[0]
            try:
                obj_list = self.resources_cache[resource]
            except KeyError:
                obj_list = self.resources_cache[resource] = self.client.get(resource, namespace=namespace)
            for obj in obj_list.items:
                self.report(check(obj), check.__module__)

    def report(self, issues, check_name):
        for issue in issues:
            print(issue)
            if self.sentry:
                self.sentry.captureMessage(str(issue), data={
                    'logger': check_name,
                    'level': issue.severity.lower(),
                }, extra={
                    'namespace': issue.namespace,
                    'object_name': issue.object_name,
                    'api_version': issue.api_version,
                    'object_kind': issue.object_kind,
                })

    @property
    def sentry_dsn(self):
        return self.sentry.dsn

    @sentry_dsn.setter
    def sentry_dsn(self, value):
        self.sentry = raven.Client(value,
                                   raise_send_errors=True,
                                   install_sys_hook=False,
                                   install_logging_hook=False,
                                   enable_breadcrumbs=False,
                                   include_versions=False,
                                   name='kubernetes',
                                   release=self.client.version,
                                   context={})
