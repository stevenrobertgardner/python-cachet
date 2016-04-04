"""
 API Wrapper for Cachet
    https://cachethq.io
 Makes an authenticated connection,  passes on API requests
 and makes the returned stuff be nice and pythony.
"""
import logging
import urllib
import json

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
        ### TODO - validate args, clean up URL
        self.logger = logging.getLogger(__name__)
        self.cachet_api_url = cachet_url + '/api/v1'
        self.api_token = api_token
        self.logger.info("Setting cachet server URL: %s, API Token: %s",
                         self.cachet_api_url, self.api_token)

    def _do_get(self, url, timeout=1):
        """ Prepare and make urllib GET request, process and translate json response.
        Args:
          url (string): the URL to get
        Returns: Result of get call as Pythonized JSON
        """
        headers = {'X-Cachet-Token' : self.api_token}
        try:
            request = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(request, timeout=timeout) as response:
                data = response.read().decode('utf-8')
                return json.loads(data)
        except urllib.error.HTTPError as e:
            print("HTTPError")
        except urllib.error.URLError as e:
            print("URLError")
        # handle json exceptions here
        return None

    def _get(self, endpoint):
        """ Broker the get request from a API call, handle paging
        Args:
          endpoint (string): the endpoint to get.
        Returns: A list containing the response(s), or None
        """
        results = []
        url = self.cachet_api_url + endpoint
        while True:
            response_json = self._do_get(url)
            data = response_json['data']
            if not isinstance(data, list):
                data = [data]
            results.extend(data)
            if not response_json.get('meta'):
                break
            url = response_json['meta']['pagination']['next_page']
            if not url:
                break
        return results

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

    def create_component(self, name, status, desc=None,
                         link=None, order=0, group_id=0, enabled=True):
        """ Create a new component (POST /components).
        Args:
          name (string): Name of the component.
          status (int): Status of the component; 1-4.
          description (Optional[string]): Description of the component.
          link (Optional[string]): A hyperlink to the component.
          order (Optional[int]): Order of the component. Defaults to 0.
          group_id (Optional[int]): The group_id the component is within. Defaults to 0.
          enabled (Optional[bool]): Whether the component is enabled. Defaults to True.
        Returns: A dictionary with component information.
        """
        pass

    def update_component(self, component_id, name=None, status=None,
                         desc=None, link=None, order=None, group_id=None, enabled=None):
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
        pass

    def delete_component(self, component_id):
        """ Delete a component (DELETE Components/:id).
        Args:
          component_id (int): ID of the component to delete.
        """
        pass

    def get_component_groups(self):
        """ Get all component groups which have been created, or None (GET /components/groups).
        Returns: A list of dicts with component group information.
        """
        return self._get('/components/groups')

    def get_component_group(self, group_id):
        """ GET /components/groups/:id
        Args:
          group_id (int): ID of the component group.
        Returns: A dict with component group information.
        """
        url = '/components/groups/' + str(group_id)
        return self._get_unwrapped(url)

    def create_component_group(self):
        """ POST /components/groups
        Args:
          name (str): Name of the component group.
          order (Optional[int]): Order of the component group.
          collapsed (Optional[int]): Collapse the group?
                 0=No,1=Yes,2=not_operational. Defaults to 0.
        Returns: Dict with group settings.
        """
        pass

    def update_component_group(self, group_id, name=None, order=None, collapsed=None):
        """ PUT /components/groups/:id
        Args:
          group_id (int): id of the component group.
          name (Optional[str]): Name of the component group.
          order (Optional[int]): Order of the group.
          collapsed (Optional[int]): Collapse the group?
                 0=No,1=Yes,2=not_operational. Defaults to 0.
        Returns: Dict with group settings.
        """
        pass

    def delete_component_group(self, group_id):
        """ DELETE /components/groups/:id
        Args:
          group_id (int): id of the component to delete.
        """
        pass

# incidents
    def get_incidents(self):
        """ Return all incidents (GET /incidents)
        Return: List of incident dicts
        """
        return self._get('/incidents')

    def get_incident(self, incident_id):
        """ Return a specific incident(GET /incidents/:id)
        Args:
          incident_id (int): ID of the incident to get.
        Return: Dict of incident information
        """
        url = '/incidents/' + str(incident_id)
        return self._get_unwrapped(url)

    def create_incident(self, name, message, status, visible=True,
                        component_id=None, component_status=None, notify=False):
        """ Create a new incident (POST /incidents)
        Args:
          name (str): Name of the incident.
          message (str): Markdown formatted message with explanations.
          status (int): Status of the incident.
          visible (Optional[bool]): Whether the incident is visible. Defaults to True
          component_id (Optional[int]): component to update (required with component_status)
          component_status (Optional[int]): The status to update the given component with.
          notify (bool): Whether to notify subscribers. Defaults to False.
        Return: Dict of incident information
        """
        pass

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
          notify (bool): Whether to notify subscribers. Defaults to False.
          incident_id (int): The ID of the incident to update.

        Return: Dict of incident information
        """
        pass

    def delete_incident(self, incident_id):
        """ Deletes an incident (DELETE /incidents/:id)
        Args:
          incident_id (int): The ID of the incident to delete.
        """
        pass


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
        pass

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
        """
        pass

    def update_metric_points(self, metric_id, metric_value, timestamp=None):
        """ Add a metric point to a given metric (POST /metrics/:id/points)
        Args:
          metric_id (int): the id of the metric to update.
          metric_value (int): value to plot on the metric graph.
          timestamp (Optional[string]): Unix timestamp of point. Defaults to current timestamp.
        """
        pass

    def delete_metric_points(self, metric_id, point_id):
        """ Delete a metric point (DELETE /metrics/:id/points/:point_id)
        Args:
          metric_id (int): the id of the metric.
          point_id (int):  the id of the point to delete.
        """
        pass

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
        pass

    def delete_subscriber(self, subscriber_id):
        """ Delete a subscriber (DELETE /subscribers/:id)
        Args:
          subscriber_id: id of the subscriber to delete.
        """
        pass

