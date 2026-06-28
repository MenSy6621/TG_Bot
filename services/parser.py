import re


ONE_TIME_PATTERN = r"(.+?) в (\d{2}:\d{2})"

PERIODIC_PATTERN = (
    r"(.+?) "
    r"(каждый день|через день|каждую неделю|каждый месяц)"
    r" в (\d{2}:\d{2})"
)

UNTIL_WITH_START_PATTERN = (
    r"(.+?) "
    r"с (\d{2}:\d{2}) "
    r"до (\d{2}:\d{2}) "
    r"каждые (\d+)"
)

UNTIL_PATTERN = (
    r"(.+?) "
    r"до (\d{2}:\d{2}) "
    r"каждые (\d+)"
)

def parse_one_time(text):
    match = re.match(ONE_TIME_PATTERN, text)

    if not match:
        return None

    return {
        "type": "one_time",
        "task": match.group(1),
        "time": match.group(2)
    }


def parse_periodic(text):
    match = re.match(PERIODIC_PATTERN, text)

    if not match:
        return None

    return {
        "type": "periodic",
        "task": match.group(1),
        "period": match.group(2),
        "time": match.group(3)
    }


def parse_until(text):

    # ======================================
    # WITH START
    # ======================================

    match = re.match(
        UNTIL_WITH_START_PATTERN,
        text
    )

    if match:

        return {
            "type": "until",
            "task": match.group(1),
            "start_time": match.group(2),
            "end_time": match.group(3),
            "interval": int(match.group(4))
        }

    # ======================================
    # WITHOUT START
    # ======================================

    match = re.match(
        UNTIL_PATTERN,
        text
    )

    if match:

        return {
            "type": "until",
            "task": match.group(1),
            "start_time": None,
            "end_time": match.group(2),
            "interval": int(match.group(3))
        }

    return None

def parse_reminder(text):

    result = parse_until(text)

    if result:
        return result

    result = parse_periodic(text)

    if result:
        return result

    result = parse_one_time(text)

    if result:
        return result

    return None
