import json
import logging

logger = logging.getLogger(__name__)

INDENT_STRING = '  '

class GraphQLJsonEncoder(json.JSONEncoder):

    def default(self, obj):
        if isinstance(obj, bytes):
            return obj.decode("utf8")
        # if isinstance(obj, datetime):
        #     return obj.strftime(ISO_FORMAT)
        # if isinstance(obj, date):
        #     return obj.strftime(DATE_FORMAT)
        # if hasattr(obj, "to_dict"):
        #     to_json = getattr(obj, "to_dict")
        #     if callable(to_json):
        #         return to_json()
        # if hasattr(obj, "value"):
        #     return obj.value
        return json.JSONEncoder.default(self, obj)

class Operation:

    def __init__(
        self,
        operation_type=None,
        operation_name=None,
        variables=None,
        fields=None
    ):
        if operation_type is None:
            raise ValueError('Must specify operation_type for Operation object: query or mutation')
        if operation_name is None and variables is not None:
            operation_name = 'UnnamedOperation'
        if fields is None:
            fields = list()
        if variables is None:
            variables = list()
        self.operation_type=operation_type
        self.operation_name=operation_name
        self.variables=variables
        self.fields=fields

    def set_variables(self, variables):
        self.variables = variables
        return self

    def add_variable(self, variable):
        self.variables.append(variable)
        return self

    def add_variables(self, variables):
        self.variables.extend(variables)
        return self

    def set_fields(self, fields):
        self.fields = fields
        return self

    def add_field(self, field):
        self.fields.append(field)
        return self

    def add_fields(self, fields):
        self.fields.extend(fields)
        return self

    def request_body(self):
        request_body_string = '{} '.format(self.operation_type)
        if self.operation_name is not None:
            request_body_string += self.operation_name
        if len(self.variables) > 0:
            request_body_string += '(\n{}\n)'.format(
                indent(',\n'.join([f'${variable.name}: {variable.type}' for variable in self.variables]))
            )
        if len(self.fields) > 0:
            request_body_string += '{{\n{}\n}}'.format(
                indent('\n'.join([field.graphql_request_string() for field in self.fields]))
            )
        return request_body_string

    def request_variables(self):
        variables_dict = {variable.name: variable.value for variable in self.variables}
        variables_json = json.dumps(
            variables_dict,
            cls=GraphQLJsonEncoder,
            indent=INDENT_STRING
        )
        return variables_json

class Variable:

    def __init__(
        self,
        name,
        type,
        value
    ):
        self.name = name
        self.type = type
        self.value = value

class Field:

    def __init__(
        self,
        name,
        subfields=None,
        parameters=None,
        alias=None
    ):
        if parameters is None:
            parameters = list()
        if subfields is None:
            subfields = list()
        self.name = name
        self.subfields=subfields
        self.parameters=parameters
        self.alias=alias

    def set_parameters(self, parameters):
        self.parameters = parameters
        return self

    def add_parameter(self, parameter):
        self.parameters.append(parameter)
        return self

    def add_parameters(self, parameters):
        self.parameters.extend(parameters)
        return self

    def set_subfields(self, subfields):
        self.subfields = subfields
        return self

    def add_subfield(self, subfield):
        self.subfields.append(subfield)
        return self

    def add_subfields(self, subfields):
        self.subfields.extend(subfields)
        return self

    def graphql_request_string(self):
        request_string = self.name
        if len(self.parameters) > 0:
            request_string += '(\n{}\n)'.format(
                indent(',\n'.join([parameter.graphql_request_string() for parameter in self.parameters]))
            )
        if len(self.subfields) > 0:
            request_string += ' {{\n{}\n}}'.format(
                indent('\n'.join([subfield.graphql_request_string() for subfield in self.subfields]))
            )
        return request_string

class Parameter:

    def __init__(
        self,
        parameter_name,
        variable_name
    ):
        self.parameter_name = parameter_name
        self.variable_name= variable_name

    def graphql_request_string(self):
        request_string = '{}: {}'.format(
            self.parameter_name,
            f'${self.variable_name}'
        )
        return request_string

def indent(multiline_string):
    return '\n'.join(f'{INDENT_STRING}{line}' for line in multiline_string.splitlines())
