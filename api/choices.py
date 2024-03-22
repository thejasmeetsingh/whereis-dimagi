from enum import Enum


class Choices(Enum):
    """
    Base enum class
    """

    @classmethod
    def get_values(cls):
        """
        Retrieve value as 2D tuples
        """
        return tuple(x.value for x in cls)


class BadgeChoices(Choices):
    """
    Employee badge choices
    """

    # This badge represent an employee who pinged his/her location 10 or more than 10 times
    MLP = ("MPL", "Most Location Pinged")

    # This badge represent an employee who pinged his/her location 3  or more than 3 times
    LLP = ("LLP", "Least Location Pinged")

    # This badge represent an employee who pinged his/her location only 1 time
    PLT = ("PLT", "Platypus")
