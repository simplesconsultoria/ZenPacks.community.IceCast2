#!/usr/bin/env python
# -*- coding:utf-8 -*-
import sys
import urllib2
from xml.dom import minidom

from optparse import OptionParser


ICESTATS = ['client_connections',
            'clients',
            'connections',
            'file_connections',
            'listener_connections',
            'listeners',
            'source_client_connections',
            'source_relay_connections',
            'source_total_connections',
            'sources',
            'stats',
            'stats_connections']

MOUNTSTATS = ['listeners',
              'slow_listners',
              'total_bytes_read',
              'total_bytes_sent',
              'listener_peak']


class ZenossIceCastPlugin(object):

    elements = ICESTATS

    def __init__(self, hostname, port, ipAddress, url, useSsl, authentication):
        self.hostname = hostname
        self.port = str(port) or '80'
        self.ipAddress = ipAddress
        self.url = url
        self.useSsl = useSsl
        self.protocol = useSsl and 'https' or 'http'
        self.authentication = authentication

    def process_response(self, data=None):
        ''' Process Response from IceCast Stats XML
            and return a Dictionary
        '''
        if not data:
            return None
        if not hasattr(data, 'getElementsByTagName'):
            dom = minidom.parse(data)
        else:
            # We already have an element
            dom = data
        result = {}
        for element in self.elements:
            node = dom.getElementsByTagName(element)
            if not node:
                continue
            result[element] = int(node[0].firstChild.data)
        return result

    def formatNagios(self, response):
        """OK|foo=0.814667;;;0.000000 bar=30737B;;;0"""
        base = 'OK |'
        for key, value in response.items():
            tmpStr = '%s=%s;;;0 ' % (str(key), str(value))
            base += tmpStr
        return base

    def run(self):
        headers = [('User-agent', 'Zenoss')]
        if self.hostname and self.ipAddress:
            headers.append(('Host', self.hostname))
            address = '%s://%s:%s%s' % (self.protocol,
                                        self.ipAddress,
                                        self.port,
                                        self.url)
        else:
            address = '%s://%s:%s%s' % (self.protocol,
                                        self.hostname,
                                        self.port,
                                        self.url)
        if self.authentication:
            username, passwd = self.authentication.split(':')
            passman = urllib2.HTTPPasswordMgrWithDefaultRealm()
            passman.add_password(None, address, username, passwd)
            authhandler = urllib2.HTTPBasicAuthHandler(passman)
            opener = urllib2.build_opener(authhandler)
        else:
            opener = urllib2.build_opener()

        opener.addheaders = headers
        f = opener.open(address)
        response = self.process_response(f)
        response = self.formatNagios(response)
        return response


class ZenossIceCastMountPlugin(ZenossIceCastPlugin):

    elements = MOUNTSTATS

    def __init__(self, hostname, port, ipAddress, url, useSsl,
                 authentication, mount):
        super(ZenossIceCastMountPlugin, self).__init__(hostname, port,
                                                       ipAddress, url,
                                                       useSsl,
                                                       authentication)
        self.mount = mount

    def process_response(self, data=None):
        ''' Process Response from IceCast Stats XML
            find right source
            and return a Dictionary
        '''
        if not data:
            return None
        dom = minidom.parse(data)
        mount = self.mount
        sources = dom.getElementsByTagName('source')
        for source in sources:
            source_mount = source.getAttribute('mount')
            if source_mount == mount:
                return super(ZenossIceCastMountPlugin,
                             self).process_response(source)


if __name__ == "__main__":
    parser = OptionParser()
    parser.add_option('-H', '--hostname', dest='hostname',
                 help='Hostname of IceCast server')
    parser.add_option('-p', '--port', dest='port', default=80, type='int',
                 help='Port of http server')
    parser.add_option('-I', '--ipAddress', dest='ipAddress',
                 help='IP Address http server')
    parser.add_option('-U', '--url', dest='url', default='/admin/stats.xml',
                 help='Path to IceCast2 Stats')
    parser.add_option('-s', '--useSsl', dest='useSsl', default=False,
                 help='Use SSL?')
    parser.add_option('-t', '--timeout', dest='timeout',
                 help='Timeout')
    parser.add_option('-m', '--mount', dest='mount',
                 help='Mount Point')
    parser.add_option('-a', '--authentication', dest='authentication',
                 help='Authentication')
    options, args = parser.parse_args()

    if not options.hostname:
        print "You must specify the hostname parameter."
        sys.exit(1)

    if not options.mount:
        cmd = ZenossIceCastPlugin(options.hostname, options.port,
                                  options.ipAddress, options.url,
                                  options.useSsl, options.authentication)
    else:
        cmd = ZenossIceCastMountPlugin(options.hostname, options.port,
                                        options.ipAddress, options.url,
                                        options.useSsl, options.authentication,
                                        options.mount)

    try:
        result = cmd.run()
    except urllib2.HTTPError:
        print 'HTTP Error'
        sys.exit(1)

    if result:
        print result
        sys.exit(0)
    else:
        sys.exit(1)
