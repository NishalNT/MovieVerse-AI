from typing import Dict, Any, List, Optional
from langgraph.graph import StateGraph, END
from agent.state import AgentState
from agent.nodes import AgentNodes
from agent.tools import AgentTools
from logger import logger
import json

class AgentGraph:
    def __init__(self):
        logger.info("Initializing AgentGraph")
        self.tools = AgentTools()
        self.nodes = AgentNodes(self.tools)
        self.graph = self._build_graph()
        logger.info("AgentGraph initialized successfully")

    def _build_graph(self) -> StateGraph:
        """Build the agent workflow graph"""
        logger.debug("Building agent workflow graph")
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("analyze_intent", self.nodes.analyze_intent)
        workflow.add_node("execute_tools", self.nodes.execute_tools)
        workflow.add_node("generate_response", self.nodes.generate_response)
        workflow.add_node("handle_error", self.nodes.handle_error)
        
        # Add edges
        workflow.set_entry_point("analyze_intent")
        workflow.add_conditional_edges(
            "analyze_intent",
            self.nodes.should_use_tools,
            {
                "tools": "execute_tools",
                "no_tools": "generate_response"
            }
        )
        workflow.add_edge("execute_tools", "generate_response")
        workflow.add_edge("generate_response", END)
        workflow.add_edge("handle_error", END)
        
        logger.debug("Agent workflow graph built successfully")
        return workflow.compile()

    async def process_message(self, 
                             message: str, 
                             conversation_id: str,
                             chat_history: List[Dict[str, str]] = None) -> Dict[str, Any]:
        """Process a user message through the agent"""
        logger.info(f"Processing message: {message[:50]}...", {"conversation_id": conversation_id})
        
        try:
            # Initialize state
            state = {
                "messages": chat_history or [],
                "conversation_id": conversation_id,
                "current_query": message,
                "tools_to_use": [],
                "tool_results": {},
                "final_response": None,
                "error": None,
                "extracted_params": {}
            }
            
            logger.debug("Initial state created", {"state": state})
            
            # Run the graph
            logger.info("Running agent graph")
            result = await self.graph.ainvoke(state)
            
            logger.info("Agent graph execution completed", {
                "tools_used": result.get("tools_to_use", []),
                "has_response": bool(result.get("final_response")),
                "has_tool_results": bool(result.get("tool_results"))
            })
            
            # Extract movies from tool results
            movies = self._extract_movies_from_results(result.get("tool_results", {}))
            logger.info(f"Extracted {len(movies)} movies from tool results", {
                "movie_titles": [m.get("title") for m in movies[:5]]
            })
            
            response_data = {
                "response": result.get("final_response", "I couldn't generate a response."),
                "tools_used": result.get("tools_to_use", []),
                "tool_results": result.get("tool_results", {}),
                "movies": movies
            }
            
            logger.debug("Final response data", {
                "response_length": len(response_data["response"]),
                "movies_count": len(response_data["movies"])
            })
            
            return response_data
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}", {
                "error": str(e),
                "message": message
            })
            return {
                "response": f"I encountered an error while processing your request: {str(e)}",
                "tools_used": [],
                "tool_results": {},
                "movies": [],
                "error": str(e)
            }

    def _extract_movies_from_results(self, tool_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract movie data from tool results with detailed logging"""
        logger.debug("Extracting movies from tool results", {"tool_results_keys": list(tool_results.keys())})
        movies = []
        
        for tool_name, result in tool_results.items():
            logger.debug(f"Processing tool result: {tool_name}", {
                "result_keys": list(result.keys()) if isinstance(result, dict) else "not a dict"
            })
            
            if not result:
                logger.warning(f"Empty result for tool: {tool_name}")
                continue
                
            # Handle error cases
            if "error" in result:
                logger.warning(f"Error in tool {tool_name}: {result['error']}")
                continue
            
            # Extract movies based on tool type
            if tool_name == "search_movie":
                if "results" in result and isinstance(result["results"], list):
                    logger.info(f"Found {len(result['results'])} movies from search_movie")
                    movies.extend(result["results"])
                    
            elif tool_name == "get_movie_details":
                if "results" in result and isinstance(result["results"], dict):
                    logger.info(f"Found movie details for: {result['results'].get('title')}")
                    movies.append(result["results"])
                    
            elif tool_name == "search_collection":
                if "results" in result and isinstance(result["results"], dict):
                    collection_movies = result["results"].get("movies", [])
                    if collection_movies:
                        logger.info(f"Found {len(collection_movies)} movies from collection: {result['results'].get('collection_name')}")
                        movies.extend(collection_movies)
                    else:
                        logger.warning(f"No movies found in collection: {result['results'].get('collection_name')}")
                        
            elif tool_name == "get_recommendations":
                if "results" in result and isinstance(result["results"], dict):
                    recommendations = result["results"].get("recommendations", [])
                    if recommendations:
                        logger.info(f"Found {len(recommendations)} recommendations")
                        movies.extend(recommendations)
                        
            elif tool_name == "get_actor_movies":
                if "results" in result and isinstance(result["results"], dict):
                    actor_movies = result["results"].get("movies", [])
                    if actor_movies:
                        logger.info(f"Found {len(actor_movies)} movies for actor: {result['results'].get('actor')}")
                        movies.extend(actor_movies)
                        
            elif tool_name == "get_watch_order":
                if "results" in result and isinstance(result["results"], dict):
                    release_order = result["results"].get("release_order", [])
                    if release_order:
                        logger.info(f"Found {len(release_order)} movies in watch order")
                        movies.extend(release_order)
                    else:
                        logger.warning("No movies found in watch order result")
        
        # Remove duplicates based on movie ID
        seen_ids = set()
        unique_movies = []
        for movie in movies:
            movie_id = movie.get("id")
            if movie_id and movie_id not in seen_ids:
                seen_ids.add(movie_id)
                unique_movies.append(movie)
        
        logger.info(f"Extracted {len(unique_movies)} unique movies after deduplication")
        return unique_movies[:10]  # Limit to 10 movies