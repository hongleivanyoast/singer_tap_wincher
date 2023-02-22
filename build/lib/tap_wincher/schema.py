"""Schema loading."""
# -*- coding: utf-8 -*-

import json
import os

from singer.schema import Schema

def get_abs_path(path:str) -> str:
    """Help function to get the absolute path.
    Arguments:
        path {str} -- Path to directory

    Returns:
        str -- The absolute path
    """
    return os.path.join(os.path.dirname(os.path.realpath(__file__)), path)


def load_schemas() -> dict:
    """ Load schemas from schemas folder.
    
    Returns: dict -- schemas
     """
    schemas: dict = {}
    for filename in os.listdir(get_abs_path('schemas')):
        path = get_abs_path('schemas') + '/' + filename
        file_raw = filename.replace('.json', '')
        with open(path) as file:
            schemas[file_raw] = Schema.from_dict(json.load(file))
    return schemas
