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


def print_list(objs, fields, formatters={}, order_by=None, obj_is_dict=False,
               labels={}):
    try:
        _output_override(objs, 'list')
        return
    except BaseException:
        pass
    # Make nice labels from the fields, if not provided in the labels arg
    if not labels:
        labels = {}
    for field in fields:
        if field not in labels:
            # No underscores (use spaces instead) and uppercase any ID's
            label = field.replace("_", " ").replace("id", "ID")
            # Uppercase anything else that's less than 3 chars
            if len(label) < 3:
                label = label.upper()
            # Capitalize each word otherwise
            else:
                label = ' '.join(word[0].upper() + word[1:]
                                 for word in label.split())
            labels[field] = label

    pt = prettytable.PrettyTable(
        [labels[field] for field in fields], caching=False)
    # set the default alignment to left-aligned
    align = dict((labels[field], 'l') for field in fields)
    set_align = True
    for obj in objs:
        row = []
        for field in fields:
            if formatters and field in formatters:
                row.append(formatters[field](obj))
            elif obj_is_dict:
                data = obj.get(field, '')
            else:
                data = getattr(obj, field, '')
            row.append(data)
            # set the alignment to right-aligned if it's a numeric
            if set_align and hasattr(data, '__int__'):
                align[labels[field]] = 'r'
        set_align = False
        pt.add_row(row)
    pt._align = align

    if not order_by:
        order_by = fields[0]
    order_by = labels[order_by]
    _print(pt, order_by)
