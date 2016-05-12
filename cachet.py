"""
 API Wrapper for Cachet
    https://cachethq.io
 Makes an authenticated connection,  passes on API requests
 and makes the returned stuff be nice and pythony.
"""
from logging import getLogger
from urllib.request import Request, urlopen
from urllib.parse import urlencode
from urllib.error import HTTPError, URLError
from json import loads


class Connection(object):
    """
    Class representing a connection to a Cachet server,
    even though it's not really a connection...
    """

    def __init__(self, cachet_url, api_token):
        """Return an object representing a Cachet server connection.
        Args:
          cachet_url (string): URL of the cachet server.
          api_token (string): API authentication token.
        Returns: A cachet 'connection' object.
        """
        self.logger = getLogger(__name__)
        self.cachet_api_url = cachet_url + '/api/v1'
        self.api_token = api_token
        self.logger.debug("Setting cachet server URL: %s", self.cachet_api_url)
        self.logger.debug("Setting API Token: %s", self.api_token)

    def _do_request(self, url, method, payload=None, timeout=1):
        """ Prepare and make urllib GET request, process and translate json response.
        Args:
          url (string): the URL to get
          timeout (int): timeout in seconds
        Returns: Result of get call as Pythonized JSON
        """
        headers = {'X-Cachet-Token' : self.api_token}
        try:
            request = Request(url, payload, headers=headers, method=method)
            with urlopen(request, timeout=timeout) as response:
                data = response.read().decode('utf-8')
                return loads(data)
        except HTTPError as http_error:
            self.logger.debug("HTTPError: %s", http_error.code)
        except URLError:
            self.logger.debug("URLError")
        except ValueError:     # trap json loads on None.
            pass
        return None

    def _get(self, endpoint):
        """ Broker the GET request from a API call, handle paging
        Args:
          endpoint (string): the endpoint to get.
        Returns: A list containing the response(s), or None
        """
        results = []
        url = self.cachet_api_url + endpoint
        while True:
            response_json = self._do_request(url, method='GET')
            if not response_json:
                break
            data = response_json.get('data')
            if not isinstance(data, list):
                data = [data]
            results.extend(data)
            if not response_json.get('meta'):
                break
            url = response_json['meta']['pagination'].get('next_page')
            if not url:
                break
        return results

    def _post(self, endpoint, params):
        """Broker POST request from an API call
        Args:
          endpoint (string): The endpoint for the object to add.
          params (dict): A dictionary with the update information.
        Returns: Dict
        """
        url = self.cachet_api_url + endpoint
        payload = urlencode(params)
        payload = payload.encode('utf-8')
        results = self._do_request(url, payload=payload, method='POST')
        return results

    def _put(self, endpoint, params):
        """Broker PUT request from an API call
        Args:
          endpoint (string): The endpoint for the object to update.
          params (dict): A dictionary with the update information.
        Returns: Dict
        """
        url = self.cachet_api_url + endpoint
        payload = urlencode(params)
        payload = payload.encode('utf-8')
        results = self._do_request(url, payload=payload, method='PUT')
        return results

    def _delete(self, endpoint):
        """Broker DELETE request from an API call
        Args:
          endpoint (string): The endpoint for the object to delete.
        Returns: None
        """
        url = self.cachet_api_url + endpoint
        _ = self._do_request(url, method='DELETE')

    def _get_unwrapped(self, url):
        """Return the first item from list returned by _get, or None
        Args:
          url (string): URL to get
        Returns: A single item from the get call, usually a dict.
        """
        result = self._get(url)
        if result:
            return result[0]

#### API Calls for utility, components, incidents, metrics, subscribers ####

# utility
    def health(self):
        """ Test API endpoint (GET /ping).
        Returns: Boolean
        """
        return self._get_unwrapped('/ping') == "Pong!"

    def version(self):
        """ Cachet version (GET /version).
        Appears to be unimplemented in Docker v. 2.0.1
        Returns: version string
        """
        return self._get_unwrapped('/version')

