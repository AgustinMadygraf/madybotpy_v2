"""
Path: src/services/data_validator.py
Este módulo contiene un esquema de validación de datos
y un validador para los datos recibidos en el controlador.
"""

from marshmallow import Schema, fields

class BrowserDataSchema(Schema):
    """
    BrowserDataSchema is a Marshmallow schema for validating browser data.
    """
    userAgent = fields.String(required=True, error_messages={"required": "El campo 'userAgent' es obligatorio."})
    screenResolution = fields.String(required=True, error_messages={"required": "El campo 'screenResolution' es obligatorio."})
    language = fields.String(required=True, error_messages={"required": "El campo 'language' es obligatorio."})
    platform = fields.String(required=True, error_messages={"required": "El campo 'platform' es obligatorio."})

class UserDataSchema(Schema):
    "Esquema de validación para los datos del usuario."
    id = fields.String(required=True, error_messages={"required": "El campo 'id' es obligatorio."})
    browserData = fields.Nested(BrowserDataSchema, required=True, error_messages={"required": "El campo 'browserData' es obligatorio."})

class DataSchema(Schema):
    "Esquema de validación para los datos recibidos en el controlador."
    prompt_user = fields.String(
        required=True,
        validate=lambda m: len(m) <= 255,
        error_messages={"required": "El campo 'prompt_user' es obligatorio.", "validator_failed": "El campo 'prompt_user' no debe exceder los 255 caracteres."}
    )
    stream = fields.Boolean(
        missing=False,
        error_messages={"invalid": "El campo 'stream' debe ser un valor booleano."}
    )
    user_data = fields.Nested(UserDataSchema, required=True, error_messages={"required": "El campo 'user_data' es obligatorio."})
    datetime = fields.Integer(
        missing=False,
        error_messages={"invalid": "El campo 'datetime' debe ser un valor entero."}
    )

class DataSchemaValidator:
    """
    DataSchemaValidator is a class responsible for validating data against a predefined schema.
    Attributes:
        schema (DataSchema): An instance of the DataSchema class used for validation.
    Methods:
        __init__():
            Initializes the DataSchemaValidator with a DataSchema instance.
        validate(data):
            Validates the provided data using the schema.
            Args:
                data (dict): The data to be validated.
            Returns:
                dict: The validated data.
            Raises:
                ValidationError: If the data does not conform to the schema.
    """
    def __init__(self):
        self.schema = DataSchema()

    def validate(self, data):
        "Valida los datos usando el esquema."
        return self.schema.load(data)
