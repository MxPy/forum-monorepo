from fastapi import FastAPI, HTTPException, status
from grpc import StatusCode, RpcError

# Mapowanie kodów błędów gRPC na kody HTTP
GRPC_TO_HTTP_STATUS = {
    StatusCode.NOT_FOUND: status.HTTP_404_NOT_FOUND,
    StatusCode.ALREADY_EXISTS: status.HTTP_409_CONFLICT,
    StatusCode.INTERNAL: status.HTTP_500_INTERNAL_SERVER_ERROR,
    StatusCode.INVALID_ARGUMENT: status.HTTP_400_BAD_REQUEST,
    StatusCode.PERMISSION_DENIED: status.HTTP_403_FORBIDDEN,
    StatusCode.UNAUTHENTICATED: status.HTTP_401_UNAUTHORIZED
}

ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif'}