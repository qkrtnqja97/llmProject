# app/dependency.py

from fastapi import Request


def get_entity_service(request: Request):
    return request.app.state.container.entity_service


def get_memory_service(request: Request):
    return request.app.state.container.memory_service