import logging


logger = logging.getLogger("buildcenter")


def setup_logger(level: str):
    level = logging.WARN if level is None else level
    logger.setLevel(level)
    ch = logging.StreamHandler()
    ch.setLevel(level)
    logger.addHandler(ch)


def run_app(args):
    setup_logger(args.log)
    args.func(**vars(args))
