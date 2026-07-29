from __future__ import annotations

import json
import os
from typing import Any

from providers.base import ModelResponse, ToolCall


class OpenAIProvider:
    """OpenAI Responses API provider with normalized tool_calls output."""

    def __init__(
        self,
        *,
        api_key_env: str = "OPENAI_API_KEY",
        base_url: str | None = None,
        default_model: str = "gpt-4o-mini",
    ) -> None:
        self.api_key_env = api_key_env
        self.base_url = base_url
        self.default_model = default_model

    def complete(
        self,
        messages: list[dict[str, str]],
        tools: list[dict[str, Any]] | None = None,
        *,
        model: str | None = None,
        temperature: float = 0.0,
        tool_choice: Any | None = None,
    ) -> ModelResponse:
        try:
            from openai import OpenAI
        except ImportError as exc:
            raise RuntimeError("Install live provider dependency first: pip install openai") from exc

        api_key = os.getenv(self.api_key_env)
        if not api_key:
            raise RuntimeError(f"Missing API key env var: {self.api_key_env}")

        client = OpenAI(api_key=api_key, base_url=self.base_url)
        system_parts = [
            str(message.get("content", ""))
            for message in messages
            if message.get("role") == "system"
        ]
        input_messages = [
            {
                "role": "assistant" if message.get("role") == "assistant" else "user",
                "content": str(message.get("content", "")),
            }
            for message in messages
            if message.get("role") != "system"
        ]
        response_tools = []
        for item in tools or []:
            function = item.get("function", item)
            response_tools.append({
                "type": "function",
                "name": function["name"],
                "description": function.get("description", ""),
                "parameters": function.get("parameters", {"type": "object", "properties": {}}),
                "strict": False,
            })
        kwargs: dict[str, Any] = {
            "model": model or self.default_model,
            "input": input_messages,
        }
        if system_parts:
            kwargs["instructions"] = "\n\n".join(system_parts)
        if response_tools:
            kwargs["tools"] = response_tools
        if tool_choice is not None:
            kwargs["tool_choice"] = tool_choice
        selected_model = model or self.default_model
        if selected_model.startswith("gpt-5.6"):
            kwargs["reasoning"] = {"effort": "low"}
            kwargs["text"] = {"verbosity": "low"}
        else:
            kwargs["temperature"] = temperature

        resp = client.responses.create(**kwargs)
        calls: list[ToolCall] = []
        seen_tool_names: set[str] = set()
        for item in resp.output or []:
            if getattr(item, "type", None) != "function_call":
                continue
            name = getattr(item, "name")
            # One model response represents one active intent. Avoid redundant
            # calls to the same tool with slightly different defaults.
            if name in seen_tool_names:
                continue
            seen_tool_names.add(name)
            args = json.loads(getattr(item, "arguments", "") or "{}")
            calls.append(ToolCall(name=name, args=args))
        return ModelResponse(text=resp.output_text or None, tool_calls=calls, raw=resp)
