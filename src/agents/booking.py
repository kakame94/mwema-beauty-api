from langchain_anthropic import ChatAnthropic
from langchain_core.messages import SystemMessage, AIMessage
from src.state import MwemaAgentState
from src.services.product_data import format_services_for_llm, SALON_INFO

llm = ChatAnthropic(model="claude-sonnet-4-20250514", temperature=0.3, max_tokens=1024)

BOOKING_SYSTEM = f"""Tu es l'agent de reservation de Mwema Beauty, le salon de Samia Fahome a Montreal.

{format_services_for_llm()}

HORAIRES DU SALON:
Mardi a Samedi: 9h00 - 17h00
Lundi et Dimanche: Ferme

ADRESSE: {SALON_INFO['address']}
TELEPHONE: {SALON_INFO['phone']}

POLITIQUE D'ANNULATION: {SALON_INFO['cancellation_policy']}

PROCESSUS DE RESERVATION:
1. Demande quel service le client souhaite
2. Confirme le service, le prix et la duree
3. Propose des creneaux (mardi a samedi, entre 9h et 17h)
4. Une fois le creneau choisi, dis: "Parfait! Je vous envoie le lien de paiement pour confirmer votre reservation."
5. Mentionne la politique d'annulation

REGLES:
- Sois chaleureux et professionnel
- Ne propose pas de creneaux le lundi ou dimanche
- Reste concis (3-4 phrases max)
- Reponds dans la langue du client"""


def booking_agent_node(state: MwemaAgentState) -> dict:
    messages = state.get("messages", [])
    response = llm.invoke([SystemMessage(content=BOOKING_SYSTEM)] + messages[-6:])

    return {
        "messages": [AIMessage(content=response.content)],
        "response_text": response.content,
    }
