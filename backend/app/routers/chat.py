from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db.database import get_db
from app.models.conversation import Conversation
from app.models.message import Message
from app.models.user import User
from app.schemas.chat import ConversationCreate, ConversationResponse, ChatRequest
from app.services.rag import search_relevant_cards, format_cards_for_prompt
from app.services.chat import stream_chat_response, build_messages
from app.routers.auth import get_current_user
import json

router = APIRouter(prefix="/chat", tags=["chat"])

@router.post("/conversations", response_model=ConversationResponse)
async def create_conversation(
    body: ConversationCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    conversation = Conversation(user_id=current_user.id, title=body.title)
    db.add(conversation)
    await db.commit()
    await db.refresh(conversation)
    return conversation

@router.get("/conversations", response_model=list[ConversationResponse])
async def get_conversations(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(
        select(Conversation)
        .where(Conversation.user_id == current_user.id)
        .order_by(Conversation.created_at.desc())
    )
    return result.scalars().all()

@router.post("/message")
async def send_message(
    body: ChatRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await deb.execute(
        select(Conversation).where(
            Conversation.id == body.conversation.id,
            Conversation.user_id == current_user.id
        )
    )

    conversation = result.scalars().first()
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    history_result = await db.execute(
        select(Message)
        .where(Message.conversation_id == conversation.id)
        .order_by(Message.created_at.asc())
    )
    history = [
        {"role": m.role, "content": m.content}
        for m in history_result.scalars().all()
    ]

    cards = await search_relevant_cards(nody.message, db)
    card_context = format_cards_for_prompt(cards)

    user_message = Message(
        conversation_id=body.conversation_id,
        role="user",
        content=body.message
    )
    db.add(user_message)
    await db.commit()

    messages = build_messages(history, body.message, card_context)

    full_response = []

    async def generate():
        async for chunk in stream_chat_response(messages):
            full_response.append(chunk)
            yield chunk

        assistant_message = Message(
            conversation_id=body.conversation_id,
            role="assistant",
            content="".join(full_response)
        )
        db.add(assistant_message)
        await db.commit()
    return StreamingResponse(generate(), media_type="text/plain")