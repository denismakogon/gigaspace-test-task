__author__ = 'dmakogon'


class OpenstackException(Exception):
    """
    Base Exception

    To correctly use this class, inherit from it and define
    a 'message' property. That message will get printf'd
    with the keyword arguments provided to the constructor.
    """
    message = "An unknown exception occurred"

    def __init__(self, **kwargs):
        try:
            self._error_string = self.message % kwargs
        except Exception as e:
            raise e

    def __str__(self):
        return self._error_string


class EmptyCatalog(OpenstackException):
    message = "Service catalog wasn't found."


class NoServiceEndpoint(OpenstackException):
    """Could not find requested endpoint in Service Catalog."""
    message = ("Endpoint not found for service_type=%(service_type)s, "
               "endpoint_type=%(endpoint_type)s, "
               "endpoint_region=%(endpoint_region)s.")
