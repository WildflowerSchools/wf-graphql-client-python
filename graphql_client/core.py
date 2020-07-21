import graphql_client.utils
import json
import logging

logger = logging.getLogger(__name__)

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

    def request(
        self,
        client,
        http_request_timeout=10
    ):
        return client.execute(
            request_body_string = self.request_body_string(),
            request_variables_dict=self.request_variables_dict(),
            http_request_timeout=http_request_timeout
        )

    def request_body_string(
        self,
        indent_string='  '
    ):
        request_body_string = '{} '.format(self.operation_type)
        if self.operation_name is not None:
            request_body_string += self.operation_name
        if len(self.variables) > 0:
            request_body_string += '(\n{}\n)'.format(
                indent(',\n'.join([f'${variable.name}: {variable.type}' for variable in self.variables]), indent_string=indent_string)
            )
        if len(self.fields) > 0:
            request_body_string += '{{\n{}\n}}'.format(
                indent('\n'.join([field.request_body_string() for field in self.fields]), indent_string=indent_string)
            )
        return request_body_string

    def request_variables_dict(self):
        return {variable.name: variable.value for variable in self.variables}

    def request_variables_json(self):
        return graphql_client.utils.graphql_json_dumps(self.request_variables_dict())

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

    def request_body_string(
        self,
        indent_string='  '
    ):
        request_string = ''
        if self.alias is not None:
            request_string += f'{self.alias}: '
        request_string += self.name
        if len(self.parameters) > 0:
            request_string += '(\n{}\n)'.format(
                indent(',\n'.join([parameter.request_body_string() for parameter in self.parameters]), indent_string=indent_string)
            )
        if len(self.subfields) > 0:
            request_string += ' {{\n{}\n}}'.format(
                indent('\n'.join([subfield.request_body_string() for subfield in self.subfields]), indent_string=indent_string)
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

    def request_body_string(self):
        request_string = '{}: {}'.format(
            self.parameter_name,
            f'${self.variable_name}'
        )
        return request_string

def indent(
    multiline_string,
    indent_string='  '
):
    return '\n'.join(f'{indent_string}{line}' for line in multiline_string.splitlines())
