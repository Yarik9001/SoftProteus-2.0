import logging
import coloredlogs

# Creating logger
mylogs = logging.getLogger(__name__)
mylogs.setLevel(logging.DEBUG)

# Handler - 1
file = logging.FileHandler("Sample.log")
fileformat = logging.Formatter("%(asctime)s:%(levelname)s:%(message)s")
file.setLevel(logging.DEBUG)
file.setFormatter(fileformat)

# Handler - 3
stream = logging.StreamHandler()
streamformat = logging.Formatter("%(levelname)s:%(module)s:%(message)s")
stream.setLevel(logging.DEBUG)
stream.setFormatter(streamformat)


# Adding all handlers to the logs
mylogs.addHandler(file)
mylogs.addHandler(stream)
coloredlogs.install(level=logging.DEBUG, logger=mylogs,
                    fmt='%(asctime)s [%(levelname)s] - %(message)s')

# Some demo codes
mylogs.debug("debug")
mylogs.info("info")
mylogs.warning("warn")
mylogs.critical("critical")
mylogs.error("error")
