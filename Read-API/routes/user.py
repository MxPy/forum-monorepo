from fastapi import Depends, status, HTTPException, APIRouter, Body, Response, Request, HTTPException, status
from user_pb2_grpc import UserServiceStub
from user_pb2 import CreateUserRequest, GetUserRequest, UpdateAvatarRequest
from schemas.user import User
from fastapi import FastAPI, HTTPException, status
from gRPC_errors import GRPC_TO_HTTP_STATUS, ALLOWED_EXTENSIONS
from grpc import StatusCode, RpcError, insecure_channel
from typing import Dict
from google.protobuf import timestamp_pb2
from google.protobuf.json_format import MessageToJson
from datetime import datetime
import json
import logging

router = APIRouter(prefix='/users', tags=['users'])
channel = insecure_channel("database-driver:50051")
stub = UserServiceStub(channel)
DEFAULT_AVATAR_LINK = "http://localhost:9001/avatars/doman.png"
logger = logging.getLogger()

@router.get('/whoami', status_code=status.HTTP_200_OK)
async def get_user(userId: str):
    try:
        try:
            user_id_str = str(userId)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User ID must be a valid string"
            )

        response = stub.GetUser(
            GetUserRequest(
                userId=user_id_str
            )
        )
        return json.loads(MessageToJson(response))
    except RpcError as e:
        status_code = e.code()
        detail = e.details()
        
        if status_code == StatusCode.NOT_FOUND:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID {userId} not found"
            )
            
        http_status = GRPC_TO_HTTP_STATUS.get(
            status_code,
            status.HTTP_500_INTERNAL_SERVER_ERROR
        )
        
        raise HTTPException(
            status_code=http_status,
            detail=detail or "Error while fetching user data"
        )
