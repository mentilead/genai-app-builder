from pynamodb.attributes import NumberAttribute, UnicodeAttribute
from pynamodb.models import Model

from genaiappbuilder import settings


class MentorSession(Model):
    class Meta:
        read_capacity_units = 1
        write_capacity_units = 1
        table_name = "MentorSession"
        host = settings.AWS_DYNAMODB_HOST
        region = settings.AWS_REGION

    user_id = NumberAttribute(hash_key=True)
    create_date = NumberAttribute(range_key=True)
    mentoring_data = UnicodeAttribute()


if not MentorSession.exists():
    MentorSession.create_table(wait=True)


class MentorSessionHistory(Model):
    class Meta:
        read_capacity_units = 1
        write_capacity_units = 1
        table_name = "MentorSessionHistory"
        host = settings.AWS_DYNAMODB_HOST
        region = settings.AWS_REGION

    mentor_session_id = UnicodeAttribute(hash_key=True)
    history_date = NumberAttribute(range_key=True)
    mentoring_data = UnicodeAttribute()


if not MentorSessionHistory.exists():
    MentorSessionHistory.create_table(wait=True)
