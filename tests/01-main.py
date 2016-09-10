#!/usr/bin/python3
import amulet
import requests
import unittest
#from .lib import helper

class TestMain(unittest.TestCase):
    """
    Deployment test for the Pentaho Data Integration charm.

    """
    @classmethod
    def setUpClass(cls):
        cls.d = amulet.Deployment(series='trusty')
        #d.add('tomcat', 'cs:trusty/tomcat-1', placement='lxc:0')
        cls.d.add('tomcat', 'cs:trusty/tomcat-1')
        cls.d.add('saiku','cs:~spicule/trusty/saikuanalytics-enterprise')
        cls.d.relate('saiku:website', 'tomcat:website')
        cls.d.expose('tomcat')
        try:
            # Create the deployment desc2ribed above, give us 900 seconds to do it
            cls.d.setup(timeout=900)
            # Setup will only make sure the services are deployed, related, and in a
            # "started" state. We can employ the sentries to actually make sure there
            # are no more hooks being executed on any of the nodes.
            cls.d.sentry.wait()
        except amulet.helpers.TimeoutError:
            cls.amulet.raise_status(amulet.SKIP, msg="Environment wasn't stood up in time")
        except:
              # Something else has gone wrong, raise the error so we can see it and this
              # will automatically "FAIL" the test.
              raise
            # Shorten the names a little to make working with unit data easier
        cls.saiku_unit = cls.d.sentry['saiku'][0]
        cls.tomcat_unit = cls.d.sentry['tomcat'][0]


    def test_webserver_responsive(self):
        home_page = requests.get('http://%s:8080/' % self.tomcat_unit.info['public-address'])
        #home_page = requests.get('http://repo.meteorite.bi:8098/')
        home_page.raise_for_status() # Make sure it's not 5XX error


    def test_webapp_returning_data(self):
        info_endpoint = requests.get('http://%s:8080/saiku/rest/saiku/info' % self.tomcat_unit.info['public-address'])
        info_endpoint.raise_for_status()




if __name__ == '__main__':
    unittest.main()
