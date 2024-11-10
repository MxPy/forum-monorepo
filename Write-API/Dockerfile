FROM python:3.10

WORKDIR /app

COPY . .
RUN pip install --upgrade pip  && \
    pip install --no-cache-dir -r req.txt

EXPOSE 8000
RUN python -m grpc_tools.protoc -I ./protobuf --python_out=. --grpc_python_out=. todo.proto && \
    python -m grpc_tools.protoc -I ./protobuf --python_out=. --grpc_python_out=. user.proto
CMD ["python3", "main.py"]