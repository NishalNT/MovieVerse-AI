from typing import List, Dict, Any, Optional, TypedDict
from datetime import datetime

class AgentState(TypedDict):
    messages: List[Dict[str, str]]
    conversation_id: str
    current_query: str
    tools_to_use: List[str]
    tool_results: Dict[str, Any]
    final_response: Optional[str]
    error: Optional[str]
    extracted_params: Optional[Dict[str, str]]