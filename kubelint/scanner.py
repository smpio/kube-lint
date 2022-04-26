import logging

import raven
from kubernetes.client import ApiClient
from kubernetes.dynamic import DynamicClient

log = logging.getLogger(__name__)


class Scanner:
    def __init__(self, namespace=None):
        self.sentry = None
        self.client = DynamicClient(ApiClient())
        self.resources_cache = {}
        self.namespace = namespace

    def scan(self, checks):
        for check in checks:
            log.info('Scanning using %s', check.__module__)
            try:
                self.do_check(check)
            except Exception as err:
                log.error('Invalid check %s: %s', check.__module__, err)
                continue

    def do_check(self, check):
        resource_spec = getattr(check, '_kubelint_resource_spec', None)
        if resource_spec is not None:
            self.do_simple_check(check, resource_spec)
            return
        multi_resource_spec = getattr(check, '_kubelint_multi_resource_spec', None)
        if multi_resource_spec is not None:
            self.do_multi_check(check, multi_resource_spec)
            return
        raise Exception('no decorator')

    def do_simple_check(self, check, resource_spec):
        for obj in self.get_objects(resource_spec):
            self.report(check(obj), check.__module__)

    def do_multi_check(self, check, multi_resource_spec):
        kwargs = {k: self.get_objects(v) for k, v in multi_resource_spec.items()}
        self.report(check(**kwargs), check.__module__)

    def get_objects(self, spec):
        resources = self.client.resources.search(**spec)
        if not resources:
            raise Exception(f'no resources matching {spec}')
        log.debug('Selector %s matches %s', spec, resources)
        resource = resources[0]
        try:
            obj_list = self.resources_cache[resource]
        except KeyError:
            obj_list = self.resources_cache[resource] = self.client.get(resource, namespace=self.namespace)
        return obj_list.items

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
