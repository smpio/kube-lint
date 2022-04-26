class Issue:
    ERROR = 'ERROR'
    WARNING = 'WARNING'

    def __init__(self, object, description, severity=ERROR,
                 object_name=None,
                 namespace=None,
                 api_version=None,
                 object_kind=None,
                 list_resource=None):
        if object_name is None and object is not None:
            object_name = object.metadata.name

        if namespace is None and object is not None:
            namespace = object.metadata.namespace

        if api_version is None and object is not None:
            api_version = object.api_version
        if api_version is None and list_resource is not None:
            api_version = list_resource.api_version

        if object_kind is None and object is not None:
            object_kind = object.kind
        if object_kind is None and list_resource is not None:
            object_kind = list_resource.removesuffix('List')

        self.object = object
        self.description = description
        self.severity = severity
        self.object_name = object_name
        self.namespace = namespace
        self.api_version = api_version
        self.object_kind = object_kind

    def __str__(self):
        return '{} {}: {}'.format(self.object_kind, self.full_object_name, self.description)

    @property
    def full_object_name(self):
        if self.namespace is None:
            return self.object_name
        else:
            return '{}/{}'.format(self.namespace, self.object_name)