# components
    def get_components(self):
        """ Return all components that have been created (GET /components).
        Returns: A list of dictionaries with component information.
        """
        return self._get('/components')

    def get_component(self, component_id):
        """ Return a single component, or None (GET /components/:id).
        Returns: A dictionary with component information.
        """
        url = '/components/' + str(component_id)
        return self._get_unwrapped(url)

    def create_component(self, name, status, desc="",
                         link="", order=0, group_id=0, enabled=True):
        """ Create a new component (POST /components).
        Args:
          name (string): Name of the component.
          status (int): Status of the component; 1-4.
          desc (Optional[string]): Description of the component.
          link (Optional[string]): A hyperlink to the component.
          order (Optional[int]): Order of the component. Defaults to 0.
          group_id (Optional[int]): The group_id the component is within. Defaults to 0.
          enabled (Optional[bool]): Whether the component is enabled. Defaults to True.
        Returns: A dictionary with component information.
        """
        if enabled:
            enabled_int = 1
        else:
            enabled_int = 0
        params = {'name':name, 'description':desc, 'status':status, 'link':link,
                  'order':order, 'group_id':group_id, 'enabled':enabled_int}
        return self._post('/components', params)


    def update_component(self, component_id, **args):
        """ Update a component (PUT /components/:id).
        Args:
          component_id (int): The ID of the component.
          name (Optional[string]): Name of the component.
          status (Optional[int]): Status of the component; 1-4.
          for some reason description isn't in the cachet docs for this...
          link (Optional[string]): A hyperlink to the component.
          order (Optional[int]): Order of the component.
          group_id (Optional[int]): The group_id the component is within.
          enabled (Optional[bool]): Whether the component is enabled.
        Returns: A dictionary with component information.
        """
        return self._put('/components/' + str(component_id), args)

    def delete_component(self, component_id):
        """ Delete a component (DELETE /components/:id).
        Args:
          component_id (int): ID of the component to delete.
        Returns: None
        """
        return self._delete('/components/' + str(component_id))

    def get_component_groups(self):
        """ Get all component groups which have been created, or None (GET /components/groups).
        Returns: A list of dicts with component group information.
        """
        return self._get('/components/groups')

    def get_component_group(self, group_id):
        """ Get a single component group by id (GET /components/groups/:id).
        Args:
          group_id (int): ID of the component group.
        Returns: A dict with component group information.
        """
        url = '/components/groups/' + str(group_id)
        return self._get_unwrapped(url)

    def create_component_group(self, name, order=False, collapsed=0):
        """ Create a component group (POST /components/groups).
        Args:
          name (str): Name of the component group.
          order (Optional[int]): Order of the component group.
          collapsed (Optional[int]): Collapse the group?
                 0=No,1=Yes,2=not_operational. Defaults to 0.
        Returns: Dict with group settings.
        """
        params = {'name' : name, 'collapsed' : collapsed}
        if order:
            params['order'] = order
        return self._post('/components/groups', params)

    def update_component_group(self, group_id, **args):
        """ PUT /components/groups/:id
        Args:
          group_id (int): id of the component group.
          name (Optional[str]): Name of the component group.
          order (Optional[int]): Order of the group.
          collapsed (Optional[int]): Collapse the group?
                 0=No,1=Yes,2=not_operational. Defaults to 0.
        Returns: Dict with group settings.
        """
        return self._put('/components/groups/' + str(group_id), args)

    def delete_component_group(self, group_id):
        """ DELETE /components/groups/:id
        Args:
          group_id (int): id of the component to delete.
        Returns: None
        """
        return self._delete('/components/groups/' + str(group_id))

