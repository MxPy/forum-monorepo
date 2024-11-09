import aio_pika
import logging
from queue.settings import settings
from typing import AsyncGenerator
from fastapi import Depends, FastAPI
from contextlib import asynccontextmanager
from websocket.connectionManager import manager
from queue.messages import *
import json
from typing import Dict, List

logger = logging.getLogger()

activeUsersTemplate = Dict[str, List[str]]
activeUsers: activeUsersTemplate = {}

async def get_amqp_connection() -> aio_pika.abc.AbstractConnection:
    """Connect to AMQP server."""
    return await aio_pika.connect_robust(str(settings.AMQP_URL))

async def add_user_to_active_users(user_id: str, session_id: str):
    """
    Add user session to active users dictionary.
    
    Args:
        user_id: User identifier
        session_id: Session identifier
    """
    logger.info(f"Adding user {user_id} with session {session_id} to active users")
    
    if user_id not in activeUsers:
        activeUsers[user_id] = []
    
    if session_id not in activeUsers[user_id]:
        activeUsers[user_id].append(session_id)
    
    logger.debug(f"Active users after addition: {activeUsers}")

async def remove_user_from_active_users(user_id: str, session_id: str):
    """
    Remove user session from active users dictionary.
    
    Args:
        user_id: User identifier
        session_id: Session identifier
    """
    logger.info(f"Removing user {user_id} with session {session_id} from active users")
    
    if user_id in activeUsers:
        if session_id in activeUsers[user_id]:
            activeUsers[user_id].remove(session_id)
            
            # If user has no active sessions, remove user entry
            if not activeUsers[user_id]:
                del activeUsers[user_id]
    
    logger.debug(f"Active users after removal: {activeUsers}")

async def declare_queue(
    channel: aio_pika.abc.AbstractChannel,
    queue: str,
    **kwargs,
) -> aio_pika.abc.AbstractQueue:
    """Create AMQP queue."""
    return await channel.declare_queue(name=queue, auto_delete=True, **kwargs)
        
async def process_message(message: aio_pika.abc.AbstractIncomingMessage):
    """Do something with the message.
w
    :param message: A message from the queue.
    """
    try:
        async with message.process(requeue=True):
            logger.info(f"MESSAGE RECEIVED: {message.message_id}")
            msg = BroadcastMessage(**json.loads(message.body.decode()))
            
            logger.info(
                f"MESSAGE CONSUMED: {message.message_id} -- {msg.body})"
            )
            await manager.broadcast("chuj", {
                "message_id": message.message_id,
                "body": msg.body
            })
    except Exception as e:
        logger.error(e)

async def process_broadcast_message(message: aio_pika.abc.AbstractIncomingMessage):
    """Do something with the message.
w
    :param message: A message from the queue.
    """
    try:
        async with message.process(requeue=True):
            logger.info(f"MESSAGE RECEIVED: {message.message_id}")
            msg = BroadcastMessage(**json.loads(message.body.decode()))
            
            logger.info(
                f"BROADCAST MESSAGE CONSUMED: {message.message_id} -- {msg.body})"
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
        await channel.set_qos(prefetch_count=settings.PREFECTH_COUNT)
        queue = await declare_queue(channel=channel, queue=settings.QUEUE)
        await queue.consume(process_message)
        yield