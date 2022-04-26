import os
import sys
import logging
import argparse
import importlib.util
import importlib.machinery

from utils.kubernetes.config import configure

from .scanner import Scanner

log = logging.getLogger(__name__)


def main():
    default_checks_dir = os.path.join(os.path.dirname(__file__), 'checks')

    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('--master', help='kubernetes api server url')
    arg_parser.add_argument('--in-cluster', action='store_true', help='configure with in-cluster config')
    arg_parser.add_argument('--sentry-dsn', help='send errors and warnings to sentry')
    arg_parser.add_argument('-n', '--namespace', help='scan only this namespace (default to scan all)')
    arg_parser.add_argument('-c', '--check', default=[], action='append', help='file or directory with checks')
    arg_parser.add_argument('--no-defaults', action='store_true', help='skip default checks')
    arg_parser.add_argument('--log-level', default='WARNING')
    args = arg_parser.parse_args()

    logging.basicConfig(format='%(levelname)s: %(message)s', level=args.log_level)
    configure(args.master, args.in_cluster)

    if not args.no_defaults:
        args.check.insert(0, default_checks_dir)

    checks = list(load_checks(args.check))
    scanner = Scanner(args.namespace)
    scanner.sentry_dsn = args.sentry_dsn
    scanner.scan(checks)


def load_checks(checks):
    for check in checks:
        for root, dirs, files in os.walk(check, followlinks=True, onerror=reraise):
            for file in files:
                path = os.path.join(root, file)
                if any(path.endswith(suffix) for suffix in importlib.machinery.SOURCE_SUFFIXES):
                    yield load_check(path)


def load_check(path):
    module_name = os.path.splitext(os.path.basename(path))[0]
    if module_name in sys.modules:
        raise Exception('Duplicate checks with same name', module_name)
    spec = importlib.util.spec_from_file_location(module_name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.check


def reraise(err):
    raise err


if __name__ == '__main__':
    main()
