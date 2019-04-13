from datetime import datetime

import ujson
from marshmallow import validates_schema, post_load, pre_load

from actor_libs.database.orm import db
from actor_libs.errors import DataNotFound
from actor_libs.schemas import BaseSchema
from actor_libs.schemas.fields import EmqString, EmqInteger
from app.models import BusinessRule, Client


__all__ = ['CurrentAlertSchema', 'HistoryAlertSchema']


class CurrentAlertSchema(BaseSchema):
    class Meta:
        additional = (
            'alertName', 'alertContent', 'alertDetail', 'alertSeverity', 'startTime'
        )

    tenantID = EmqString(required=True)
    deviceID = EmqString(required=True)
    ruleIntID = EmqInteger(required=True)
    alertTimes = EmqInteger(missing=1)

    @validates_schema
    def validate_data(self, in_data):
        tenant_uid = in_data.get('tenantID')
        rule = db.session.query(BusinessRule.id) \
            .filter(BusinessRule.id == in_data.get('ruleIntID'),
                    BusinessRule.tenantID == tenant_uid) \
            .first()
        if not rule:
            raise DataNotFound(field='ruleIntID')
        device = db.session.query(Client.id) \
            .filter(Client.tenantID == tenant_uid,
                    Client.deviceID == in_data.get('deviceID')) \
            .first()
        if not device:
            raise DataNotFound(field='deviceID')

    @pre_load
    def handle_data(self, data):
        action = data.get('action')
        payload = data.get('value')
        payload_dict = ujson.loads(payload)
        in_data = {**action, 'alertDetail': payload_dict, "startTime": datetime.now()}
        return in_data

    @post_load
    def add_tenant_info(self, data):
        return data


class HistoryAlertSchema(BaseSchema):
    class Meta:
        additional = (
            'deviceID', 'alertName', 'alertContent', 'alertTimes',
            'alertDetail', 'alertSeverity', 'startTime', 'endTime'
        )
