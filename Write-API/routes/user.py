from fastapi import Depends, status, HTTPException, APIRouter, Body, Response, Request, HTTPException, status
from user_pb2_grpc import UserServiceStub
from user_pb2 import CreateUserRequest, GetUserRequest, UpdateAvatarRequest
from schemas.user import User
from fastapi import FastAPI, HTTPException, status
from gRPC_errors import GRPC_TO_HTTP_STATUS, ALLOWED_EXTENSIONS
from grpc import StatusCode, RpcError, insecure_channel
from typing import Dict
from files.settings import settings
from files.schemas import UserAvatar
from files.services import upload_file
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

@router.post('/create', status_code=status.HTTP_201_CREATED)
async def create_user(request: User) -> Dict[str, str]:
    current_time = datetime.utcnow()
    timestamp = timestamp_pb2.Timestamp()
    timestamp.FromDatetime(current_time)
    try:
        response = stub.CreateUser(
            CreateUserRequest(
                userId=request.userId,
                nickName=request.nickName,
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
async def get_user(userId: str):
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
        return json.loads(MessageToJson(response))
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

def handle_grpc_error(e: RpcError, default_message: str) -> HTTPException:
    status_code = e.code()
    detail = e.details() or default_message
    http_status = GRPC_TO_HTTP_STATUS.get(status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
    return HTTPException(status_code=http_status, detail=detail)

@router.post('/avatar')
async def get_user(data: UserAvatar = Depends()) -> Dict[str, str]:
    try:
        # Sprawdzenie czy użytkownik istnieje
        try:
            user_response = stub.GetUser(
                GetUserRequest(
                    userId=data.userId
                )
            )
        except RpcError as e:
            raise handle_grpc_error(e, f"Error with user ID {data.userId}")

        # Walidacja pliku
        original_extension = data.file.filename.split('.')[-1].lower() if '.' in data.file.filename else ''
        ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif'}
        if not original_extension or original_extension not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid file format. Allowed formats: {', '.join(ALLOWED_EXTENSIONS)}"
            )

        # Upload pliku
        new_filename = f"{data.userId}.{original_extension}"
        data.file.filename = new_filename

        if uploaded := await upload_file(
            user_id=data.userId,
            bucket_name="avatars",
            file=data.file
        ):
            try:
                # Aktualizacja avatara
                update_response = stub.UpdateAvatar(
                    UpdateAvatarRequest(
                        userId=data.userId,
                        avatar=uploaded
                    )
                )
                # Zwracamy status kod z gRPC
                return Response(
                    content=MessageToJson(update_response),
                    media_type="application/json",
                    status_code=status.HTTP_200_OK
                )
            except RpcError as e:
                raise handle_grpc_error(e, "Error while updating avatar")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )