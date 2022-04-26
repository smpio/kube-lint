"""
Report all PersistentVolumes in Released state.
"""

from kubelint import Issue, resource_spec


@resource_spec(group='', kind='PersistentVolume')
def check(pv):
    if pv.status.phase == 'Released':
        yield Issue(pv, 'PV is Released')
