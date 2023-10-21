"""Functions for Authentication for the Apps"""
import os
from functools import wraps
from custom_exceptions import PermissionException, SupabaseException
from fastapi import WebSocket

from log_configs import log
import schema

#pylint: disable=too-few-public-methods, unused-argument

def admin_auth_check_decorator(func):
    """For all data managment APIs"""

    @wraps(func)
    async def wrapper(*args, **kwargs):
        # Extract the access token from the request headers
        access_token = kwargs.get("token")
        if not access_token:
            raise ValueError("Access token is missing")
        access_token_str = access_token.get_secret_value()
        # Verify the access token using Supabase secret
        try:
            user_data = supa.auth.get_user(access_token_str)

        except gotrue.errors.AuthApiError as e:
            raise PermissionException("Unauthorized access. Invalid token.") from e
        else:
            result = (
                supa.table("adminUsers")
                .select(
                    """
                    user_id
                    """
                )
                .eq("user_id", user_data.user.id)
                .execute()
            )
        if not result.data:
            raise PermissionException("Unauthorized access. User is not admin.")

    def check_role(self, user_id, role) -> bool:
        '''Check if the user has given role'''
        # To be implemented by the implementing class
        return False

    def get_accessible_labels(self, user_id) -> [str]:
        '''Check user rights and find document labels he can access'''
        # To be implemented by the implementing class
        return []

    def admin_auth_check_decorator(self, func):
        '''For all data managment APIs'''
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract the access token from the request headers
            access_token = kwargs.get('token')
            if not access_token:
                raise ValueError("Access token is missing")
            user_data = self.check_token(access_token)
            if not self.check_role(user_data['user_id'], 'admin'):
                raise PermissionException("Unauthorized access. User is not admin.")
            return await func(*args, **kwargs)

        return wrapper


def chatbot_auth_check_decorator(func):
    """checks a predefined token in request header, and checks it is a
    valid, logged in, user.
    """

    @wraps(func)
    async def wrapper(websocket: WebSocket, *args, **kwargs):
        # Extract the access token from the request headers
        access_token = kwargs.get("token")
        if not access_token:
            raise ValueError("Access token is missing")
        access_token_str = access_token.get_secret_value()

        # Verify the access token using Supabase secret
        try:
            supa.auth.get_user(access_token_str)

        except gotrue.errors.AuthApiError as e:
            await websocket.accept()
            json_response = schema.BotResponse(
                sender=schema.SenderType.BOT,
                message="Please sign in first. I look forward to answering your questions.",
                type=schema.ChatResponseType.ANSWER,
                sources=[],
                media=[],
            )
            await websocket.send_json({"logged_in": False, **json_response.dict()})
            return
        return await func(websocket, *args, **kwargs)

    return wrapper


def chatbot_get_labels_decorator(func):
    """checks a predefined token in request header, and returns available sources."""

    @wraps(func)
    async def wrapper(*args, **kwargs):
        # Extract the access token from the request headers
        access_token = kwargs.get("token")
        if not access_token:
            db_labels = []
        else:
            access_token_str = access_token.get_secret_value()

            # Verify the access token using Supabase secret
            try:
                self.check_token(access_token)
            except PermissionException:
                await websocket.accept()
                json_response = schema.BotResponse(sender=schema.SenderType.BOT,
                        message='Please sign in first. I look forward to answering your questions.',
                        type=schema.ChatResponseType.ANSWER,
                        sources=[],
                        media=[])
                await websocket.send_json({'logged_in': False, **json_response.dict()})
                return
            except Exception as exe: #pylint: disable=broad-exception-caught
                log.exception(exe)
                await websocket.accept()
                json_response = schema.BotResponse(sender=schema.SenderType.BOT,
                        message='Error in Authentication:'+str(exe),
                        type=schema.ChatResponseType.ANSWER,
                        sources=[],
                        media=[])
                await websocket.send_json({'logged_in': False, **json_response.dict()})
                return
            return await func(websocket, *args, **kwargs)

            except gotrue.errors.AuthApiError as e:  # The user is not logged in
                db_labels = []
            else:
                result = (
                    supa.table("userAttributes")
                    .select('id, user_id, user_type, "userTypes"(user_type, sources)')
                    .eq("user_id", user_data.user.id)
                    .execute()
                )
                db_labels = []
                for data in result.data:
                    db_labels.extend(data.get("userTypes", {}).get("sources", []))
                log.info(f"{db_labels=}")
        kwargs["labels"] = [label for label in kwargs["labels"] if label in db_labels]
        # Proceed with the original function call and pass the sources to it
        return await func(*args, **kwargs)

            kwargs['labels'] = [label for label in kwargs['labels'] if label in db_labels]
            # Proceed with the original function call and pass the sources to it
            return await func(*args, **kwargs)

        return wrapper
