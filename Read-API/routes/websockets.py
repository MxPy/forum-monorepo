from fastapi import WebSocket, WebSocketDisconnect, HTTPException, APIRouter
# from auth import decode_access_token
from websocket.connectionManager import manager
from queue.queueManager import add_user_to_active_users, remove_user_from_active_users

router = APIRouter(prefix='/socket', tags=['socket'])


@router.websocket("/connect/{user_id}")
async def user_connect(user_id: str, websocket: WebSocket):
    protocols = websocket.headers.get('sec-websocket-protocol', '').split(', ')
    
    session_id = None
    for protocol in protocols:
        if protocol.startswith('session-id.'):
            session_id = protocol.replace('session-id.', '')
            break
    
    # if not session_id:
    #     await websocket.close(code=4001)
    #     return

    # auth = await decode_access_token(session_id)
    # if not auth.get("valid"):
    #     await websocket.close(code=403)
    #     return

    
    await manager.connect(user_id, websocket)
    await add_user_to_active_users(user_id, session_id)
    try:
        while True:
            data = await websocket.receive_json()
            await manager.broadcast(user_id, data)
    except WebSocketDisconnect:
        await manager.disconnect(user_id, websocket)
        await remove_user_from_active_users(user_id, session_id)
