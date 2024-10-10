import grpc
import logging
import todo_pb2
import todo_pb2_grpc
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import time
from concurrent import futures
from google.protobuf import empty_pb2, timestamp_pb2
import os
from datetime import datetime

# SQLAlchemy database URL
DATABASE_URL = os.environ.get("DATABASE_URL")

# Create a SQLAlchemy engine
engine = create_engine(DATABASE_URL)

# Create a session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create a Base class for declarative models
Base = declarative_base()

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

# Server setup remains the same
server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
todo_pb2_grpc.add_TodoServiceServicer_to_server(TodoServicer(), server)
server.add_insecure_port('[::]:50051')
server.start()
logging.info("Server started on port 50051")

try:
    while True:
        time.sleep(86400)
except KeyboardInterrupt:
    server.stop(0)