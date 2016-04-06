#!/usr/bin/env python3

# expedient and bad functional test, using local docker cachet.
# Expects an initialized database, manual setup completed, and key updated.
# Note to self - commit a docker container in this state for testing
# and add code to check/spin up container.

import unittest
import time
import cachet

CACHET_SERVER = 'http://192.168.99.100:80'
API_KEY       = 'vJvJtdfvPZjtoGuwfyfF'

#conn = cachet.Connection(CACHET_SERVER,API_KEY)

#health  = conn.health()    # Assert this is true
#version = conn.version()  # Assert this is correct


class FunctionalTestCase(unittest.TestCase):

    def setUp(self):
        self.conn = cachet.Connection(CACHET_SERVER,API_KEY)

    def get_max_id(self, dictlist):
        max_id = 0
        for thing in dictlist:
            max_id = max(thing['id'], max_id)
        return max_id

    def test_health(self):
        self.assertEqual(self.conn.health(), True)

    def test_version(self):
        self.assertEqual(self.conn.version(), None)

    def test_component_crud(self):
        all_components = self.conn.get_components()
        start_id = self.get_max_id(all_components)
        component_1 = self.conn.create_component(name="foo",desc="foo engine",status=1)
        component_2 = self.conn.create_component(name="bar",desc="bar machine",status=1)
        component_3 = self.conn.create_component(name="baz",desc="bazzifier",status=1)
        second_component = self.conn.get_component(start_id + 2)
        time.sleep(2)
        second_component_name = None
        if second_component:
            second_component_name = second_component.get('name')
        self.assertEqual(second_component_name,'bar')
        delete_response = self.conn.delete_component(start_id + 2)
        second_component_after_delete = self.conn.get_component(start_id + 2)
        self.assertEqual(second_component_after_delete,None)

        # TODO - check the returned dictionary from one of these

    def test_incident_crud(self):
        all_incidents = self.conn.get_incidents()
        start_id = self.get_max_id(all_incidents)
        incident_1 = self.conn.create_incident('World Disaster','Armageddon!!',1)
        self.assertEqual('World Disaster', (self.conn.get_incident(start_id + 1))['name'])
        


    def test_subscriber_crud(self):
        start_id = self.get_max_id(self.conn.get_subscribers())
        # create subscriber sans verify
        subscriber_1 = self.conn.create_subscriber(email="testing1@bar.com",verify=False)
        subscriber_2 = self.conn.create_subscriber(email="testing2@bar.com",verify=False)
        subscribers = self.conn.get_subscribers()
        subscriber_emails = [d['email'] for d in self.conn.get_subscribers()]
        subscriber_ids = { d['email']: d['id'] for d in self.conn.get_subscribers() }
        # Delete testing1, ensure testing1 deleted and testing2 present
        self.conn.delete_subscriber(subscriber_ids['testing1@bar.com'])
        subscriber_emails = [d['email'] for d in self.conn.get_subscribers()]
        self.assertEqual( 'testing1@bar.com' in subscriber_emails, False) 
        self.assertEqual( 'testing2@bar.com' in subscriber_emails, True) 
        # Delete testing2, ensure both deleted
        self.conn.delete_subscriber(subscriber_ids['testing2@bar.com'])
        subscriber_emails = [d['email'] for d in self.conn.get_subscribers()]
        self.assertEqual( 'testing1@bar.com' in subscriber_emails, False) 
        self.assertEqual( 'testing2@bar.com' in subscriber_emails, False) 




# test component groups:
#all_component_groups = conn.get_component_groups()
#component_group_2 = conn.get_component_group(2)

# test incidents:
#all_incidents = conn.get_incidents()
#incident_2 = conn.get_incident(1)


# test metrics
#all_metrics = conn.get_metrics()
#one_metric = conn.get_metric(1)
#all_subscribers = conn.get_subscribers()



#delete_subscriber_response = conn.delete_subscriber(2)
# assert the response is null
# assert the subscriber is deleted



