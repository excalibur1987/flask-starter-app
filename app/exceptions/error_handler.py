class ErrorHandler(Exception):
    trace: str
    logger: str
    level: str
    msg: str

    def __init__(self, e: Exception, logger=None, level=None, msg=None) -> None:
        from app.helpers import get_traceback

        self.trace = get_traceback(e)
        self.logger = logger
        self.level = level
        self.msg = msg
