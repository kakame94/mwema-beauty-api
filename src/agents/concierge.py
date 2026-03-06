from langchain_anthropic import ChatAnthropic
from langchain_core.messages import SystemMessage, AIMessage
from src.state import MwemaAgentState
from src.services.product_data import (
    format_products_for_llm,
    format_services_for_llm,
    format_salon_info_for_llm,
)

llm = ChatAnthropic(model="claude-sonnet-4-20250514", temperature=0.3, max_tokens=1024)

SUPERVISOR_SYSTEM = """Tu es le concierge intelligent de Mwema Beauty, un salon de coiffure specialise dans les locs et les soins capillaires naturels a Montreal, fonde par Samia Fahome.

TON ROLE: Analyser le message du client et determiner l'intention principale.

INTENTIONS POSSIBLES:
- "buy" : Le client veut acheter un produit (beurre corporel, huile, spray)
- "book" : Le client veut reserver un service au salon (locs, tresses, coiffure, formation)
- "info" : Le client pose une question sur le salon (horaires, adresse, politique, ingredients)
- "general" : Salutation, conversation generale, ou demande qui ne rentre pas dans les autres categories

REPONDS UNIQUEMENT avec l'intention en un seul mot: buy, book, info, ou general.
Ne reponds rien d'autre que le mot d'intention."""


def supervisor_node(state: MwemaAgentState) -> dict:
    messages = state.get("messages", [])
    if not messages:
        return {"current_intent": "general"}

    response = llm.invoke([SystemMessage(content=SUPERVISOR_SYSTEM)] + messages[-3:])
    intent = response.content.strip().lower()

    if intent not in ("buy", "book", "info", "general"):
        intent = "general"

    return {"current_intent": intent}


GENERAL_SYSTEM = f"""Tu es le concierge de Mwema Beauty, chaleureux et professionnel.
Tu parles en francais par defaut mais tu t'adaptes a la langue du client.

{format_salon_info_for_llm()}

Tu es accueillant, tu connais bien les produits et services.
Si le client veut acheter un produit, recommande-lui et propose de l'aider.
Si le client veut reserver, propose les services disponibles.
Reste concis (2-3 phrases max). Utilise un ton professionnel mais chaleureux.
Ne mentionne jamais que tu es une IA. Tu es le concierge Mwema."""


def general_chat_node(state: MwemaAgentState) -> dict:
    messages = state.get("messages", [])
    response = llm.invoke([SystemMessage(content=GENERAL_SYSTEM)] + messages[-6:])
    return {
        "messages": [AIMessage(content=response.content)],
        "response_text": response.content,
    }
