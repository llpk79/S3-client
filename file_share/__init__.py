from dotenv import load_dotenv
from flask import Flask
from flask_dynamo import Dynamo
from flask_cognito import CognitoAuth


def create_app():
    app = Flask(__name__)
    load_dotenv()
    # Configure DynamoDB-tables.
    app.config['DYNAMO_TABLES'] = [
        dict(
             TableName='users',
             KeySchema=[dict(AttributeName='email', KeyType='S')],
             AttributeDefinitions=[dict(AttributeName='username', AttributeType='S')],
             ProvisionedThroughput=dict(ReadCapacityUnits=5, WriteCapacityUnits=5)
        ),
        dict(
             TableName='file-share-db',
             KeySchema=[dict(AttributeName='name', KeyType='S')],
             AttributeDefinitions=[dict(AttributeName='name', AttributeType='S')],
             ProvisionedThroughput=dict(ReadCapacityUnits=5, WriteCapacityUnits=5)
        )
    ]
    dynamo = Dynamo()
    dynamo.init_app(app)

    # Configure Cognito authorization.
    app.config.extend({
        'COGNITO_REGION': 'eu-central-1',
        'COGNITO_USERPOOL_ID': 'eu-central-1c3fea2',

        # optional
        'COGNITO_APP_CLIENT_ID': 'abcdef123456',  # client ID you wish to verify user is authenticated against
        'COGNITO_CHECK_TOKEN_EXPIRATION': False,  # disable token expiration checking for testing purposes
    })

    cogauth = CognitoAuth(app)

    @cogauth.identity_handler
    def lookup_cognito_user(payload):
        """Look up user in our database from Cognito JWT payload."""
        return dynamo.tables['users'].query(key='email')
    from . import routes
    app.register_blueprint(routes.bp)

    return app
