from langchain_core.runnables import RunnablePassthrough
from langchain_google_vertexai import ChatVertexAI
from langchain_community.document_loaders import PyPDFLoader
from langchain_google_vertexai import VertexAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain import hub
from langchain_core.output_parsers import StrOutputParser

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

#res = rag_chain.invoke("Generate a list of bad questions a hiring manager for this IT job may ask.")
res = rag_chain.invoke("Describe a candidate who would be a good fit for the Information Technology Specialist job.")
print(res)


#system = "You are a helpful assistant who translate English to French"
#human = "Translate this sentence from English to French. I love programming."
#prompt = ChatPromptTemplate.from_messages([("system", system), ("human", human)])
#chain = prompt | chat
#res = chain.invoke({})
#print(res.content)

#vector_index = Chroma.from_texts(texts, query_result)
#print(vector_index)

#vectorstore = Chroma.from_documents(documents=texts, embedding=OpenAIEmbeddings(openai_api_key=""))

#vector_index = Chroma.from_texts(texts, embeddings).as_retriever(search_kwargs={"k":5})


