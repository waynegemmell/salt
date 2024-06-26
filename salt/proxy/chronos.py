"""
Chronos
========

Proxy minion for managing a Chronos cluster.

Dependencies
------------

- :mod:`chronos execution module (salt.modules.chronos) <salt.modules.chronos>`

Pillar
------

The chronos proxy configuration requires a 'base_url' property that points to
the chronos endpoint:

.. code-block:: yaml

    proxy:
      proxytype: chronos
      base_url: http://my-chronos-master.mydomain.com:4400

.. versionadded:: 2015.8.2
"""

import logging

import salt.utils.http

__proxyenabled__ = ["chronos"]
CONFIG = {}
CONFIG_BASE_URL = "base_url"
log = logging.getLogger(__file__)


def __virtual__():
    return True


def init(opts):
    """
    Perform any needed setup.
    """
    if CONFIG_BASE_URL in opts["proxy"]:
        CONFIG[CONFIG_BASE_URL] = opts["proxy"][CONFIG_BASE_URL]
    else:
        log.error("missing proxy property %s", CONFIG_BASE_URL)
    log.debug("CONFIG: %s", CONFIG)


def ping():
    """
    Is the chronos api responding?
    """
    try:
        response = salt.utils.http.query(
            f"{CONFIG[CONFIG_BASE_URL]}/scheduler/jobs",
            decode_type="json",
            decode=True,
        )
        log.debug(
            "chronos.info returned successfully: %s",
            response,
        )
        if "dict" in response:
            return True
    except Exception as ex:  # pylint: disable=broad-except
        log.error(
            "error pinging chronos with base_url %s: %s",
            CONFIG[CONFIG_BASE_URL],
            ex,
        )
    return False


def shutdown(opts):
    """
    For this proxy shutdown is a no-op
    """
    log.debug("chronos proxy shutdown() called...")
