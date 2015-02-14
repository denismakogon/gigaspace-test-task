__author__ = 'dmakogon'

import sys
import simplejson as json
import prettytable
import six
import jinja2

from gigaspace.common import cfg
from oslo.utils import encodeutils

CONF = cfg.CONF
ENV = jinja2.Environment(loader=jinja2.ChoiceLoader([
                         jinja2.FileSystemLoader("~/.ssh/"),
                         jinja2.PackageLoader("gigaspace", "templates")
                         ]))


def _output_override(objs, print_as):
    """Output override flag checking.

    If an output override global flag is set, print with override
    raise BaseException if no printing was overridden.
    """
    if globals().get('json_output', False):
        if print_as == 'list':
            new_objs = []
            for o in objs:
                new_objs.append(o._info)
        elif print_as == 'dict':
            new_objs = objs
        # pretty print the json
        print(json.dumps(new_objs, indent='  '))
    else:
        raise BaseException('No valid output override')


def _print(pt, order):

    if sys.version_info >= (3, 0):
        print(pt.get_string(sortby=order))
    else:
        print(encodeutils.safe_encode(pt.get_string(sortby=order)))


def print_dict(d, property="Property"):
    try:
        _output_override(d, 'dict')
        return
    except BaseException:
        pass
    pt = prettytable.PrettyTable([property, 'Value'], caching=False)
    pt.align = 'l'
    [pt.add_row(list(r)) for r in six.iteritems(d)]
    _print(pt, property)
