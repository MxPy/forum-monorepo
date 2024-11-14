from fastapi import Depends, FastAPI, status, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import HTTPException
from contextlib import asynccontextmanager
from datetime import datetime
from typing import AsyncGenerator
import uvicorn
import aio_pika
import logging
import sys
import asyncio
import json
import logging
import random
import uuid
from gRPC_errors import GRPC_TO_HTTP_STATUS, ALLOWED_EXTENSIONS
from grpc import StatusCode, RpcError, insecure_channel
from routes import user
from settings import settings  
from models import example
from schemas.message import Message
from enums.state import State
from websocket.connectionManager import ConnectionManager

from todo_pb2_grpc import TodoServiceStub
from todo_pb2 import TodoRequest, TodoListResponse, ListOlderThanRequest
from google.protobuf.json_format import MessageToJson
from google.protobuf.timestamp_pb2 import Timestamp
import grpc

ch = logging.StreamHandler(sys.stdout)
logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(funcName)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[ch]
    )
MSG_LOG = dict()
PREFECTH_COUNT = 100
logger = logging.getLogger()
manager = ConnectionManager()
channel = grpc.insecure_channel("database-driver:50051")
stub = TodoServiceStub(channel)

async def get_amqp_connection() -> aio_pika.abc.AbstractConnection:
    """Connect to AMQP server."""
    return await aio_pika.connect_robust(str(settings.AMQP_URL))


async def declare_queue(
    channel: aio_pika.abc.AbstractChannel,
    queue: str,
    **kwargs,
) -> aio_pika.abc.AbstractQueue:
    """Create AMQP queue."""
    return await channel.declare_queue(name=queue, auto_delete=True, **kwargs)


async def get_channel(
    connection: aio_pika.abc.AbstractConnection = Depends(get_amqp_connection)
) -> AsyncGenerator[aio_pika.abc.AbstractChannel, None]:
    """Connect to and yield a AMQP channel.

    :yield: RabbitMQ channel.
    """
    async with connection:
        channel = await connection.channel()
        await declare_queue(channel=channel, queue=settings.QUEUE)
        yield channel


async def process_message(message: aio_pika.abc.AbstractIncomingMessage):
    """Do something with the message.
w
    :param message: A message from the queue.
    """
    try:
        async with message.process(requeue=True):
            logger.info(f"MESSAGE RECEIVED: {message.message_id}")
            msg = Message(**json.loads(message.body.decode()))
            
            logger.info(
                f"MESSAGE CONSUMED: {message.message_id} -- {msg.body})"
            )
            MSG_LOG[message.message_id] = dict(
                message=msg.body,
                state=State.CONSUMED,
                consumed_at=datetime.now(),
            )
            
            await manager.broadcast("chuj", {
                "message_id": message.message_id,
                "body": msg.body
            })
    except Exception as e:
        logger.error(e)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Start internal message consumer on app startup."""
    connection = await aio_pika.connect_robust(str(settings.AMQP_URL))

    async with connection:
        channel = await connection.channel()
        await channel.set_qos(prefetch_count=PREFECTH_COUNT)
        queue = await declare_queue(channel=channel, queue=settings.QUEUE)
        await queue.consume(process_message)
        yield

app = FastAPI(lifespan=lifespan)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def logging_init(): 
    logging.info(f"Starting producer...")
    
    
@app.get("/")
async def read_root():
	return JSONResponse(content={"Hello":"World"})

@app.get("/healthcheck")
def healthcheck():
    """
    Check the health of the application.
    """
    return JSONResponse(content={"status": "ok"})

@app.get("/log")
def _():
    return MSG_LOG

#TODO: move this to other router

@app.websocket("/connect")
async def user_connect(websocket: WebSocket):
    room_id = "chuj"
    await manager.connect(str(room_id), websocket)
    # cache = rd.get(str(room_id))
    # if cache:
    #     await manager.broadcast(str(room_id), cache)
    #await manager.broadcast(str(room_id), "connected")
    try: 
        while True:
            data = await websocket.receive_json()
            #rd.set(str(room_id), data)
            await manager.broadcast(str(room_id), data)
    except WebSocketDisconnect:
        await manager.disconnect(str(room_id), websocket)
        #await manager.broadcast(str(room_id), "disconected")
        
@app.get("/todos")
def read_todos():
    # Read all Todos using the gRPC stub
    response = stub.List(TodoListResponse())
    # Convert the gRPC response message to JSON and return it
    return JSONResponse(content=json.loads(MessageToJson(response)))

@app.get("/todos/{todo_id}")
def read_todo(todo_id: int):
    # Read a Todo by ID using the gRPC stub
    try:
        response = stub.Read(TodoRequest(id=todo_id))
    
    except grpc.RpcError as e:
        if e.code() == grpc.StatusCode.NOT_FOUND:
            raise HTTPException(status_code=404, detail='Todo not found')
    # Convert the gRPC response message to JSON and return it
    return JSONResponse(content=json.loads(MessageToJson(response)))

# Helper function to convert datetime to gRPC Timestamp
def datetime_to_grpc_timestamp(dt):
    timestamp = Timestamp()
    timestamp.FromDatetime(dt)
    return timestamp

@app.get("/todos/older_than/{timestamp_str}")
def read_todos_older_than(timestamp_str: str):
    # Convert the timestamp_str (string) to a datetime object
    try:
        # Convert string to datetime using the correct format: "YYYY-MM-DD HH:MM:SS.ssssss"
        timestamp_datetime = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S.%f")
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid timestamp format. Use 'YYYY-MM-DD HH:MM:SS.ssssss'.")

    # Convert the datetime object to gRPC Timestamp
    grpc_timestamp = datetime_to_grpc_timestamp(timestamp_datetime)

    # Create the request with the gRPC timestamp
    request = ListOlderThanRequest(timestamp=grpc_timestamp)

    # Fetch older todos using the gRPC stub
    try:
        response = stub.ListOlderThan(request)
    except grpc.RpcError as e:
        raise HTTPException(status_code=500, detail=f"gRPC error: {e.details()}")

    # Convert the gRPC response message to JSON and return it
    return json.loads(MessageToJson(response))

app.include_router(user.router)
# Opcjonalnie możesz dodać middleware do globalnej obsługi błędów
@app.middleware("http")
async def grpc_error_handler(request, call_next):
    try:
        return await call_next(request)
    except RpcError as e:
        status_code = e.code()
        http_status = GRPC_TO_HTTP_STATUS.get(
            status_code,
            status.HTTP_500_INTERNAL_SERVER_ERROR
        )
        return JSONResponse(
            status_code=http_status,
            content={"detail": e.details() or "Internal server error"}
        )
    
if __name__ == '__main__':
    uvicorn.run("main:app", host="0.0.0.0", port=8000, log_level="info", reload=True)