from google.cloud import speech_v1p1beta1 as speech
import pyaudio
from six.moves import queue
from fastapi import FastAPI
from langchain_core.runnables import RunnablePassthrough
from langchain_google_vertexai import ChatVertexAI
from langchain_community.document_loaders import PyPDFLoader
from langchain_google_vertexai import VertexAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain import hub
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from fastapi.middleware.cors import CORSMiddleware
import redis

r = redis.Redis(
  host='redis-16096.c329.us-east4-1.gce.cloud.redislabs.com',
  port=16096,
  password='')

for key in r.keys("response*"):
    r.delete(key) 
r.set("counter", "0")

chat = ChatVertexAI(model_name="gemini-pro",convert_system_message_to_human=True,response_validation=False)


app = FastAPI() 

origins = [
    "http://*",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration for audio recording
RATE = 16000
CHUNK = int(RATE / 10)  # 100ms



class MicrophoneStream(object):
    """Class for real-time microphone data acquisition"""

    def __init__(self, rate, chunk):
        self._rate = rate
        self._chunk = chunk
        self._buff = queue.Queue()
        self.closed = True

    def __enter__(self):
        self._audio_interface = pyaudio.PyAudio()
        self._audio_stream = self._audio_interface.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=self._rate,
            input=True,
            frames_per_buffer=self._chunk,
            stream_callback=self._fill_buffer,
        )
        self.closed = False
        return self

    def __exit__(self, type, value, traceback):
        self._audio_stream.stop_stream()
        self._audio_stream.close()
        self.closed = True
        self._buff.put(None)
        self._audio_interface.terminate()

    def _fill_buffer(self, in_data, frame_count, time_info, status_flags):
        """Put audio data into buffer every callback"""
        self._buff.put(in_data)
        return None, pyaudio.paContinue

    def generator(self):
        while not self.closed:
            chunk = self._buff.get()
            if chunk is None:
                return
            data = [chunk]

            while True:
                try:
                    chunk = self._buff.get(block=False)
                    if chunk is None:
                        return
                    data.append(chunk)
                except queue.Empty:
                    break

            yield b''.join(data)



    
    


@app.get("/init")
async def init():
    print("Init Called")
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

Bachelor's degree student in Computer Science, Software Engineering or related program
Solid knowledge of machine learning algorithms and deep learning models
Strong programming and debugging skills using Python
Familiarity and some experience with PyTorch framework
Excellent analytical thinking, problem solving, and presentation skills
Familiarity with Graph Neural Network (GNN) models and Reinforcement Learning (RL) algorithms is an asset
Experience with TorchRL and/or PyG libraries is an asset
Some knowledge of network routing and/or optimization problems is an asset
*End of job posting*
An interview question is considered biased if it is irrelevant to job requirements, stereotypes a candidate, assumes inequality, is inconsistent across candidates, leads the candidate to a specific answer, exhibits cultural bias, shows language or accent bias, or contains microaggressions.
You should also be aware of affinity bias. This type of bias occurs when interviewers favor candidates with whom they share similarities, whether in looks, interests, backgrounds, or experiences, even if these aspects are irrelevant to the job's requirements.


Here are some examples to illustrate:

Question: "Do you have children or plan to start a family soon?"
Result: "Do you have children or plan to start a family soon?" is a biased question, because it is irrelevant to the job requirements. Here is an unbiased alternative question you could ask: "Are there any personal commitments or activities that may affect your availability for work or travel?"

Question: "Can you describe your experience with managing large projects?"
Result: "Can you describe your experience with managing large projects?" is not a biased question, good job!

Question: "As a woman, how would you handle working in a predominantly male environment?"
Result: "As a woman, how would you handle working in a predominantly male environment?" is biased, because it's a gender stereotype. Here is an unbiased alternative: "How would you approach fostering a positive and inclusive work environment in a diverse team?"

Question: "How do you approach conflict resolution within a team?"
Result: "How do you approach conflict resolution within a team?" is not biased, keep up the good work!

Question: "Will your disability hinder your ability to work long hours?"
Result: "Will your disability hinder your ability to work long hours?" is biased, because it is assuming inequality. Here is an unbiased alternative: "What accommodations or support, if any, do you need to perform at your best in this role?"

Question: "What strategies do you use to prioritize your tasks?"
Result: "What strategies do you use to prioritize your tasks?" is a great non-biased question, great job!

Question: "What are your career goals for the next five years?"
Result: "What are your career goals for the next five years?" is not biased, keep the good questions rolling!

Question: "How do you feel about reporting to someone younger than you?"
Result: "How do you feel about reporting to someone younger than you?" is biased, because it is an inconsistent question. Here is an unbiased alternative: "What strategies do you use to build successful working relationships with colleagues of various backgrounds and experiences?"

Question: "You're not planning to take any extended personal time soon, are you?"
Result: "You're not planning to take any extended personal time soon, are you?" is biased, because it is a leading question. Here is something you could try instead: "Can you describe your availability for the upcoming months and how you typically manage personal time off?"

Question: "You're from Iran; can you handle the freedom/responsibility here?"
Result: "You're from Iran; can you handle the freedom/responsibility here?" is a biased question because it is culture bias. Here is an unbiased alternative: "Can you describe your experience adjusting to different work environments and cultures, and how you approach new responsibilities?"

Question: "Can you give an example of a time when you overcame a significant challenge at work?"
Result: "Can you give an example of a time when you overcame a significant challenge at work?" is not a biased question, keep up the great work!

Question: "Where did you learn to speak English?"
Result: "Where did you learn to speak English?" is biased due to language or accent bias, try an unbiased alternative instead: "What experiences have contributed to your proficiency in English?"

Question: "What is your approach to ensuring clear communication with your team?"
Result: "What is your approach to ensuring clear communication with your team?" is not biased, good job!

Question: "You're quite articulate for someone from your background."
Result: "You're quite articulate for someone from your background." is biased due to microaggressions, try this unbiased version instead: "Can you describe how your communication skills have contributed to your success in previous roles?"

Question: "We went to the same college, right? It's great to see alumni applying. How do you think our shared college experience has equipped you for this job?"
Result: "We went to the same college, right? It's great to see alumni applying. How do you think our shared college experience has equipped you for this job?" is affinity bias, try an unbiased version instead: "How do you feel your college experience has prepared you for this role?"""
    
    client = speech.SpeechClient()
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=RATE,
        language_code='en-US',
        enable_automatic_punctuation=True,
        enable_speaker_diarization=True,
        diarization_speaker_count=1,
    )
    streaming_config = speech.StreamingRecognitionConfig(
        config=config,
        interim_results=True,
    )

    with MicrophoneStream(RATE, CHUNK) as stream:
        audio_generator = stream.generator()
        requests = (speech.StreamingRecognizeRequest(audio_content=content)
                    for content in audio_generator)

        responses = client.streaming_recognize(streaming_config, requests)

        for response in responses:
            if not response.results:
                continue

            result = response.results[0]
            if not result.alternatives:
                continue

            transcript = result.alternatives[0].transcript
            if result.is_final:
                print(transcript)
            
            
                human = f"Evaluate only the following text in the manner outlined above in at most 60 words. Only respond to the text I give you and nothing else. {transcript}"
                
                prompt = ChatPromptTemplate.from_messages([("system", system), ("human", human)])
                chain = prompt | chat
                res = chain.invoke({})
                

                print(res.content)
                currentCounter = r.get("counter").decode("utf-8")
                
                res1 = r.set("response"+currentCounter, res.content)
                r.set("counter", str(int(currentCounter)+1))
                
                

            

                
                

        
                
