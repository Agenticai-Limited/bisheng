from langchain_aws import ChatBedrockConverse


class CustomChatBedrock(ChatBedrockConverse):
    """Custom wrapper for AWS Bedrock ChatModel via Converse API.

    Uses ChatBedrockConverse which supports streaming, tool calling,
    and all Bedrock foundation models through the unified Converse API.
    """
    pass
