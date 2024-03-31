import { useState, useEffect } from 'react'
import reactLogo from './assets/react.svg'
import viteLogo from '/vite.svg'
import axios from 'axios';
import './App.css'
import pdfToText from 'react-pdftotext'



function App() {
  

  const [recording, setRecording] = useState(false);
  const [feedback, setFeedback] = useState("");
  const [finishFeedback, setFinishFeedback] = useState("");
  const [pdf,setPdf] = useState("");

  useEffect(()=>{
    let interval=null;

    if (recording){
      interval = setInterval(()=>{
        console.log("calling gemini from frontend")

        axios({
          method: "get",
          url: "http://127.0.0.1:5000/retrieve",
          
        }).then(function (response) {
          console.log(response.data)
          const dataArray = response.data;
          const stringData = dataArray.map(item => item + '\n').join('');
          setFeedback(stringData);
        });

      },4000)
    }
  },[recording])
  
  const startRecording = async () => {
    setRecording(true);
    console.log("init called from frontend")
    const response = await fetch(`http://127.0.0.1:8000/init`)
  };

  const stopRecording = async () => {
    setRecording(false);
    axios({
      method: "get",
      url: "http://127.0.0.1:5000/finish",
    }).then(function (response) {
      console.log(response.data)
      const data = response.data;
      setFinishFeedback(data);
    });
  };

  function extractText(event) {
    const file = event.target.files[0]
    pdfToText(file)
        .then(function (text) {
          setPdf(text)
          console.log(text)
        })
        .catch(error => console.error("Failed to extract text from pdf"))
}

  

  return (
    <>
      <link rel="stylesheet" href="https://fonts.googleapis.com/css?family=Kanit"></link>
      <div>
      <nav class="navbar">
          <img src="../src/assets/Logo.PNG" class="logo" alt=""/>
          <h1 class="website-name">InterView</h1>
      </nav>
      </div>

      <div class="left-panel">
        <h2>Tell us a bit about your interview:</h2>
        <form>
          <input type="text" name="interviewer_name" placeholder="Enter your name"></input>
          <input type="text" name="interviewee_name" placeholder="Enter your interviewee's name"></input>
          <input type="text" name="job_position" placeholder="What position are you interviewing for?"></input>
          <label for="job-desc">Upload Job Description</label>
          {/* <input type="file" onChange={handleFileSelected} name="file_uploaded" id="job-desc"></input> */}
          <input type="file"  accept="application/pdf" onChange={extractText} name="file_uploaded" id="job-desc"></input>
          <div class="buttons">
            <button type="button" name="interview_start" id="start" onClick={startRecording}>Start Interview</button>
            <button type="button" name="interview_stop" id="end" onClick={stopRecording}>End Interview</button>
          </div>
        </form>
      </div>

      <div class="right-panel">

        <h2 class="insights">Real-time Interview Feedback</h2>
        
        <p class="scrollable-output">{feedback}</p>
        <h2 class="insights">Post-Interview Insights</h2>
        <p class="scrollable-output">{finishFeedback}</p>
      
      </div>

    </>
  )
}

export default App
