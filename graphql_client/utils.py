from enum import Enum
import json
import logging
import re

logger = logging.getLogger(__name__)


class GraphQLJsonEncoder(json.JSONEncoder):

    def default(self, obj):
        if isinstance(obj, Enum):
            return obj.name
        if hasattr(obj, "graphql_json"):
            graphql_json = getattr(obj, "graphql_json")
            if callable(graphql_json):
                return graphql_json()
        return json.JSONEncoder.default(self, obj)


def graphql_json_dumps(object, indent='  '):
    return json.dumps(
        object,
        cls=GraphQLJsonEncoder,
        indent=indent
    )



class GraphQLEncoder(json.JSONEncoder):

    def default(self, obj):
        if isinstance(obj, Enum):
            return f"||{obj.name}||"
        if hasattr(obj, "graphql_json"):
            graphql_json = getattr(obj, "graphql_json")
            if callable(graphql_json):
                return graphql_json()
        return json.JSONEncoder.default(self, obj)

    def encode(self, obj):
        json_data = json.JSONEncoder.encode(self, obj)
        return re.sub(r'"(.*?)"(?=:)', r'\1', re.sub(r'"\|\|(.*?)\|\|"', r'\1', json_data))




def json2gql(data, indent=None):
    return json.dumps(
        data,
        cls=GraphQLEncoder,
        indent=indent
    )
