import asyncio
import inspect
from functools import partial
from typing import Any, Callable, Optional, TypeVar, Union, overload

from marvin.components.ai_function import ai_fn
from marvin.utilities.asyncio import run_sync
from marvin.utilities.jinja import BaseEnvironment

T = TypeVar("T")

prompt = inspect.cleandoc(
    "The user will provide context as text that you need to parse into a structured"
    " form. To validate your response, you must call the"
    " `{{_response_model.function.name}}` function. Use the provided text to extract or"
    " infer any parameters needed by `{{_response_model.function.name}}`, including any"
    " missing data."
    " user: The text to parse: {{text}}"
)


@overload
def ai_model(
    *,
    environment: Optional[BaseEnvironment] = None,
    prompt: Optional[str] = prompt,
    model_name: str = "FormatResponse",
    model_description: str = "Formats the response.",
    field_name: str = "data",
    field_description: str = "The data to format.",
    **render_kwargs: Any,
) -> Callable[[T], Callable[[str], T]]:
    pass


@overload
def ai_model(
    _type: Optional[T],
    *,
    environment: Optional[BaseEnvironment] = None,
    prompt: Optional[str] = prompt,
    model_name: str = "FormatResponse",
    model_description: str = "Formats the response.",
    field_name: str = "data",
    field_description: str = "The data to format.",
    **render_kwargs: Any,
) -> Callable[[str], T]:
    pass


def ai_model(
    _type: Optional[T] = None,
    *,
    environment: Optional[BaseEnvironment] = None,
    prompt: Optional[str] = prompt,
    model_name: str = "FormatResponse",
    model_description: str = "Formats the response.",
    field_name: str = "data",
    field_description: str = "The data to format.",
    **render_kwargs: Any,
) -> Union[Callable[[T], Callable[[str], T]], Callable[[str], T],]:
    def wrapper(_type_: T, text: str) -> T:
        def extract(text: str) -> T:  # type: ignore
            pass

        extract.__annotations__["return"] = _type_

        return ai_fn(
            extract,
            environment=environment,
            prompt=prompt,
            model_name=model_name,
            model_description=model_description,
            field_name=field_name,
            field_description=field_description,
            **render_kwargs,
        )(text)

    async def async_wrapper(_type_: T, text: str) -> T:
        return wrapper(_type_, text)

    async def amap(inputs: list[str]) -> list[T]:
        return await asyncio.gather(
            *[
                asyncio.create_task(async_wrapper(_type, input_text))
                for input_text in inputs
            ]
        )

    def map(inputs: list[str]) -> list[T]:
        return run_sync(amap(inputs))

    if _type is not None:
        wrapper_with_map = partial(wrapper, _type)
        wrapper_with_map.amap = amap
        wrapper_with_map.map = map
        return wrapper_with_map

    def decorator(_type_: T) -> Callable[[str], T]:
        decorated = partial(wrapper, _type_)
        decorated.amap = amap
        decorated.map = map
        return decorated

    return decorator
