import datetime
import logging
import time
import dateutil

logger = logging.getLogger("RateManager")


class RateManager:
    """
    Class to handle rate limiting. Chose class for easier and central management.
    """
    AISLER_API_RATE_LIMIT = 1000
    CURRENT_QUERIES = 0
    DIGIKEY_RESET_TIME = datetime.time(
        0,
        tzinfo=dateutil.tz.gettz("US/Central")
    )
    FORCE_LIMIT_REACHED = False
    screen_update_hook = None

    def is_limit_reached(self):
        """
        Defines when the limit is reached.
        :return: True if limit is reached, False otherwise
        """
        return (self.CURRENT_QUERIES >= self.AISLER_API_RATE_LIMIT) or self.FORCE_LIMIT_REACHED

    def update_next_reset_time(self, latest_reset=None):
        """
        Updates the time, when the next reset is to be expected.

        :param latest_reset: (optional) can be the last reset time
        :return: returns the next expected reset time
        """
        if latest_reset is None:
            # Get current UTC time as base.
            latest_reset = datetime.datetime.now(tz=dateutil.tz.tzutc())

        # Check whether the reset is today or tomorrow
        if latest_reset.time() >= self.DIGIKEY_RESET_TIME:
            # Reset is tomorrow hence add one day
            latest_reset += datetime.timedelta(days=1)

        # Set the time Accordingly
        latest_reset = latest_reset.replace(
            hour=self.DIGIKEY_RESET_TIME.hour,
            minute=self.DIGIKEY_RESET_TIME.minute,
            second=self.DIGIKEY_RESET_TIME.second,
            microsecond=0,
            tzinfo=self.DIGIKEY_RESET_TIME.tzinfo
        )

        return latest_reset

    # Initially update time once
    def __init__(self):
        self.NEXT_RESET = self.update_next_reset_time()

    @staticmethod
    def wait_until(until):
        """
        Waits (sleeps) until a given time.

        :param until: Datetime to sleep until
        :return: Nothing
        """
        now = datetime.datetime.utcnow()
        now = now.replace(tzinfo=dateutil.tz.tzutc())
        while now <= until:
            logger.info(f"Sleeping due to rate limit. {now} -> {until}")
            time.sleep(60)
            now = datetime.datetime.utcnow()
            now = now.replace(tzinfo=dateutil.tz.tzutc())

    def check_and_wait(self, screen_update_hook=None):
        """
        Checks if we surpassed the rate limit and waits accordingly, if so.

        :return: Nothing
        """
        if self.is_limit_reached():
            if screen_update_hook is not None:
                screen_update_hook(f"Rate limit reached. Waiting until {self.NEXT_RESET.isoformat()}")
            self.wait_until(self.NEXT_RESET)
            self.reset()

    def update(self):
        """
        Update the number of queries. (Add one)

        :return: Nothing
        """
        self.CURRENT_QUERIES += 1

    def reset(self):
        """
        Resets the rate limit counter to 0 and calculates next reset date.

        :return: Nothing
        """
        self.CURRENT_QUERIES = 0
        self.NEXT_RESET = self.update_next_reset_time(self.NEXT_RESET)
        self.FORCE_LIMIT_REACHED = False

    def force_ratelimit_reached(self):
        """
        Forces the ratelimit to be triggered. E.g. if we find out that the limit is reached by the API response.

        :return: nothing
        """
        self.force_ratelimit_reached()
