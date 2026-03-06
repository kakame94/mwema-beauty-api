from langchain_anthropic import ChatAnthropic
from langchain_core.messages import SystemMessage, AIMessage
from src.state import MwemaAgentState
from src.services.product_data import format_products_for_llm

llm = ChatAnthropic(model="claude-sonnet-4-20250514", temperature=0.3, max_tokens=1024)

CATALOG_SYSTEM = f"""Tu es l'expert produits de Mwema Beauty. Tu aides les clients a choisir le bon produit.

{format_products_for_llm()}

REGLES:
- Recommande en fonction du type de peau/cheveux du client
- Sois enthousiaste mais honnete sur les produits
- Si le client veut acheter, confirme le produit et la quantite
- Termine en disant: "Je prepare votre commande! Souhaitez-vous ajouter autre chose?"
- Quand le client est pret, dis: "Parfait! Je vous envoie le lien de paiement."
- Reste concis (3-4 phrases max)
- Reponds dans la langue du client (francais par defaut)"""


def catalog_agent_node(state: MwemaAgentState) -> dict:
    messages = state.get("messages", [])
    response = llm.invoke([SystemMessage(content=CATALOG_SYSTEM)] + messages[-6:])

    return {
        "messages": [AIMessage(content=response.content)],
        "response_text": response.content,
    }
