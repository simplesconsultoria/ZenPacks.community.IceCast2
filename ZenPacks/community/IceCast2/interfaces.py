# -*- coding:utf-8 -*-
from Products.Zuul.interfaces import IRRDDataSourceInfo
from Products.Zuul.form import schema
from Products.Zuul.utils import ZuulMessageFactory as _t


class IIceCastDataSourceInfo(IRRDDataSourceInfo):
    timeout = schema.Int(title=_t(u'Timeout (seconds)'))
    cycletime = schema.Int(title=_t(u'Cycle Time (seconds)'))
    hostname = schema.Text(title=_t(u'Host Name'),
                           group=_t('IceCast Monitor'))
    port = schema.Int(title=_t(u'Port'),
                      group=_t('IceCast Monitor'))
    ipAddress = schema.Text(title=_t(u'Ip Address'),
                            group=_t('IceCast Monitor'))
    url = schema.Text(title=_t(u'URL'),
                      group=_t('IceCast Monitor'))
    useSsl = schema.Bool(title=_t(u'Use SSL?'),
                         group=_t('IceCast Monitor'))
    basicAuthUser = schema.Text(title=_t(u'Basic Auth User'),
                                group=_t('IceCast Monitor'))
    basicAuthPass = schema.Password(title=_t(u'Basic Auth Password'),
                                    group=_t('IceCast Monitor'))


class IIceCastMountDataSourceInfo(IIceCastDataSourceInfo):
    mount = schema.Text(title=_t(u'Mount'),
                      group=_t('IceCast Monitor'))
