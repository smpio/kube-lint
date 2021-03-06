import logging

import raven
from kubernetes import client

log = logging.getLogger(__name__)


class Scanner:
    def __init__(self, checks):
        self.checks = checks
        self.sentry = None
        self.apiserver_version = client.VersionApi().get_code().git_version

    def scan(self, namespace=None):
        for check in self.checks:
            self.report(check(namespace), check.__module__)

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
                                   release=self.apiserver_version,
                                   context={})
