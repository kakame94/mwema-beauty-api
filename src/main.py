from fastapi import FastAPI, HTTPException, Query, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel
from contextlib import asynccontextmanager
import uuid

from src.config import settings
from src.schemas import WhatsAppWebhookPayload
from src.graph import create_mwema_graph
from src.services.product_data import PRODUCTS, SERVICES, SALON_INFO
from langchain_core.messages import HumanMessage


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Mwema Beauty AI Starting up...")
    app.state.graph = create_mwema_graph()
    yield
    print("Shutting down...")


app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL, "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Health ---

@app.get("/health")
async def health_check():
    return {"status": "ok", "version": "0.2.0"}


# --- Chat API (Website) ---

class ChatRequest(BaseModel):
    message: str
    thread_id: str | None = None

class ChatResponse(BaseModel):
    response: str
    thread_id: str
    checkout_url: str | None = None


@app.post("/api/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    thread_id = req.thread_id or str(uuid.uuid4())

    initial_state = {
        "messages": [HumanMessage(content=req.message)],
        "thread_id": thread_id,
        "user_id": thread_id,
    }

    result = await app.state.graph.ainvoke(initial_state)

    return ChatResponse(
        response=result.get("response_text", "Desolee, je n'ai pas compris."),
        thread_id=thread_id,
        checkout_url=result.get("checkout_url"),
    )


# --- Products & Services API ---

@app.get("/api/products")
async def list_products(category: str | None = None):
    if category:
        return [p for p in PRODUCTS if p["category"] == category]
    return PRODUCTS


@app.get("/api/services")
async def list_services(category: str | None = None):
    if category:
        return [s for s in SERVICES if s["category"] == category]
    return SERVICES


@app.get("/api/salon")
async def salon_info():
    return SALON_INFO


# --- WhatsApp Webhook (preserved) ---

@app.get("/webhook/whatsapp")
async def verify_whatsapp_webhook(
    mode: str = Query(alias="hub.mode"),
    token: str = Query(alias="hub.verify_token"),
    challenge: str = Query(alias="hub.challenge"),
):
    if mode and token:
        if mode == "subscribe" and token == settings.WHATSAPP_VERIFY_TOKEN:
            return PlainTextResponse(content=challenge, status_code=200)
        else:
            raise HTTPException(status_code=403, detail="Verification failed")
    return HTTPException(status_code=400, detail="Missing parameters")


async def process_whatsapp_message(payload: WhatsAppWebhookPayload, graph):
    try:
        entry = payload.entry[0]
        changes = entry.changes[0]
        value = changes.value
        if value.messages:
            message = value.messages[0]
            if message.type == "text":
                user_text = message.text.body
                sender_id = message.from_
                initial_state = {
                    "messages": [HumanMessage(content=user_text)],
                    "thread_id": sender_id,
                    "user_id": sender_id,
                }
                result = await graph.ainvoke(initial_state)
                response = result.get("response_text")
                print(f"WhatsApp AI Response for {sender_id}: {response}")
                # TODO: Send response back via Meta API
    except Exception as e:
        print(f"Error processing webhook: {e}")


@app.post("/webhook/whatsapp")
async def receive_whatsapp_webhook(
    payload: WhatsAppWebhookPayload, background_tasks: BackgroundTasks
):
    background_tasks.add_task(process_whatsapp_message, payload, app.state.graph)
    return {"status": "received"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True)
