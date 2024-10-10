# -*- coding: utf-8 -*-
from collective.z3cform.datagridfield import DataGridFieldFactory
from collective.z3cform.datagridfield.registry import DictRow
from imio.fpaudit import _
from imio.fpaudit import LOG_DIR
from imio.fpaudit.interfaces import ILogsStorage
from imio.fpaudit.logger import FPAuditLogInfo
from plone.app.registry.browser.controlpanel import ControlPanelFormWrapper
from plone.app.registry.browser.controlpanel import RegistryEditForm
from plone.autoform.directives import widget
from plone.registry.interfaces import IRecordModifiedEvent
from plone.z3cform import layout
from z3c.form.validator import NoInputData
from zope import schema
from zope.component import getUtility
from zope.interface import Interface
from zope.interface import Invalid
from zope.interface import invariant

import os


class ILogInfoSchema(Interface):
    log_id = schema.TextLine(
        title=_("Log id"),
        required=True,
    )

    audit_log = schema.TextLine(
        title=_("Audit file name"),
        description=_("Will be located in var/log"),
        required=True,
    )

    log_format = schema.TextLine(
        title=_("Log format"),
        default=u"%(asctime)s - %(message)s",
        required=True,
    )


class IFPAuditSettings(Interface):

    log_entries = schema.List(
        title=_(""),
        required=False,
        value_type=DictRow(title=_(u"Field"), schema=ILogInfoSchema, required=False),
    )
    widget(
        "log_entries",
        DataGridFieldFactory,
        display_table_css_class="listing",
        allow_reorder=False,
        auto_append=False,
    )

    @invariant
    def validate_settings(data):  # noqa
        # check ITableListSchema id uniqueness
        ids = []
        try:
            values = getattr(data, "log_entries") or []
        except NoInputData:
            return
        for entry in values:
            if entry["log_id"] in ids:
                raise Invalid(
                    _(
                        u"You cannot use same id multiple times '${id}'",
                        mapping={"id": entry["log_id"]},
                    )
                )
            ids.append(entry["log_id"])


class FPAuditSettings(RegistryEditForm):

    schema = IFPAuditSettings
    schema_prefix = "imio.fpaudit.settings"
    label = _("FP Audit Settings")


FPAuditSettingsView = layout.wrap_form(FPAuditSettings, ControlPanelFormWrapper)


def settings_changed(event):
    """Manage a record change"""
    if (
        IRecordModifiedEvent.providedBy(event)
        and event.record.interfaceName
        and event.record.interface != IFPAuditSettings
    ):
        return
    if event.record.fieldName == "log_entries":
        dic = {}
        for entry in event.record.value:
            log_i = FPAuditLogInfo(
                {"audit-log": os.path.join(LOG_DIR, entry["audit_log"])},
                entry["log_id"],
                logformat=entry["log_format"],
            )
            log_i.handler.formatter.datefmt = "%y-%m-%d %H:%M:%S"
            dic[entry["log_id"]] = log_i
        storage = getUtility(ILogsStorage)
        storage.set(dic)
