__author__ = 'dmakogon'

from gigaspace.common import utils

ENV = utils.ENV


class UserdataTemplate(object):
    """
    Userdata is used to format volume right after
    operating system would finish file
    system partitioning and device mapping
    """
    _template_name = "user.data"

    def get_userdata(self):
        """
        Extracts userdata script content.
        :return userdata content
        :rtype: basestring
        """
        try:
            template = ENV.get_or_select_template(self._template_name)
            return template.render()
        except Exception:
            print("Template is missing.")
