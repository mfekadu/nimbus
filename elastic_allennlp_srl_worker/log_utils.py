import logging
import color_utils
import inspect

# flake8: noqa

# fmt: off
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
# create console handler and set level to debug
ch1 = logging.StreamHandler()
ch1.setLevel(logging.DEBUG)
ch2 = logging.StreamHandler()
ch2.setLevel(logging.INFO)
ch3 = logging.StreamHandler()
ch3.setLevel(logging.WARNING)
ch4 = logging.StreamHandler()
ch4.setLevel(logging.ERROR)
# create formatter
_a  = "%(asctime)s "
_b  = "[%(levelname)-5.5s]  "
_b2 = f"{color_utils.info(_b)}"
_b3 = f"{color_utils.warning(_b)}"
_b4 = f"{color_utils.error(_b)}"
_c  = " %(CALLER)20s()  "
_cc = f"{color_utils.success(_c)}"
_d  = "%(message)s"
_d1 = f"{color_utils.bold(_d)}"
_fmt1 = f"{_a} " + f"{_b}"  + f"{_cc}" + f"{_d1}"
_fmt2 = f"{_a} " + f"{_b2}" + f"{_cc}" + f"{_d}"
_fmt3 = f"{_a} " + f"{_b3}" + f"{_cc}" + f"{_d}"
_fmt4 = f"{_a} " + f"{_b4}" + f"{_cc}" + f"{_d}"
formatter1 = logging.Formatter(_fmt1)
formatter2 = logging.Formatter(_fmt2)
formatter3 = logging.Formatter(_fmt3)
formatter4 = logging.Formatter(_fmt4)
# add formatter to ch
ch1.setFormatter(formatter1)
ch2.setFormatter(formatter2)
ch3.setFormatter(formatter3)
ch4.setFormatter(formatter4)
# add ch to logger
logger.addHandler(ch1)
logger.addHandler(ch2)
logger.addHandler(ch3)
logger.addHandler(ch4)
# fmt: on


def log(extra_msg="", info=False):
    logLevelFunc = logger.info if info else logger.debug  # default debug
    logLevelFunc(
        "-" * 10 + "\n" + extra_msg + "\n",
        extra={
            # https://stackoverflow.com/a/44164714/5411712
            "CALLER": inspect.stack()[1].function
        },
    )
