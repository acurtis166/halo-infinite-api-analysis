"""Contains classes representing custom errors that occur in the application."""


from requests import Response


class ApiRequestError(Exception):
    """Exception raised when an API request fails."""
    
    def __init__(self, resp:Response, data:dict=None):
        """Exception raised when an API request fails. Construct an ApiRequestError from the Response object that resulted from the failed request.

        Args:
            resp (Response): the Response object from the request that failed.
            data (dict): Any data that accompanied the request. Defaults to None.
        """        
        
        self.status_code = resp.status_code
        self.message = f'Request to the HaloAPI failed.\n\tURL: {resp.url}\n\tData: {data}\n\tReason: {resp.status_code} - {resp.reason}\n\tBody: {resp.text}'
        super().__init__(self.message)


class ParsingError(Exception):
    """Exception raised when API data is unsuccessfully retrieved from an object."""

    def __init__(self, obj_name:str, obj:object):
        """Exception raised when API data is unsuccessfully retrieved from an object. Construct a ParsingError.

        Args:
            obj_name (str): Description of the data being retrieved.
            obj (object): The object that caused the ParsingError.
        """

        self.message = f'Error occurred when parsing {obj_name}. Raw data: {obj}'
        super().__init__(self.message)

        