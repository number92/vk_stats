from loguru import logger
from core.config import URL


class FloodControlException(Exception):
    pass


class BadTokenException(Exception):
    pass


class ResponseEmptyException(Exception):
    pass


def raise_err_by_code(err: dict):
    logger.error(err.get("error_msg"))
    code = err.get("error_code")
    err_msg = err.get("error_msg")
    if code == 5:
        print(f"link for update token:\n {URL}")
        raise BadTokenException(err_msg)

    elif code == 9:
        raise FloodControlException(err_msg)

    else:
        raise Exception(err_msg)
