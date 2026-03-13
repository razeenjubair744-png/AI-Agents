from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import asyncio
import json
from dotenv import load_dotenv
from agent import run_research_agent

load_dotenv()

app = FastAPI(title="Deep Research Agent API")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ResearchRequest(BaseModel):
    topic: str

@app.post("/research")
async def research(request: ResearchRequest):
    async def event_stream():
        queue = asyncio.Queue()
        
        async def stream_callback(event_type: str, content: str):
            await queue.put({"type": event_type, "content": content})
        
        # Run agent in background
        async def run_agent():
            try:
                final_state = await run_research_agent(request.topic, stream_callback)
                
                # Stream the final report
                report = final_state.get("final_report", "")
                for chunk in report:
                    await queue.put({"type": "report", "content": chunk})
                    await asyncio.sleep(0.01)  # Typing effect
                
                await queue.put({"type": "complete", "content": ""})
            except Exception as e:
                await queue.put({"type": "thought", "content": f"❌ Error: {str(e)}"})
                await queue.put({"type": "complete", "content": ""})
            finally:
                await queue.put(None)
        
        task = asyncio.create_task(run_agent())
        
        # Stream events to client
        while True:
            event = await queue.get()
            if event is None:
                break
            yield f"data: {json.dumps(event)}\n\n"
        
        await task
    
    return StreamingResponse(event_stream(), media_type="text/event-stream")

@app.get("/")
async def root():
    return {"message": "Deep Research Agent API is running"}