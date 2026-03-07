from typing import Any

class _Message:
    content: str | None

class _Choice:
    message: _Message

class _CompletionResponse:
    choices: list[_Choice]

class _Completions:
    def create(self, *args: Any, **kwargs: Any) -> _CompletionResponse: ...

class _Chat:
    completions: _Completions

class OpenAI:
    chat: _Chat
    def __init__(self, *, api_key: str | None = ...) -> None: ...
