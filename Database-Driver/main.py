import grpc
import logging
import todo_pb2
import todo_pb2_grpc
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import time
from concurrent import futures
from google.protobuf import empty_pb2, timestamp_pb2
import os
from datetime import datetime
import user_pb2
import user_pb2_grpc
import logging
import sys
ch = logging.StreamHandler(sys.stdout)
logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(funcName)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[ch]
    )
logger = logging.getLogger()
# SQLAlchemy database URL
DATABASE_URL = os.environ.get("DATABASE_URL")

# Create a SQLAlchemy engine
engine = create_engine(DATABASE_URL)

# Create a session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create a Base class for declarative models
Base = declarative_base()

#move it to models
# Define the Todo model
class Todo(Base):
    __tablename__ = "todo"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    image_link = Column(String)
    community = Column(String)
    vote_count = Column(Integer, default=0)
    author = Column(String)

# Define the User model
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, unique=True)
    nick_name = Column(String)
    avatar = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_banned = Column(Boolean, default=False)
    ban_expiration_date = Column(DateTime)
    banned_by_admin_id = Column(String, default="")

# Helper functions
def datetime_to_timestamp(dt):
    return timestamp_pb2.Timestamp(seconds=int(dt.timestamp()), nanos=dt.microsecond * 1000)

def timestamp_to_datetime(ts):
    return datetime.fromtimestamp(ts.seconds + ts.nanos / 1e9)


# Create the todo table
Base.metadata.create_all(bind=engine)

# Helper functions remain the same
def datetime_to_timestamp(dt):
    return timestamp_pb2.Timestamp(seconds=int(dt.timestamp()), nanos=dt.microsecond * 1000)

def timestamp_to_datetime(ts):
    return datetime.fromtimestamp(ts.seconds + ts.nanos / 1e9)

# Define the gRPC service
class TodoServicer(todo_pb2_grpc.TodoServiceServicer):

    def Create(self, request, context):
        todo = Todo(
            title=request.title,
            description=request.description,
            created_at=timestamp_to_datetime(request.created_at),
            image_link=request.image_link,
            community=request.community,
            vote_count=request.vote_count,
            author=request.author
        )
        db = SessionLocal()
        db.add(todo)
        db.commit()
        db.refresh(todo)
        db.close()
        return self._todo_to_proto(todo)

    def Read(self, request, context):
        db = SessionLocal()
        todo = db.query(Todo).filter(Todo.id == request.id).first()
        db.close()
        if todo:
            return self._todo_to_proto(todo)
        else:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details("Todo not found")
            return todo_pb2.Todo()

    def Update(self, request, context):
        db = SessionLocal()
        todo = db.query(Todo).filter(Todo.id == request.id).first()
        if todo:
            todo.title = request.title
            todo.description = request.description
            todo.image_link = request.image_link
            todo.community = request.community
            todo.vote_count = request.vote_count
            todo.author = request.author
            db.add(todo)
            db.commit()
            db.refresh(todo)
            db.close()
            return self._todo_to_proto(todo)
        else:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details("Todo not found")
            return todo_pb2.Todo()

    def Delete(self, request, context):
        db = SessionLocal()
        todo = db.query(Todo).filter(Todo.id == request.id).first()
        if todo:
            db.delete(todo)
            db.commit()
            db.close()
            return empty_pb2.Empty()
        else:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details("Todo not found")
            return empty_pb2.Empty()

    def List(self, request, context):
        db = SessionLocal()
        todos = db.query(Todo).all()
        db.close()
        return todo_pb2.TodoListResponse(todos=[self._todo_to_proto(todo) for todo in todos])
    
    def ListOlderThan(self, request, context):
        db = SessionLocal()
        timestamp = timestamp_to_datetime(request.timestamp)
        todos = db.query(Todo).filter(Todo.created_at < timestamp).order_by(Todo.created_at.desc()).limit(25).all()
        db.close()
        return todo_pb2.TodoListResponse(todos=[self._todo_to_proto(todo) for todo in todos])

    def _todo_to_proto(self, todo):
        return todo_pb2.Todo(
            id=todo.id,
            title=todo.title,
            description=todo.description,
            created_at=datetime_to_timestamp(todo.created_at),
            image_link=todo.image_link,
            community=todo.community,
            vote_count=todo.vote_count,
            author=todo.author
        )
