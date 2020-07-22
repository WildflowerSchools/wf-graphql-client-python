import json
import logging
import re

logger = logging.getLogger(__name__)

class GraphQLJsonEncoder(json.JSONEncoder):

    def default(self, obj):
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


def json2gql(data):
    json_data = json.dumps(data)
    return re.sub(r'"(.*?)"(?=:)', r'\1', json_data)
