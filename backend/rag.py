from langchain_core.runnables import RunnablePassthrough
from langchain_google_vertexai import ChatVertexAI
from langchain_community.document_loaders import PyPDFLoader
from langchain_google_vertexai import VertexAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain import hub
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI() 
chat = ChatVertexAI(model_name="gemini-pro",temperature=0)
embeddings = VertexAIEmbeddings(model_name="textembedding-gecko")
text_splitter = RecursiveCharacterTextSplitter(chunk_size=10000, chunk_overlap=1000)

loader = PyPDFLoader("https://ursu.ca/wp-content/uploads/2021/03/Information-Technology-Spoecialist-job-description.pdf")
docs = loader.load()
splits = text_splitter.split_documents(docs)
vectorstore = Chroma.from_documents(documents=splits, embedding=VertexAIEmbeddings(model_name="textembedding-gecko"))
retriever = vectorstore.as_retriever(search_kwargs={"k":1})
prompt = hub.pull("rlm/rag-prompt")

def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

rag_chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | prompt
    | chat
    | StrOutputParser()
)
system = ""
human = "Translate this sentence from English to French. I love programming."
prompt = ChatPromptTemplate.from_messages([("system", system), ("human", human)])

#res = rag_chain.invoke("Generate a list of bad questions a hiring manager for this IT job may ask.")
res = rag_chain.invoke("Describe a candidate who would be a good fit for the Information Technology Specialist job.")
print(res)

class Item(BaseModel):
    posting: str | None = None



@app.post("/init/")
async def create_item(item: Item):
    system = """You are a interview helper specialist, and you are responsible for distinguishing between biased and non-biased interview questions. You will receive a bonus and vacation if you correctly classify each interview question as biased or non-biased.

    Here is the context (job posting) of the interview:
    *Start of job posting*
    Intern Developer - AI
    Huawei Technologies Canada Co., Ltd. · Ottawa, ON
    Our team has an immediate 3-month internship opening for a Developer.

    Responsibilities:

    Work closely with Senior team members on exciting research projects in optical network automation
    Write, refactor, debug, and test code to apply AI/ML algorithms to network optimization problems
    Run experiments and simulations to evaluate the performance of developed methods
    Prepare reports and presentations to communicate research outcomes

    Job requirements

    What you’ll bring to the team:

    Bachelor\'s degree student in Computer Science, Software Engineering or related program
    Solid knowledge of machine learning algorithms and deep learning models
    Strong programming and debugging skills using Python
    Familiarity and some experience with PyTorch framework
    Excellent analytical thinking, problem solving, and presentation skills
    Familiarity with Graph Neural Network (GNN) models and Reinforcement Learning (RL) algorithms is an asset
    Experience with TorchRL and/or PyG libraries is an asset
    Some knowledge of network routing and/or optimization problems is an asset
    *End of job posting*
    An interview question is considered biased if it is irrelevant to job requirements, stereotypes a candidate, assumes inequality, is inconsistent across candidates, leads the candidate to a specific answer, exhibits cultural bias, shows language or accent bias, or contains microaggressions.
    You should also be aware of affinity bias. This type of bias occurs when interviewers favor candidates with whom they share similarities, whether in looks, interests, backgrounds, or experiences, even if these aspects are irrelevant to the job\'s requirements.

    Here are some examples to illustrate:

    Question: \"Do you have children or plan to start a family soon?\"
    Result: Biased (Irrelevance to Job Requirements)

    Question: \"Can you describe your experience with managing large projects?\"
    Result: Non-Biased

    Question: \"As a woman, how would you handle working in a predominantly male environment?\"
    Result: Biased (Stereotyping)

    Question: \"How do you approach conflict resolution within a team?\"
    Result: Non-Biased

    Question: \"Will your disability hinder your ability to work long hours?\"
    Result: Biased (Assuming Inequality)

    Question: \"What strategies do you use to prioritize your tasks?\"
    Result: Non-Biased

    Question: Asking only older candidates: \"How do you feel about reporting to someone younger than you?\"
    Result: Biased (Inconsistency)

    Question: \"What are your career goals for the next five years?\"
    Result: Non-Biased

    Question: \"You\'re not planning to take any extended personal time soon, are you?\"
    Result: Biased (Leading Questions)

    Question: \"You\'re from Canada; can you handle the freedom/responsibility here?\"
    Result: Biased (Cultural Bias)

    Question: \"Can you give an example of a time when you overcame a significant challenge at work?\"
    Result: Non-Biased

    Question: \"Where did you learn to speak English?\"
    Result: Biased (Language or Accent Bias)

    Question: \"What is your approach to ensuring clear communication with your team?\"
    Result: Non-Biased

    Question: \"You\'re quite articulate for someone from your background.\"
    Result: Biased (Microaggressions)

    Question: \"We went to the same college, right? It\'s great to see alumni applying. How do you think our shared college experience has equipped you for this job?\"
    Result: Biased (Affinity)

    Question: \"Oh so you also like Soccer? That\'s great to hear, I\'m sure you will have great collaboration skills right?\"
    Result:"""

    human = "Translate this sentence from English to French. I love programming."