# incidents
    def get_incidents(self):
        """ Return all incidents (GET /incidents)
        Returns: List of incident dicts
        """
        return self._get('/incidents')

    def get_incident(self, incident_id):
        """ Return a specific incident(GET /incidents/:id)
        Args:
          incident_id (int): ID of the incident to get.
        Returns: Dict of incident information
        """
        url = '/incidents/' + str(incident_id)
        return self._get_unwrapped(url)

    def create_incident(self, name, message, status, visible=1,
                        component_id=None, component_status=None, notify=False):
        """ Create a new incident (POST /incidents)
        Args:
          name (str): Name of the incident.
          message (str): Markdown formatted message with explanations.
          status (int): Status of the incident.
          visible (Optional[bool]): Whether the incident is visible. Defaults to 1
          component_id (Optional[int]): component for incident (required with component_status)
          component_status (Optional[int]): The status for the given component.
          notify (int): Whether to notify subscribers. Defaults to 0. 0 = false, 1 = true
        Returns: Dict of incident information
        """
        # TODO handle status better
        params = {'name' : name, 'message' : message, 'status' : status}
        if not visible:
            params['visible'] = 0
        if component_id:
            params['component_id'] = component_id
        if component_status:
            params['component_status'] = component_status
        if notify:
            params['notify'] = 1
        return self._post('/incidents', params)

    def update_incident(self, name, message, status, visible=True,
                        component_id=None, component_status=None, notify=False):
        """ Update an (PUT /incidents)
        Args:
          name (str): Name of the incident.
          message (str): Markdown formatted message with explanations.
          status (int): Status of the incident.
          visible (Optional[bool]): Whether the incident is visible. Defaults to True
          component_id (Optional[int]): component to update (required with component_status)
          component_status (Optional[int]): The status to update the given component with.
          notify (Optional[bool]): Whether to notify subscribers. Defaults to False.
          incident_id (int): The ID of the incident to update.

        Returns: Dict of incident information
        """
        # TODO handle status better

    def delete_incident(self, incident_id):
        """ Deletes an incident (DELETE /incidents/:id)
        Args:
          incident_id (int): The ID of the incident to delete.
        Returns: None
        """
        return self._delete('/incidents/' + str(incident_id))


# metrics
    def get_metrics(self):
        """ Returns all configured metrics (GET /metrics)
        Returns: a list of dicts of metric info.
        """
        return self._get('/metrics')

    def create_metric(self, name, suffix, description, default, display=True):
        """ Create a new metric (POST /metrics)
        Args:
          name (string): The name of the new metric.
          suffix (string): 'measurements in'.
          description (string): What the metric is measuring.
          default (int): The default val to use when point is added.
          display (Optional[bool]): whether to display chart on page. Defaults to True.
        Returns: A dictionary with the args used to create the metric.
        """
        params = {'name':name, 'suffix':suffix, 'description': description,
                  'default': default, 'display': display}
        return self._post('/metrics', params)

    def get_metric(self, metric_id):
        """ Return a single metric, without points (GET /metrics/:id)
        Args:
          metric_id: the id of the metric to get
        Returns: A dictionary with metric information.
        """
        url = '/metrics/' + str(metric_id)
        return self._get_unwrapped(url)

    def delete_metric(self, metric_id):
        """ Delete a metric (DELETE /metrics/:id)
        Args:
          metric_id (int): the id of the metric to delete.
        Returns: None
        """
        return self._delete('/metrics/' + str(metric_id))

    def update_metric_points(self, metric_id, metric_value, timestamp=None):
        """ Add a metric point to a given metric (POST /metrics/:id/points)
        Args:
          metric_id (int): the id of the metric to update.
          metric_value (int): value to plot on the metric graph.
          timestamp (Optional[string]): Unix timestamp of point. Defaults to current timestamp.
        Returns: None
        """
        pass

    def delete_metric_points(self, metric_id, point_id):
        """ Delete a metric point (DELETE /metrics/:id/points/:point_id)
        Args:
          metric_id (int): the id of the metric.
          point_id (int):  the id of the point to delete.
        Returns: None
        """
        return self._delete('/metrics/' + str(metric_id) + '/points/' + str(point_id))

# subscribers
    def get_subscribers(self):
        """ Get all subscribers (GET /subscribers)
        Returns: A list of subscriber dicts.
        """
        return self._get('/subscribers')

    def create_subscriber(self, email, verify=False):
        """ Create a new subscriber (POST /subscribers)
        Args:
          email (string): email of the subscriber
          verify (Optional[bool]): send a verification email? Defaults to False.
        Returns: Dict with verify_code, id and other info.
        """
        params = {'email':email, 'verify':verify}
        return self._post('/subscribers', params)

    def delete_subscriber(self, subscriber_id):
        """ Delete a subscriber (DELETE /subscribers/:id)
        Args:
          subscriber_id (int): id of the subscriber to delete.
        Returns: None
        """
        return self._delete('/subscribers/' + str(subscriber_id))


