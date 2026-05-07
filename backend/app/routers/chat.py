from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db.database import get_db
from app.core.limiter import limiter
from app.models.conversation import Conversation
from app.models.message import Message
from app.models.user import User
from app.schemas.chat import ConversationCreate, ConversationResponse, ChatRequest, MessageResponse
from app.services.rag import search_relevant_cards, format_cards_for_prompt
from app.services.chat import stream_chat_response, build_messages
from app.routers.auth import get_current_user
import json
import uuid

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

    # Auto-insert opening message
    opening_message = Message(
        conversation_id=conversation.id,
        role="assistant",
        content="Welcome to Commander's Counsel! ⚔️\n\nTo help you build the best deck, let's start with some context.\n\nWhat format are you playing — **Commander** or **Oathbreaker**?"
    )
    db.add(opening_message)
    await db.commit()

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
@limiter.limit("10/minute")
async def send_message(
    request: Request,
    body: ChatRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(
        select(Conversation).where(
            Conversation.id == body.conversation_id,
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

    cards = await search_relevant_cards(body.message, db)
    card_context = format_cards_for_prompt(cards)

    user_message = Message(
        conversation_id=body.conversation_id,
        role="user",
        content=body.message
    )
    db.add(user_message)
    await db.commit()

    # Build deck context string
    deck_context = ""
    if conversation.format:
        deck_context += f"Format: {conversation.format}\n"
    if conversation.commander_name:
        deck_context += f"Commander: {conversation.commander_name}\n"
    if conversation.signature_spell:
        deck_context += f"Signature Spell: {conversation.signature_spell}\n"

    # Build messages for Groq
    messages = build_messages(history, body.message, card_context, deck_context)

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

@router.get("/conversations/{conversation_id}/messages", response_model=list[MessageResponse])
async def get_messages(
    conversation_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(
        select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.user_id == current_user.id
        )
    )
    if not result.scalars().first():
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    messages = await db.execute(
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.asc())
    )
    return messages.scalars().all()

@router.patch("/conversations/{conversation_id}/context")
async def update_conversation_context(
    conversation_id: uuid.UUID,
    body: dict,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(
        select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.user_id == current_user.id
        )
    )
    conversation = result.scalars().first()
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    if "format" in body:
        conversation.format = body["format"]
    if "commander_name" in body:
        conversation.commander_name = body["commander_name"]
        conversation.title = f"{body['commander_name']} Deck"
    if "signature_spell" in body:
        conversation.signature_spell = body["signature_spell"]

    await db.commit()
    await db.refresh(conversation)
    return conversation

@router.patch("/conversations/{conversation_id}/title")
async def update_conversation_title(
    conversation_id: uuid.UUID,
    body: dict,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(
        select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.user_id == current_user.id
        )
    )
    conversation = result.scalars().first()
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    conversation.title = body.get("title", conversation.title)
    await db.commit()
    await db.refresh(conversation)
    return conversation

@router.delete("/conversations/{conversation_id}")
async def delete_conversation(
    conversation_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(
        select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.user_id == current_user.id
        )
    )
    conversation = result.scalars().first()
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    await db.delete(conversation)
    await db.commit()
    return {"message": "Conversation deleted"}