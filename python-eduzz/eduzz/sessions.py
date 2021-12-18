import requests

from urllib.parse import urljoin


ENDPOINT = 'https://api2.eduzz.com/'

# Taken from https://github.com/requests/toolbelt/
class BaseUrlSession(requests.Session):
    base_url = None

    def __init__(self, base_url=None):
        if base_url:
            self.base_url = base_url
        super(BaseUrlSession, self).__init__()

    def request(self, method, url, *args, **kwargs):
        """Send the request after generating the complete URL."""
        url = self.create_url(url)
        return super(BaseUrlSession, self).request(
            method, url, *args, **kwargs
        )

    def prepare_request(self, request, *args, **kwargs):
        """Prepare the request after generating the complete URL."""
        request.url = self.create_url(request.url)
        return super(BaseUrlSession, self).prepare_request(
            request, *args, **kwargs
        )

    def create_url(self, url):
        """Create the URL based off this partial path."""
        return urljoin(self.base_url, url)


class EduzzAPIError(requests.HTTPError):
    """An API level error has ocurred."""


class ResponseAdapter:
    def __init__(self, r):
        self._response = r

    def __getattr__(self, item):
        return getattr(self._response, item)

    def raise_for_status(self):
        documented_statuses = (400, 401, 403, 404, 405, 409, 422, 500)
        if self.status_code in documented_statuses:
            json = self.json()
            code, details = json['code'], json['details']

            raise EduzzAPIError(f'{code} {details}', response=self)

        self._response.raise_for_status()


class EduzzSession(BaseUrlSession):
    def __init__(self, base_url=ENDPOINT):
        super(EduzzSession, self).__init__(base_url=base_url)

    def request(self, method, url, *args, **kwargs):
        r = super(EduzzSession, self).request(method, url, *args, **kwargs)
        return ResponseAdapter(r)