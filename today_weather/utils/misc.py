import logging


def log_reply(user, kwargs):
    text = kwargs.get('text', ' ').replace('\n', "") 
    logging.info(f"message to {user}: {text}")