# Define the gRPC service
class UserServicer(user_pb2_grpc.UserServiceServicer):
    def CreateUser(self, request, context):
        db = SessionLocal()
        
        # Check if user already exists
        existing_user = db.query(User).filter(User.user_id == request.userId).first()
        if existing_user:
            context.set_code(grpc.StatusCode.ALREADY_EXISTS)
            context.set_details("User already exists")
            db.close()
            return user_pb2.InfoResponse(info="User already exists")
        user = User(
            user_id=request.userId,
            nick_name=request.nickName,
            avatar=request.avatar,
            created_at=timestamp_to_datetime(request.createdAt),
            is_banned=request.isBanned,
            ban_expiration_date=timestamp_to_datetime(request.banExpirationDate),
            banned_by_admin_id=request.bannedByAdminId,
        )
        
        try:
            db.add(user)
            db.commit()
            db.refresh(user)
            db.close()
            return user_pb2.InfoResponse(info=f"User created successfully with ID: {user.user_id}")
        except Exception as e:
            db.rollback()
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Error creating user: {str(e)}")
            return user_pb2.InfoResponse(info=f"Error creating user: {str(e)}")
        finally:
            db.close()

    def GetUser(self, request, context):
        db = SessionLocal()
        user = db.query(User).filter(User.user_id == request.userId).first()
        if user:
            response = user_pb2.GetUserResponse(
                userId=user.user_id,
                nickName=user.nick_name,
                avatar=user.avatar,
                createdAt=datetime_to_timestamp(user.created_at),
                isBanned=user.is_banned,
                banExpirationDate=datetime_to_timestamp(user.ban_expiration_date),
                bannedByAdminId=user.banned_by_admin_id,
            )
            db.close()
            return response
        else:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details("User not found")
            db.close()
            return user_pb2.GetUserResponse()

    def UpdateAvatar(self, request, context):
        db = SessionLocal()
        user = db.query(User).filter(User.user_id == request.userId).first()
        
        if user:
            try:
                user.avatar = request.avatar
                db.commit()
                db.refresh(user)
                db.close()
                return user_pb2.InfoResponse(info=f"Avatar updated successfully for user: {user.user_id}")
            except Exception as e:
                db.rollback()
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details(f"Error updating avatar: {str(e)}")
                return user_pb2.InfoResponse(info=f"Error updating avatar: {str(e)}")
        else:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details("User not found")
            db.close()
            return user_pb2.InfoResponse(info="User not found")

    def BanUnbanPlayer(self, request, context):
        db = SessionLocal()
        user = db.query(User).filter(User.user_id == request.userId).first()
        
        if user:
            try:
                user.is_banned = request.isBanned
                user.ban_expiration_date = timestamp_to_datetime(request.banExpirationDate)
                db.commit()
                db.refresh(user)
                db.close()
                if request.isBanned:
                    return user_pb2.InfoResponse(info=f"User {user.user_id} has been banned until {user.ban_expiration_date}")
                else:
                    return user_pb2.InfoResponse(info=f"User {user.user_id} has been unbanned")
            except Exception as e:
                db.rollback()
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details(f"Error banning/unbanning user: {str(e)}")
                return user_pb2.InfoResponse(info=f"Error banning/unbanning user: {str(e)}")
        else:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details("User not found")
            db.close()
            return user_pb2.InfoResponse(info="User not found")


# Server setup remains the same
server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
user_pb2_grpc.add_UserServiceServicer_to_server(UserServicer(), server)
todo_pb2_grpc.add_TodoServiceServicer_to_server(TodoServicer(), server)
server.add_insecure_port('[::]:50051')
server.start()
logging.info("Server started on port 50051")

try:
    while True:
        time.sleep(86400)
except KeyboardInterrupt:
    server.stop(0)