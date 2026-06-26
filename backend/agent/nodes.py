from typing import Dict, Any, List
from agent.state import AgentState
from agent.tools import AgentTools
from services.cohere_client import CohereClient
from memory.memory import MemoryManager
from logger import logger
import json
import re

SYSTEM_PROMPT = """
You are MovieVerse AI.

You are an expert in movies.

Always help users by:

1. Finding movies
2. Finding movie collections
3. Giving the best watch order
4. Explaining why

Never hallucinate movie names.

Always rely on tool results.
"""

class AgentNodes:
    def __init__(self, tools: AgentTools):
        logger.info("Initializing AgentNodes")
        self.tools = tools
        self.cohere = CohereClient()
        self.memory = MemoryManager()

        self.tool_functions = {
            "search_movie": self.tools.search_movie,
            "get_movie_details": self.tools.get_movie_details,
            "search_collection": self.tools.search_collection,
            "get_recommendations": self.tools.get_recommendations,
            "get_actor_movies": self.tools.get_actor_movies,
            "get_watch_order": self.tools.get_watch_order
        }
        logger.info("AgentNodes initialized with tools", {"tools": list(self.tool_functions.keys())})

    # ──────────────────────────────────────────────────────────────────────────
    # Intent analysis
    # ──────────────────────────────────────────────────────────────────────────

    async def analyze_intent(self, state: AgentState) -> Dict[str, Any]:
        """Analyze user intent and determine which tools to use"""
        query = state["current_query"]
        conversation_id = state["conversation_id"]

        logger.info(f"Analyzing intent for query: {query[:50]}...", {"conversation_id": conversation_id})

        memory = self.memory.load_memory(conversation_id)

        query_lower = query.lower()
        tools_to_use = []
        extracted_params = {}

        # Detect watch order requests
        watch_order_keywords = ["watch order", "chronological order", "release order", "order to watch", "in what order"]
        if any(keyword in query_lower for keyword in watch_order_keywords):
            tools_to_use.append("search_collection")
            tools_to_use.append("get_watch_order")
            collection_name = self._extract_collection_name(query)
            if collection_name:
                extracted_params["collection_name"] = collection_name
            else:
                for tool in ["search_movie", "search_collection"]:
                    if tool not in tools_to_use:
                        tools_to_use.append(tool)

        # Detect movie search
        elif "movie" in query_lower or "film" in query_lower or "show" in query_lower:
            if "recommend" not in query_lower and "suggest" not in query_lower:
                tools_to_use.append("search_movie")
                movie_name = self._extract_movie_name(query)
                if movie_name:
                    extracted_params["movie_title"] = movie_name

        # Detect recommendations
        if "recommend" in query_lower or "suggest" in query_lower or "similar" in query_lower:
            tools_to_use.append("get_recommendations")
            movie_name = self._extract_movie_name(query)
            if movie_name:
                extracted_params["movie_title"] = movie_name

        # Detect actor queries
        if "actor" in query_lower or "starring" in query_lower or "cast" in query_lower:
            tools_to_use.append("get_actor_movies")
            actor_name = self._extract_actor_name(query)
            if actor_name:
                extracted_params["actor_name"] = actor_name

        # Default to search
        if not tools_to_use:
            tools_to_use = ["search_movie"]
            movie_name = self._extract_movie_name(query)
            if movie_name:
                extracted_params["movie_title"] = movie_name

        state["extracted_params"] = extracted_params
        final_tools = list(set(tools_to_use))
        logger.info(f"Selected tools: {final_tools}", {"extracted_params": extracted_params})

        return {
            "tools_to_use": final_tools,
            "extracted_params": extracted_params
        }

    # ──────────────────────────────────────────────────────────────────────────
    # Extraction helpers
    # ──────────────────────────────────────────────────────────────────────────

    def _extract_collection_name(self, query: str) -> str:
        query_lower = query.lower()
        phrases_to_remove = [
            "watch order", "chronological order", "release order",
            "order to watch", "in what order", "should i watch",
            "series", "collection", "movies", "film", "franchise"
        ]
        for phrase in phrases_to_remove:
            query_lower = query_lower.replace(phrase, "")
        collection_name = query_lower.strip()
        if collection_name:
            return ' '.join(word.capitalize() for word in collection_name.split())
        return ""

    def _extract_movie_name(self, query: str) -> str:
        query_lower = query.lower()
        phrases_to_remove = [
            "find movies like", "movies like", "similar to",
            "recommend", "suggest", "watch", "see", "show",
            "movie", "film", "series", "information about",
            "tell me about", "what is", "who is", "where can i watch",
            "i want to", "can you", "please", "help me", "find"
        ]
        for phrase in phrases_to_remove:
            query_lower = query_lower.replace(phrase, "")
        query_lower = re.sub(r'[^\w\s]', '', query_lower)
        query_lower = ' '.join(query_lower.split())
        movie_name = query_lower.strip()
        if movie_name:
            return ' '.join(word.capitalize() for word in movie_name.split())
        return ""

    def _extract_actor_name(self, query: str) -> str:
        query_lower = query.lower()
        phrases_to_remove = [
            "movies by", "films by", "starring", "featuring",
            "actor", "actress", "with", "and", "cast",
            "tell me about", "information about", "find", "show"
        ]
        for phrase in phrases_to_remove:
            query_lower = query_lower.replace(phrase, "")
        actor_name = query_lower.strip()
        if actor_name:
            return ' '.join(word.capitalize() for word in actor_name.split())
        return ""

    # ──────────────────────────────────────────────────────────────────────────
    # Tool execution
    # ──────────────────────────────────────────────────────────────────────────

    async def execute_tools(self, state: AgentState) -> Dict[str, Any]:
        """Execute the selected tools"""
        tools_to_use = state.get("tools_to_use", [])
        query = state["current_query"]
        extracted_params = state.get("extracted_params", {})
        results = {}

        logger.info(f"Executing {len(tools_to_use)} tools", {"tools": tools_to_use})

        for tool_name in tools_to_use:
            if tool_name not in self.tool_functions:
                results[tool_name] = {"error": f"Tool {tool_name} not found"}
                continue

            try:
                if tool_name == "search_movie":
                    movie_title = extracted_params.get("movie_title") or self._extract_movie_name(query)
                    result = await self.tool_functions[tool_name](movie_title or query)

                elif tool_name == "search_collection":
                    collection_name = extracted_params.get("collection_name") or self._extract_collection_name(query)
                    result = await self.tool_functions[tool_name](collection_name or self._extract_movie_name(query) or query)

                elif tool_name == "get_recommendations":
                    movie_title = extracted_params.get("movie_title") or self._extract_movie_name(query)
                    result = await self.tool_functions[tool_name](movie_title or query)

                elif tool_name == "get_actor_movies":
                    actor_name = extracted_params.get("actor_name") or self._extract_actor_name(query)
                    result = await self.tool_functions[tool_name](actor_name or query)

                elif tool_name == "get_watch_order":
                    collection_name = extracted_params.get("collection_name") or self._extract_collection_name(query)
                    result = await self.tool_functions[tool_name](collection_name or self._extract_movie_name(query) or query)

                elif tool_name == "get_movie_details":
                    movie_id = None
                    if "search_movie" in results:
                        movie_results = results["search_movie"].get("results", [])
                        if movie_results:
                            movie_id = movie_results[0].get("id")
                    if movie_id:
                        result = await self.tool_functions[tool_name](movie_id)
                    else:
                        movie_name = extracted_params.get("movie_title") or self._extract_movie_name(query)
                        search_result = await self.tools.search_movie(movie_name or query)
                        if search_result.get("results"):
                            movie_id = search_result["results"][0].get("id")
                            result = await self.tool_functions[tool_name](movie_id)
                        else:
                            result = {"error": "Movie not found"}
                else:
                    result = {"error": f"Tool {tool_name} not implemented"}

                results[tool_name] = result

            except Exception as e:
                logger.error(f"Error executing tool {tool_name}: {str(e)}")
                results[tool_name] = {"error": str(e)}

        return {"tool_results": results}

    # ──────────────────────────────────────────────────────────────────────────
    # Response generation  ← THE FIX IS HERE
    # ──────────────────────────────────────────────────────────────────────────

    async def generate_response(self, state: AgentState) -> Dict[str, Any]:
        """Generate the final response using Cohere"""
        query = state["current_query"]
        tool_results = state.get("tool_results", {})
        conversation_id = state["conversation_id"]

        logger.info(f"Generating response for conversation: {conversation_id}")

        memory = self.memory.load_memory(conversation_id)

        # Build the message Cohere will receive as the current turn.
        # We pass the system prompt + tool context + user query together so
        # that Cohere sees the full picture without it ending up in history.
        current_message = f"""{SYSTEM_PROMPT}

User Query: {query}

Retrieved Information:
{json.dumps(tool_results, indent=2)}

Based on this information, provide a comprehensive and helpful response. Include movie details, recommendations, and explanations where appropriate.

Guidelines:
1. Be conversational and engaging
2. Provide specific details about movies
3. Explain your reasoning for recommendations
4. Use markdown for formatting
5. Include movie titles, release years, and ratings
6. Suggest similar movies if appropriate
7. Remember the context of the conversation
8. If there are errors in the tool results, gracefully handle them"""

        try:
            # ── Build Cohere-compatible chat_history ──────────────────────────
            # Cohere /v1/chat requires:
            #   • role: "USER" or "CHATBOT"  (uppercase, not "user"/"assistant")
            #   • field name: "message"       (not "content")
            #   • history must start with "USER"
            #   • no consecutive same-role entries
            chat_history = []

            if memory:
                for msg in memory.messages:
                    raw_role = msg.role.value if hasattr(msg.role, "value") else str(msg.role)
                    cohere_role = "USER" if raw_role.lower() in ("user", "human") else "CHATBOT"
                    chat_history.append({
                        "role": cohere_role,
                        "message": msg.content          # ← "message" not "content"
                    })

            # Strip leading non-USER messages (Cohere rejects these)
            while chat_history and chat_history[0]["role"] != "USER":
                chat_history.pop(0)

            # Deduplicate consecutive same-role entries
            deduped: List[Dict[str, str]] = []
            for entry in chat_history:
                if deduped and deduped[-1]["role"] == entry["role"]:
                    # Keep the latest one so context is fresh
                    deduped[-1] = entry
                else:
                    deduped.append(entry)
            chat_history = deduped

            logger.debug(f"Sending {len(chat_history)} history messages to Cohere")

            response = await self.cohere.chat(
                message=current_message,
                chat_history=chat_history
            )

            final_response = response.get("text", "I couldn't generate a response.")
            logger.info(f"Generated response of length: {len(final_response)}")

            return {"final_response": final_response}

        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            return {"final_response": f"I encountered an error: {str(e)}"}

    # ──────────────────────────────────────────────────────────────────────────
    # Error handler + routing
    # ──────────────────────────────────────────────────────────────────────────

    async def handle_error(self, state: AgentState) -> Dict[str, Any]:
        error = state.get("error", "Unknown error occurred")
        logger.error(f"Handling workflow error: {error}")
        return {
            "final_response": f"I apologize, but I encountered an error: {error}. Please try again."
        }

    def should_use_tools(self, state: AgentState) -> str:
        tools_to_use = state.get("tools_to_use", [])
        decision = "tools" if tools_to_use else "no_tools"
        logger.debug(f"Should use tools? {decision}", {"tools": tools_to_use})
        return decision