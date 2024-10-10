# -*- coding: utf-8 -*-
from collective.fingerpointing.config import AUDIT_MESSAGE
from collective.fingerpointing.utils import get_request_information
from imio.fpaudit.interfaces import ILogsStorage
from zope.component import getUtility

import logging


logger = logging.getLogger("imio.fpaudit")


def fplog(log_id, action, extras):
    """collective.fingerpointing add log message."""
    user, ip = get_request_information()
    storage = getUtility(ILogsStorage)
    log_i = storage.get(log_id)
    if log_i:
        log_i(AUDIT_MESSAGE.format(user, ip, action, extras))
    else:
        logger.info(AUDIT_MESSAGE.format(user, ip, action, extras))
