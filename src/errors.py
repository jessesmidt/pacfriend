"""

    A file for all the errors the program will raise and catch

"""


class PacManError(Exception):
    """
    The base error class all expected errors will inherit from
    """
    pass


class NonExistingPath(PacManError):
    """
    Raised wehn a path or file does ot exist
    """
    def __init__(self, add: str):
        msg: str = f"The filepath {add} does not exist"
        super().__init__(msg)


class InvalidJson(PacManError):
    """
    Raised when a file is not valid json
    """
    def __init__(self, add: str):
        msg: str = f"{add} is not a valid json and/or json file"
        super().__init__(msg)


class InvalidJsonValues(PacManError):
    """
    Raised when there is a formatting error within the json
    """
    def __init__(self, add: str):
        msg: str = f"Invalid json values.\n{add}"
        super().__init__(msg)
