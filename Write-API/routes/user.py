from fastapi import Depends, status, HTTPException, APIRouter, Body, Response, Request, HTTPException, status
from user_pb2_grpc import UserServiceStub
from user_pb2 import CreateUserRequest, GetUserRequest, UpdateAvatarRequest
from schemas.user import User
from fastapi import FastAPI, HTTPException, status
from gRPC_errors import GRPC_TO_HTTP_STATUS
from grpc import StatusCode, RpcError, insecure_channel
from typing import Dict
from files.settings import settings
from files.schemas import UserAvatar
from files.services import upload_file
from google.protobuf import timestamp_pb2
from datetime import datetime

router = APIRouter(prefix='/users', tags=['users'])
channel = insecure_channel("database-driver:50051")
stub = UserServiceStub(channel)
DEFAULT_AVATAR_LINK = "http://localhost:9001/avatars/doman.png"

@router.post('/create', status_code=status.HTTP_201_CREATED)
async def create_user(request: User) -> Dict[str, str]:
    current_time = datetime.utcnow()
    timestamp = timestamp_pb2.Timestamp()
    timestamp.FromDatetime(current_time)
    try:
        response = stub.CreateUser(
            CreateUserRequest(
                userId=request.userId,
                avatar=DEFAULT_AVATAR_LINK,
                created_at=timestamp,
            )
        )
        return {"details": response.info}
    except RpcError as e:
        # Pobierz kod statusu gRPC
        status_code = e.code()
        # Pobierz szczegóły błędu
        detail = e.details()
        
        # Mapuj kod gRPC na kod HTTP lub użyj domyślnego 500
        http_status = GRPC_TO_HTTP_STATUS.get(
            status_code, 
            status.HTTP_500_INTERNAL_SERVER_ERROR
        )
        
        raise HTTPException(
            status_code=http_status,
            detail=detail or "Unexpected error occurred"
        )

@router.get('/whoami', status_code=status.HTTP_200_OK)
async def get_user(userId: str) -> Dict[str, str]:
    try:
        # Konwersja userId na int, z obsługą błędu
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
        return {
            "nickName": response.nickName,
            "avatar": response.avatar
        }
    except RpcError as e:
        status_code = e.code()
        detail = e.details()
        
        # Szczególna obsługa dla przypadku NOT_FOUND
        if status_code == StatusCode.NOT_FOUND:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID {userId} not found"
            )
            
        # Dla innych błędów używamy ogólnego mapowania
        http_status = GRPC_TO_HTTP_STATUS.get(
            status_code,
            status.HTTP_500_INTERNAL_SERVER_ERROR
        )
        
        raise HTTPException(
            status_code=http_status,
            detail=detail or "Error while fetching user data"
        )

@router.post('/avatar', status_code=status.HTTP_200_OK)
async def get_user(data: UserAvatar = Depends()) -> Dict[str, str]:
    if uploaded := await upload_file(
        user_id=file.user_id, bucket_name="avatars", file=file.file
    ):
        return uploaded