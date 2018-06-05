# Copyright (c) 2017 Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


from __future__ import (absolute_import, division, print_function)
__metaclass__ = type


ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['preview'],
    'supported_by': 'community'
}


from ansible.errors import AnsibleFilterError
from ansible.module_utils.six.moves.urllib.parse import urlsplit
from ansible.utils import helpers


def sort_routes(route_list, alias='routeinfo_filter'):

    route_type = {}
    route_list = []
    for route in route_list:
        if route.get('PROTOCOL') == 'S':
            route_list['static'] = route
        elif route.get('PROTOCOL') == 'B':
            route_list['bgp'] = route
        elif route.get('PROTOCOL') == 'O':
            route_list['ospf'] = route
        elif route.get('PROTOCOL') == 'L':
            route_list['local'] = route
        elif route.get('PROTOCOL') == 'C':
            route_list['connected'] = route
            
    results = helpers.object_to_dict(urlsplit(value), exclude=['count', 'index', 'geturl', 'encode'])

    # If a query is supplied, make sure it's valid then return the results.
    # If no option is supplied, return the entire dictionary.
    if query:
        if query not in results:
            raise AnsibleFilterError(alias + ': unknown URL component: %s' % query)
        return results[query]
    else:
        return results


# ---- Ansible filters ----
class FilterModule(object):
    ''' URI filter '''

    def filters(self):
        return {
            'route_info': sort_routes
        }
