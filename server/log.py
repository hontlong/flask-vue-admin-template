# log
# doc https://cuiqingcai.com/6080.html
import logging
import os
import sys
from logging import handlers

__all__ = [
    "log"
]

os.makedirs("./logs", mode=0o755, exist_ok=True)

_format = r'%(asctime)s - %(filename)s[%(lineno)d] - %(levelname)s: %(message)s'

_formatter = logging.Formatter(_format)
_time_h = handlers.TimedRotatingFileHandler(
    encoding="utf-8",
    filename='./logs/app.log',
    when='D',
    interval=1,
    backupCount=10
)
_time_h.setFormatter(_formatter)
_time_h.suffix = '%y-%m-%d.log'

_std_h = logging.StreamHandler(stream=sys.stdout)
_std_h.setFormatter(_formatter)

log = logging.root
# log = logging.getLogger()
# log = logging.getLogger("APP")
log.setLevel(logging.DEBUG)

log.addHandler(_time_h)
log.addHandler(_std_h)
