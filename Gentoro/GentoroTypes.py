from enum import Enum
from typing import List, Optional, Union
from pydantic import BaseModel

class Providers(str, Enum):
    OPENAI = 'openai'
    ANTHROPIC = 'anthropic'
    OPENAI_ASSISTANTS = 'openai_assistants'
    VERCEL = 'vercel'
    GENTORO = 'gentoro'
    LANGCHAIN = 'langchain'

class AuthenticationScope(str, Enum):
    METADATA = 'metadata'
    API_KEY = 'api_key'

class BaseObject(BaseModel):
    pass

class ScopeForMetadata(BaseObject):
    key_name: str

class Authentication(BaseObject):
    scope: AuthenticationScope
    metadata: Optional[ScopeForMetadata]

class SdkConfig(BaseObject):
    base_url: Optional[str] = None
    auth_mod_base_url: Optional[str] = None
    timeout_ms: Optional[int] = 30000
    api_key: Optional[str] = None
    provider: Optional[Providers] = Providers.GENTORO
    authentication: Optional[Authentication] = Authentication(scope=AuthenticationScope.API_KEY, metadata=None)

class Request(BaseObject):
    uri: str
    content: BaseObject

class Response(BaseObject):
    content: BaseObject

class Message(BaseObject):
    role: str
    content: str

class Context(BaseObject):
    bridge_uid: str
    messages: Optional[List[Message]]

class KeyValuePair(BaseObject):
    key: str
    value: str

class GetToolsRequest(BaseObject):
    context: Context
    metadata: List[KeyValuePair]

class FunctionParameter(BaseObject):
    name: str
    type: str
    description: str

class FunctionParameterCollection(BaseObject):
    properties: List[FunctionParameter]
    required: List[str]

class Function(BaseObject):
    name: str
    description: str
    parameters: FunctionParameterCollection

class ToolDef(BaseObject):
    type: str
    definition: Function

class GetToolsResponse(BaseObject):
    tools: List[ToolDef]

class TextContent(BaseObject):
    text: str

class NumberContent(BaseObject):
    number: float

class BoolContent(BaseObject):
    flag: bool

class DataType(str, Enum):
    STRING = 'string'
    NUMBER = 'number'
    OBJECT = 'object'
    BOOLEAN = 'boolean'
    ARRAY = 'array'

class DataValue(BaseObject):
    field_name: str
    data_type: DataType
    value: Union[TextContent, NumberContent, BoolContent]

class ArrayContent(BaseObject):
    entries: List[DataValue]

class ObjectContent(BaseObject):
    object: DataValue

class AuthenticationData(BaseObject):
    type: str
    connection_uid: str
    tool_call_id: str
    request_uid: str
    request_secret: str
    values: List[DataValue]

class FunctionCall(BaseObject):
    name: str
    arguments: str

class ToolCall(BaseObject):
    id: str
    type: str
    details: FunctionCall

class RunToolsRequest(BaseObject):
    context: Context
    authentication: Authentication
    metadata: List[KeyValuePair]
    tool_calls: List[ToolCall]

class ExecResultType(str, Enum):
    EXEC_OUTPUT = 'output'
    ERROR = 'error'
    AUTH_REQUEST = 'auth_request'

class ExecOutput(BaseObject):
    content_type: str
    content: str

class ExecError(BaseObject):
    code: str
    message: str
    details: str

class AuthSchemaField(BaseObject):
    name: str
    description: str
    data_type: DataType
    fields: Optional[dict]

class AuthSchema(BaseObject):
    fields: List[AuthSchemaField]

class AuthenticationType(str, Enum):
    OAUTH = 'oauth'
    BASIC = 'basic'
    KEYPAIR = 'keypair'
    KEY = 'key'
    API_KEY = 'apikey'
    JWT = 'jwt'
    UNKNOWN = 'unknown'

class AuthRequest(BaseObject):
    connection_uid: str
    request_uid: str
    request_secret: str
    type: AuthenticationType
    settings: Optional[List[KeyValuePair]]
    schema: Optional[AuthSchema]

class AuthRequests(BaseObject):
    requests: List[AuthRequest]

class ExecResult(BaseObject):
    type: ExecResultType
    tool_call_id: str
    tool_uid: Optional[str]
    data: Union[ExecOutput, ExecError, AuthRequests]

class RunToolsResponse(BaseObject):
    results: List[ExecResult]

class SdkError(BaseObject):
    code: str
    message: str
    details: str

class SdkEventType(str, Enum):
    AUTHENTICATION_REQUEST = 'authentication_request'

class AuthenticationStatus(str, Enum):
    REQUESTED = 'requested'
    AUTHENTICATED = 'authenticated'
    EXPIRED = 'expired'
    ERROR = 'error'

class SdkAuthenticationEventInfo(BaseObject):
    tool_call_id: str
    tool_uid: str
    auth_request: AuthRequest

class SdkEvent(BaseObject):
    event_type: SdkEventType
    sdk: dict
    event_info: Union[SdkAuthenticationEventInfo]

class GetAuthStatusRequest(BaseObject):
    connection_uid: str
    request_uid: str
    request_secret: str

class AuthStatusSuccess(BaseObject):
    type: AuthenticationType
    authenticated_at: float

class AuthStatusError(BaseObject):
    code: str
    message: str
    stack_trace: str

class GetAuthStatusResponse(BaseObject):
    result: AuthenticationStatus
    info: Optional[Union[AuthStatusError, AuthStatusSuccess]]

