"""
contains custom exceptions to handle specific errors
"""

import logging


LOG = logging.getLogger(__name__)

class IDNotFound(ValueError):
    """
    handles exceptions caused by ID not present in database
    """

    def __init__(self, id):
        """
        logs and invokes ValueError
        
        :param id: id query
        :type id: int
        """

        LOG.error("id (=%s) parameter not found in database", str(id))
        super(IDNotFound, self).__init__()
