from flask import Flask, jsonify
from flask_swagger_ui import get_swaggerui_blueprint

# URL for exposing Swagger UI (without trailing '/')
SWAGGER_URL = '/api/docs'
# This must point to a valid OpenAPI/Swagger JSON definition
API_URL = '/swagger.json'

blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,  # Swagger UI static files will be mapped to '{SWAGGER_URL}/dist/'
    API_URL,
    config={  # Swagger UI config overrides
        'app_name': "Test application"
    },
    # oauth_config={  # OAuth config. See https://github.com/swagger-api/swagger-ui#oauth2-configuration .
    #    'clientId': "your-client-id",
    #    'clientSecret': "your-client-secret-if-required",
    #    'realm': "your-realms",
    #    'appName': "your-app-name",
    #    'scopeSeparator': " ",
    #    'additionalQueryStringParams': {'test': "hello"}
    # }
)


def create_app():
    app = Flask(__name__)

    @app.route('/')
    def hello():
        return "Hello from Flask!"

    # Minimal OpenAPI 3.0 spec so Swagger UI can render
    @app.get('/swagger.json')
    def swagger_spec():
        spec = {
            "openapi": "3.0.3",
            "info": {
                "title": "Test application",
                "version": "1.0.0",
                "description": "Minimal OpenAPI spec for the Flask app"
            },
            "servers": [
                {"url": "http://localhost:8000"}
            ],
            "paths": {
                "/": {
                    "get": {
                        "summary": "Hello endpoint",
                        "responses": {
                            "200": {
                                "description": "A friendly greeting",
                                "content": {
                                    "text/plain": {
                                        "schema": {"type": "string"},
                                        "examples": {"example": {"value": "Hello from Flask!"}}
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
        return jsonify(spec)

    app.register_blueprint(blueprint)

    return app



if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=8000, debug=True)