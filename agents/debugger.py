import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import HumanMessage, AIMessage
from dotenv import load_dotenv

load_dotenv()

class DebuggerAgent:
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            google_api_key=os.getenv("GEMINI_API_KEY")
        )

    def chat_with_copilot(self, dossier_content, active_code, chat_history, user_message) -> str:
        """
        A unified conversational agent that acts as a Gemini/Claude style Code Co-pilot.
        """
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an elite AI Software Engineer and Kaggle Grandmaster acting as a Code Co-pilot.
            The developer is talking to you via a chat interface. They may ask you to review code, debug an error they pasted in the chat, or brainstorm a feature.

            --- COMPETITION DOSSIER REFERENCE ---
            {dossier}

            --- ACTIVE WORKSPACE CODE (UPLOADED FILE) ---
            ```python
            {code}
            ```
            
            Engage naturally. If they paste a stack trace in the chat, diagnose it against the active workspace code. If they ask for a review, analyze the code. Provide precise, actionable Python snippets when needed."""),
            MessagesPlaceholder(variable_name="history"),
            ("human", "{message}")
        ])

        chain = prompt | self.llm | StrOutputParser()
        
        formatted_history = []
        for msg in chat_history:
            if msg["role"] == "user":
                formatted_history.append(HumanMessage(content=msg["content"]))
            else:
                formatted_history.append(AIMessage(content=msg["content"]))

        response = chain.invoke({
            "dossier": dossier_content,
            "code": active_code if active_code else "No file uploaded currently.",
            "history": formatted_history,
            "message": user_message
        })
        
        return response