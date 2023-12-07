from fastiot.core import ReplySubject
from fastiot.msg import Thing

SAVE_MANY_RAW_DATA_SUBJECT_NAME = "save-many-raw-datapoints"


DB_SAVE_MANY_RAW_DATAPOINTS_SUBJECT = ReplySubject(name=SAVE_MANY_RAW_DATA_SUBJECT_NAME, msg_cls=Thing, reply_cls=Thing)

