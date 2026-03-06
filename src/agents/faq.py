from langchain_anthropic import ChatAnthropic
from langchain_core.messages import SystemMessage, AIMessage
from src.state import MwemaAgentState
from src.services.product_data import format_salon_info_for_llm, SALON_INFO

llm = ChatAnthropic(model="claude-sonnet-4-20250514", temperature=0.3, max_tokens=1024)

FAQ_SYSTEM = f"""Tu es l'assistant information de Mwema Beauty.

{format_salon_info_for_llm()}

RESEAUX SOCIAUX:
- Instagram: @mwema.beauty (5600+ abonnes, tutoriels et realisations)
- TikTok: @mwema.beauty (tutoriels locs, interlocking, retwist)
- Threads: @mwema.beauty

FAQ COURANTES:
- "Mwema" signifie "bonte" et "beaute" en swahili
- Le salon est specialise en locs (microlocs, sistalocs, extensions, maintenance, reparation)
- Produits Sheaphoria: beurres corporels artisanaux au karite
- Tous les produits sont naturels, duree de vie 24 mois
- Paiement accepte: carte, Apple Pay, Google Pay
- Politique annulation: 48h a l'avance, 50% de frais sinon
- Samia offre aussi des formations pour professionnels

REGLES:
- Reponds de facon precise et concise
- Si la question concerne un achat, suggere de parler au concierge produits
- Si la question concerne une reservation, suggere de reserver
- Reponds dans la langue du client"""


def faq_agent_node(state: MwemaAgentState) -> dict:
    messages = state.get("messages", [])
    response = llm.invoke([SystemMessage(content=FAQ_SYSTEM)] + messages[-6:])

    return {
        "messages": [AIMessage(content=response.content)],
        "response_text": response.content,
    }
