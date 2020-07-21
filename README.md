# graphql_client

A simple GraphQL client for Python

## Installation
```
pip install wf-graphql-client-python
```
## Preliminary design choices

#### Make this layer schema-agnostic

We would like to be able to use this library with any GraphQL schema, so we have avoided building in any schema-specific functionality (e.g., type checking/conversion for Python objects based on corresponding GraphQL types). The idea would be to build additional schema-specific layers on top of this layer. We are trying to build in hooks for those later layers to use. For example, just before sending the request to the GraphQL server, we convert the request variables to JSON via a custom `graphql_json_dumps()` function. If any supplied object has a `.graphql_json()` method, this function will use that method rather than the default JSON encoder. This would be an obvious way to specify schema-specific type checking/type conversion/serialization rules.

#### Always pass parameters via variables

All parameters must be passed to the server via GraphQL variables (rather than inserting them directly into the request body). We made this choice because parameters in the request body have strict and idiosyncratic serialization rules that require schema-specific logic (e.g., parameter names are unquoted, string parameter values are quoted but enum parameter values are not, etc.), whereas if we pass the same values as variables, the server accepts and converts standard JSON serialization for the vast majority of values (e.g., parameter names are quoted, string and enum parameter values are both quoted, etc.). This allows us to build a more fully functional interface without resorting to schema-specific logic.

#### Use an object-oriented approach

Common components of a GraphQL request are defined as custom classes (e.g., `Operation`, `Variable`, `Parameter`, `Field`) rather than native Python objects with idiosyncratic structure rules. This allows us to be much more explicit about the components of these objects.

#### Implement a fluent interface

One downside of the object-oriented approach is that it can lead to much more typing. To try to mitigate this, we have implemented a fluent interface that allows chaining alongside the "standard" constructor interface. So, for example,
```
Operation(
    operation_type='query',
    operation_name='DeviceAssignments',
    variables=[
        Variable(
            name='device_type',
            type='DeviceType',
            value=selected_device_type
        ),
        Variable(
            name='assignments_filter',
            type='_DeviceDeviceAssignmentFilter',
            value={
                'AND': {
                    'start_lte': {'formatted': selected_datetime_string},
                    'OR': {
                        'end': None,
                        'end_gte': {'formatted': selected_datetime_string}
                    }
                }
            }
        )
    ],
    fields=[
        Field(
            name='Device',
            parameters=[
                Parameter(parameter_name='device_type', variable_name='device_type')
            ],
            subfields=[
                Field('device_id'),
                Field('name'),
                Field(
                    name='assignments',
                    parameters=[
                        Parameter(parameter_name='filter', variable_name='assignments_filter')
                    ],
                    subfields=[
                        Field(
                            name='Environment',
                            subfields=[
                                Field('name')
                            ]
                        ),
                        Field(
                            name='start',
                            subfields=[
                                Field('formatted')
                            ]
                        ),
                        Field(
                            name='end',
                            subfields=[
                                Field('formatted')
                            ]
                        )
                    ]
                )
            ]
        )
    ]
)
```
can also be written as
```
Operation(operation_type='query', operation_name='DeviceAssignments')
    .add_variable(Variable(
        name='device_type',
        type='DeviceType',
        value=selected_device_type
    ))
    .add_variable(Variable(
        name='assignments_filter',
        type='_DeviceDeviceAssignmentFilter',
        value={
            'AND': {
                'start_lte': {'formatted': selected_datetime_string},
                'OR': {
                    'end': None,
                    'end_gte': {'formatted': selected_datetime_string}
                }
            }
        }
    ))
    .add_field(
        Field('Device')
            .add_parameter(Parameter(parameter_name='device_type', variable_name='device_type'))
            .add_subfield(Field('device_id'))
            .add_subfield(Field('name'))
            .add_subfield(Field('assignments')
                .add_parameter(Parameter(parameter_name='filter', variable_name='assignments_filter'))
                .add_subfield(Field('Environment')
                    .add_subfield(Field('name'))
                 )
                .add_subfield(Field('start')
                    .add_subfield(Field('formatted'))
                 )
                .add_subfield(Field('end')
                    .add_subfield(Field('formatted'))
                 )
            )
    )
```
