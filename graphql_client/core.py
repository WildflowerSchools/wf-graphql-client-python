import logging

logger = logging.getLogger(__name__)

INDENT_STRING = '  '

class Field:

    def __init__(
        self,
        name,
        parameters=None,
        subfields=None
    ):
        if parameters is None:
            parameters = list()
        if subfields is None:
            subfields = list()
        self.name = name
        self.parameters=parameters
        self.subfields=subfields

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

    def __repr__(self):
        repr_string = self.name
        if len(self.parameters) > 0:
            repr_string += '(\n{}\n)'.format(
                indent(',\n'.join([repr(parameter) for parameter in self.parameters]))
            )
        if len(self.subfields) > 0:
            repr_string += ' {{\n{}\n}}'.format(
                indent('\n'.join([repr(subfield) for subfield in self.subfields]))
            )
        return repr_string

class Parameter:

    def __init__(
        self,
        name,
        value,
        quote=False
    ):
        self.name = name
        self.value = value
        self.quote = quote

    def __repr__(self):
        repr_string = '{}: {}'.format(
            self.name,
            optional_quote_string(self.value, self.quote)
        )
        return repr_string

def indent(multiline_string):
    return '\n'.join(f'{INDENT_STRING}{line}' for line in multiline_string.splitlines())

def optional_quote_string(value, quote):
    if quote:
        return f'"{value}"'
    else:
        return value
