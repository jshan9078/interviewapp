import redis
from flask_cors import CORS, cross_origin
from flask import Flask, jsonify
from langchain_core.runnables import RunnablePassthrough
from langchain_google_vertexai import ChatVertexAI
from langchain_community.document_loaders import PyPDFLoader
from langchain_google_vertexai import VertexAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain import hub
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from typing import List
from langchain_core.pydantic_v1 import BaseModel, Field, validator
from langchain.output_parsers import PydanticOutputParser

class Feedback(BaseModel):
    feedback_title: str = Field(description="performance rating")
    elaboration: str = Field(description="explanation for rating")

chat = ChatVertexAI(model_name="gemini-pro",convert_system_message_to_human=True,response_validation=False)


r = redis.Redis(
  host='redis-16096.c329.us-east4-1.gce.cloud.redislabs.com',
  port=16096,
  password='')


# Function that create the app 
def create_app(test_config=None ):
    # create and configure the app
    app = Flask(__name__)
    cors = CORS(app)
    app.config['CORS_HEADERS'] = 'Content-Type'

    
    @app.route('/retrieve')
    def retrieve():
        l = r.get(str.encode("counter")).decode("utf-8")
        return [r.get(str.encode("response"+str(int(l)-1))).decode("utf-8")]
        
    
    @app.route('/finish')
    def finish():
        arr=[]
        for key in r.keys("response*"):
            arr.append(r.get(key).decode("utf-8")) 
            r.delete(key)

        interviewdata = ' '.join(arr)
        system = "You are a helpful assistant who gives interviews feedback on their performance."
        human = f"Give a performance rating and feedback to this interviewer who had the following issues in their interview (not the interviewee): {interviewdata}" 
        prompt = ChatPromptTemplate.from_messages([("system", system), ("human", human)])
        chain = prompt | chat
        res = chain.invoke({})
        return res.content
        
     
    return app 

APP = create_app()

if __name__ == '__main__':
    APP.run(debug=True)
