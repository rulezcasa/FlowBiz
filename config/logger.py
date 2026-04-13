import logging

logging.basicConfig(
    level=logging.INFO,  # change to DEBUG during development
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    filename="app.log",
    filemode="a"
)



