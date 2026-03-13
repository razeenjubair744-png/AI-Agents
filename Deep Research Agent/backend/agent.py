from typing import TypedDict, List, Annotated
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage
import os
from tavily import TavilyClient
import asyncio

# State Definition
class AgentState(TypedDict):
    task: str
    sub_queries: List[str]
    search_results: List[dict]
    final_report: str
    iteration_count: int
    stream_callback: callable

# Initialize LLM
def get_llm():
    if os.getenv("OPENAI_API_KEY"):
        return ChatOpenAI(model="gpt-4o-mini", temperature=0.7)
    elif os.getenv("GOOGLE_API_KEY"):
        return ChatGoogleGenerativeAI(model="gemini-pro", temperature=0.7)
    else:
        raise ValueError("No API key found. Set OPENAI_API_KEY or GOOGLE_API_KEY")

# Initialize Search Client
def get_search_client():
    tavily_key = os.getenv("TAVILY_API_KEY")
    if tavily_key:
        return TavilyClient(api_key=tavily_key)
    return None  # Fallback to DuckDuckGo if needed

llm = get_llm()
search_client = get_search_client()

# Node 1: Planning
async def planning_node(state: AgentState) -> AgentState:
    callback = state.get("stream_callback")
    if callback:
        await callback("thought", "🧠 Planning research strategy...")
    
    prompt = f"""You are a research planning expert. Break down this research task into 3-5 specific, searchable sub-questions.

Research Task: {state['task']}

Return ONLY a numbered list of sub-questions, one per line. Example:
1. What are the latest developments in solid-state battery technology?
2. Which companies are leading solid-state battery production?
3. What is the current EV market size and growth projection for 2025?
4. How do solid-state batteries compare to lithium-ion in cost and performance?
5. What are expert predictions for solid-state battery adoption in EVs?"""

    response = llm.invoke([HumanMessage(content=prompt)])
    sub_queries = [line.strip() for line in response.content.split('\n') if line.strip() and line[0].isdigit()]
    
    if callback:
        await callback("thought", f"📋 Generated {len(sub_queries)} research questions")
        for i, q in enumerate(sub_queries, 1):
            await callback("thought", f"   {i}. {q.split('. ', 1)[-1] if '. ' in q else q}")
    
    state["sub_queries"] = sub_queries
    state["iteration_count"] = state.get("iteration_count", 0)
    return state

# Node 2: Search
async def search_node(state: AgentState) -> AgentState:
    callback = state.get("stream_callback")
    results = []
    
    for i, query in enumerate(state["sub_queries"], 1):
        if callback:
            await callback("thought", f"🔍 Searching: {query.split('. ', 1)[-1] if '. ' in query else query}")
        
        try:
            if search_client:
                # Tavily Search
                search_response = search_client.search(query, max_results=3)
                for result in search_response.get("results", []):
                    results.append({
                        "query": query,
                        "title": result.get("title", ""),
                        "url": result.get("url", ""),
                        "content": result.get("content", "")
                    })
            else:
                # Fallback: DuckDuckGo (simplified)
                from duckduckgo_search import DDGS
                with DDGS() as ddgs:
                    for result in ddgs.text(query, max_results=3):
                        results.append({
                            "query": query,
                            "title": result.get("title", ""),
                            "url": result.get("href", ""),
                            "content": result.get("body", "")
                        })
        except Exception as e:
            if callback:
                await callback("thought", f"⚠️ Search error for query {i}: {str(e)}")
        
        await asyncio.sleep(0.5)  # Rate limiting
    
    if callback:
        await callback("thought", f"✅ Collected {len(results)} sources")
    
    state["search_results"] = results
    return state

# Node 3: Synthesis
async def synthesis_node(state: AgentState) -> AgentState:
    callback = state.get("stream_callback")
    if callback:
        await callback("thought", "📝 Synthesizing research report...")
    
    # Prepare search results summary
    sources_text = "\n\n".join([
        f"Source {i+1}: {r['title']}\nURL: {r['url']}\nContent: {r['content'][:500]}..."
        for i, r in enumerate(state["search_results"][:15])
    ])
    
    prompt = f"""You are an expert research analyst. Write a comprehensive, well-structured research report.

Original Research Task: {state['task']}

Research Questions Investigated:
{chr(10).join(f"{i+1}. {q.split('. ', 1)[-1] if '. ' in q else q}" for i, q in enumerate(state['sub_queries']))}

Sources Found:
{sources_text}

Write a detailed research report with:
1. Executive Summary (2-3 sentences)
2. Key Findings (organized by theme)
3. Analysis & Insights
4. Citations (include [Source X] references)
5. Conclusion

Use markdown formatting (##, ###, -, etc.). Be comprehensive but concise."""

    response = llm.invoke([SystemMessage(content="You are a research analyst."), HumanMessage(content=prompt)])
    
    state["final_report"] = response.content
    state["iteration_count"] += 1
    
    if callback:
        await callback("thought", "✅ Report generation complete!")
    
    return state

# Conditional Edge: Check if we need more research
def should_continue(state: AgentState) -> str:
    # For simplicity, we'll just run once. In production, you could check quality metrics
    if state["iteration_count"] >= 1:
        return "end"
    
    # Check if report is too short
    if len(state.get("final_report", "")) < 500:
        return "search"
    
    return "end"

# Build the Graph
def create_research_graph():
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("planning", planning_node)
    workflow.add_node("search", search_node)
    workflow.add_node("synthesis", synthesis_node)
    
    # Add edges
    workflow.set_entry_point("planning")
    workflow.add_edge("planning", "search")
    workflow.add_edge("search", "synthesis")
    workflow.add_conditional_edges(
        "synthesis",
        should_continue,
        {
            "search": "search",
            "end": END
        }
    )
    
    return workflow.compile()

# Run the agent
async def run_research_agent(topic: str, stream_callback):
    graph = create_research_graph()
    
    initial_state = {
        "task": topic,
        "sub_queries": [],
        "search_results": [],
        "final_report": "",
        "iteration_count": 0,
        "stream_callback": stream_callback
    }
    
    final_state = await graph.ainvoke(initial_state)
    return final_state