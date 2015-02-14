__author__ = 'denis_makogon'

import argparse


# Decorators for actions
def args(*args, **kwargs):
    def _decorator(func):
        func.__dict__.setdefault('args', []).insert(0, (args, kwargs))
        return func
    return _decorator


def methods_of(obj):
    """Get all callable methods of an object that don't start with underscore
    returns a list of tuples of the form (method_name, method)
    """
    result = []
    for i in dir(obj):
        if callable(getattr(obj, i)) and not i.startswith('_'):
            result.append((i, getattr(obj, i)))
    return result


def add_command_parsers(categories):

    def _subparser(subparsers):
        for category in categories:
            command_object = categories[category]()

            desc = getattr(command_object, 'description', None)
            parser = subparsers.add_parser(category, description=desc)
            parser.set_defaults(command_object=command_object)

            category_subparsers = parser.add_subparsers(dest='action')

            for (action, action_fn) in methods_of(command_object):
                parser = category_subparsers.add_parser(
                    action, description=desc)

                action_kwargs = []
                for args, kwargs in getattr(action_fn, 'args', []):
                    kwargs.setdefault('dest', args[0][2:])
                    if kwargs['dest'].startswith('action_kwarg_'):
                        action_kwargs.append(
                            kwargs['dest'][len('action_kwarg_'):])
                    else:
                        action_kwargs.append(kwargs['dest'])
                        kwargs['dest'] = 'action_kwarg_' + kwargs['dest']

                    parser.add_argument(*args, **kwargs)

                parser.set_defaults(action_fn=action_fn)
                parser.set_defaults(action_kwargs=action_kwargs)

                parser.add_argument('action_args', nargs='*',
                                    help=argparse.SUPPRESS)

    return _subparser
