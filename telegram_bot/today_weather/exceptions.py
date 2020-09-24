import logging


class CustomError(Exception):
    """
    Base class for all foreseen exceptions.
    """


class BackendError(CustomError):
    def __init__(self, error):
        self.error = error


def custom_exception_handler(update, context):
    if isinstance(context.error, CustomError):
        logging.error(f"{context.error.__class__.__name__}: {context.error.error}")
    else:
        raise context.error
