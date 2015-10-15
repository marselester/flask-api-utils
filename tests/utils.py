# coding: utf-8
import json

import mohawk


class HawkTestMixin(object):
    def signed_request(self, credentials, method='GET', path='/', data=None):
        url = 'http://localhost' + path
        content = json.dumps(data)
        content_type = 'application/json'

        sender = mohawk.Sender(
            credentials,
            url,
            method,
            content,
            content_type
        )

        return self.client.open(
            method=method,
            path=path,
            headers={'Authorization': sender.request_header},
            data=content,
            content_type=content_type
        )
