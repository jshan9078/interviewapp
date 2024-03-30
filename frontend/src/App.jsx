import { useState } from 'react'
import reactLogo from './assets/react.svg'
import viteLogo from '/vite.svg'
import './App.css'



function App() {
  const [recording_state, setRecord] = useState(0)

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
          <input type="file" onChange={handleFileSelected} name="file_uploaded" id="job-desc"></input>
          <div class="buttons">
            <button type="button" name="interview_start" id="start" onClick={() => setRecord((recording_state) => recording_state=1)}>Start Interview</button>
            <button type="button" name="interview_stop" id="end" onClick={() => setRecord((recording_state) => recording_state=0)}>End Interview</button>
          </div>
        </form>
      </div>

      <div class="right-panel">

        <h2 class="insights">Real-time Interview Recommendations</h2>
        <p class="scrollable-output">OUTPUT</p>
        <h2 class="insights">Post-Interview Insights</h2>
        <p class="scrollable-output">OUTPUT2 aaaaaaaaaaaaa</p>
      
      </div>

    </>
  )
}

export default App
