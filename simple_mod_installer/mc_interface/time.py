"""
For converting time to and from Minecraft Format
"""
import datetime as dt


def to_mc_time(datetime):
    """
    To Minecraft-style timestamp
    :param datetime: datetime object
    :return: string
    """
    return dt.datetime.strftime(datetime, "%Y-%m-%dT%H:%M:%S%fZ")


def from_mc_time(datetime):
    """
    From Minecraft-style timestamp
    :param datetime: string
    :return: datetime object
    """
    return dt.datetime.strptime(datetime, "%Y-%m-%dT%H:%M:%S%fZ")
