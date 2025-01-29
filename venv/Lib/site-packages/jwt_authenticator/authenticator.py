import os
import jwt
import pymysql
import logging
from functools import wraps
from azure.functions import HttpRequest, HttpResponse

class JWTAuthenticator:
    def __init__(self, db_config, secret_key):
        """
        Initialize the JWTAuthenticator.

        Args:
            db_config (dict): Database configuration containing host, user, password, etc.
            secret_key (str): Secret key for JWT decoding.
        """
        self.db_config = db_config
        self.secret_key = secret_key
        self.logger = logging.getLogger(__name__)

    def jwt_required(self, f):
        """
        Decorator to enforce JWT-based authentication.
        """
        @wraps(f)
        def decorated_function(req: HttpRequest, *args, **kwargs):
            try:
                # Extract token from request
                token = self._extract_token(req)
                
                # Decode and validate JWT
                payload = self._decode_token(token)
                
                # Verify token in the database
                self._verify_token_in_db(payload.get('token_id'))
                
                # Attach JWT payload to the request for downstream usage
                req.jwt_payload = payload

            except Exception as e:
                # Handle errors and return an appropriate response
                return self._handle_error(e)

            # Proceed with the original function if authentication is successful
            return f(req, *args, **kwargs)
        return decorated_function

    def _extract_token(self, req: HttpRequest) -> str:
        """
        Extract JWT token from request headers or cookies.

        Args:
            req (HttpRequest): Azure Function HTTP request object.

        Returns:
            str: Extracted JWT token.

        Raises:
            ValueError: If token is missing.
        """
        # Attempt to extract token from cookies
        cookie_header = req.headers.get('Cookie', '')
        cookies = {
            cookie.split('=')[0]: cookie.split('=')[1]
            for cookie in cookie_header.split('; ') if '=' in cookie
        }
        token = cookies.get('auth_token')

        # If token is not found in cookies, check the Authorization header
        if not token:
            auth_header = req.headers.get('Authorization', None)
            if auth_header:
                token = auth_header.split(" ")[1]  # Extract token from "Bearer <token>"
            else:
                raise ValueError("Token is missing")

        return token

    def _decode_token(self, token: str) -> dict:
        """
        Decode the JWT token and validate its signature.

        Args:
            token (str): JWT token.

        Returns:
            dict: Decoded JWT payload.

        Raises:
            jwt.ExpiredSignatureError: If the token is expired.
            jwt.InvalidTokenError: If the token is invalid.
        """
        return jwt.decode(token, self.secret_key, algorithms=['HS256'])

    def _verify_token_in_db(self, token_id: str):
        """
        Verify the token's existence in the database to prevent blacklisted tokens.

        Args:
            token_id (str): Unique identifier of the JWT token.

        Raises:
            ValueError: If the token is not found in the database or is blacklisted.
        """
        if not token_id:
            raise ValueError("Token ID is missing from payload")

        try:
            connection = pymysql.connect(**self.db_config)
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM jwt_token WHERE token_id = %s", [token_id])
                token_record = cursor.fetchone()

                if not token_record:
                    raise ValueError("JWT token is blacklisted")
        finally:
            connection.close()

    def _handle_error(self, e: Exception) -> HttpResponse:
        """
        Handle authentication errors and return an appropriate HTTP response.

        Args:
            e (Exception): Caught exception during authentication.

        Returns:
            HttpResponse: Azure Function HTTP response object with an error message.
        """
        self.logger.error(f"JWT validation error: {e}")

        if isinstance(e, jwt.ExpiredSignatureError):
            return HttpResponse(
                '{"success": false, "error": "Token is expired. Please log in again."}',
                status_code=401,
                mimetype="application/json"
            )
        elif isinstance(e, jwt.InvalidTokenError):
            return HttpResponse(
                '{"success": false, "error": "Invalid token."}',
                status_code=401,
                mimetype="application/json"
            )
        elif isinstance(e, ValueError):
            return HttpResponse(
                f'{{"success": false, "error": "{str(e)}"}}',
                status_code=401,
                mimetype="application/json"
            )
        else:
            return HttpResponse(
                '{"success": false, "error": "Internal server error during authentication."}',
                status_code=500,
                mimetype="application/json"
            )
