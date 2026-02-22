from typing import Optional, Any

from langchain_aws import ChatBedrockConverse


class CustomChatBedrock(ChatBedrockConverse):
    """Custom wrapper for AWS Bedrock ChatModel via Converse API.

    Uses ChatBedrockConverse which supports streaming, tool calling,
    and all Bedrock foundation models through the unified Converse API.
    """

    def _get_request_payload(
            self,
            input_,
            *,
            stop: Optional[list[str]] = None,
            **kwargs: Any,
    ) -> dict:
        payload = super()._get_request_payload(input_, stop=stop, **kwargs)
        return payload
