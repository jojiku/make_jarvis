 
from src.utils.config import DB_PARAMS
from src.db.database import DatabaseHandler    
from langchain.prompts import (
    ChatPromptTemplate,
    MessagesPlaceholder,
)
from langchain.chains import LLMChain
from langchain.memory import ConversationBufferMemory
from langchain_community.chat_message_histories import (
    PostgresChatMessageHistory,
)
from langchain_groq import ChatGroq 
from src.model.system_prompt import russian_persona, uwu_persona

prompt = ChatPromptTemplate.from_messages([ 
        ("system",  uwu_persona),

        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}")
    ])


class ConversationHandler:

    def __init__(self):

        try:
            self.db_handler = DatabaseHandler(**DB_PARAMS)
        except Exception as e:
            print(f"Failed to connect to database: {e}")
            raise

    def handle_conversation(self, user_name: str, new_question: str) -> str:
         
        try:
            history = self.db_handler.get_user_history(user_name)
            history_reversed = history[::-1]
            messages = [{'role': 'user', 'content': item['message_sent']} for item in history_reversed]
            messages.append({'role': 'user', 'content': new_question})

            llm = ChatGroq(temperature=0,  
               groq_api_key='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',
               model_name='llama3-70b-8192',
               max_tokens=20000,
               streaming=True)
            
            
            history = PostgresChatMessageHistory(
                connection_string="postgresql://db_user:new@localhost:5432/postgres",
                session_id= str(user_name)
            )
            

            memory = ConversationBufferMemory(
                memory_key="chat_history",
                return_messages=True,
                chat_memory=history,
            )
          
            if new_question in {'new', 'reset', 'restart', 'New'}:
                memory.clear()

            chain = LLMChain(
                llm=llm,
                prompt=prompt,
                verbose=True,
                memory=memory
            )
            input_data = {"input": messages[-1]['content']}
            response_text = chain.invoke(str(input_data)) 
            self.db_handler.insert_conversation(user_name, new_question, response_text["text"])
            


        except Exception as e:
            print(f"Failed during conversation handling: {e}")
            return "Sorry, I encountered an error while processing your request."

        return response_text
    
    def clear_user_history(self, user_id: str) -> str:
        try:
            self.db_handler.clear_user_history(user_id)
            
            return "I've successfully forgotten our previous interactions 😊 *bows* Reply with 'new' to me please"
        except Exception as e:
            print(f"Failed during clearing history for {user_id}: {e}")
            return "Failed to clear your history due to an internal error."