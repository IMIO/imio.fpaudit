# -*- coding: utf-8 -*-
from collective.fingerpointing.config import AUDIT_MESSAGE
from collective.fingerpointing.utils import get_request_information
from file_read_backwards import FileReadBackwards
from imio.fpaudit.interfaces import ILogsStorage
from natsort import natsorted
from zope.component import getUtility

import logging
import os
import re


logger = logging.getLogger("imio.fpaudit")


def fplog(log_id, action, extras):
    """collective.fingerpointing add log message.

    :param log_id: The log id as defined in the configuration
    :param action: The action string
    :param extras: The extras"""
    user, ip = get_request_information()
    storage = getUtility(ILogsStorage)
    log_i = storage.get(log_id)
    if log_i:
        log_i(AUDIT_MESSAGE.format(user, ip, action, extras))
    else:
        logger.info(AUDIT_MESSAGE.format(user, ip, action, extras))


def get_all_lines_of(logfiles):
    """Get all lines of a list of log files.

    :param logfiles: The list of log files"""
    for logfile in logfiles:
        for line in get_lines_of(logfile):
            yield line


def get_lines_of(logfile, actions=()):
    """Generator for reversed log lines of a log file.

    :param logfile: The path to the log file
    :param actions: An action list to search_on"""
    acts = [" action={}".format(act) for act in actions]
    with FileReadBackwards(logfile, encoding="utf-8") as file:
        for line in file:
            s_line = line.strip("\n")
            if not actions or any(act in s_line for act in acts):
                yield s_line


def get_logrotate_filenames(directory, base_filename, suffix_regex=r"\.\d+$", full=True):
    """Get all logrotate files matching the base filename in the directory.

    :param directory: The directory where the logrotate files are stored
    :param base_filename: The base filename of the logrotate files
    :param suffix_regex: The regex pattern to match the suffix of the logrotate files
    :param full: If True, return the full path of the logrotate files
    """
    pattern = re.compile("^{}(?:{})*$".format(re.escape(base_filename), suffix_regex))
    res = natsorted([f for f in os.listdir(directory) if pattern.match(f)])
    if full:
        res = [os.path.join(directory, f) for f in res]
    return res
