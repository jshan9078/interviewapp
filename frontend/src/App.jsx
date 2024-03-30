import { useState } from 'react'
import reactLogo from './assets/react.svg'
import viteLogo from '/vite.svg'
import './App.css'

function App() {
  const [count, setCount] = useState(0)

  return (
    <>
      
      <div>
      <nav class="navbar">
          <img src="../src/assets/Logo.PNG" class="logo" alt=""/>
          <h1 class="website-name">InterView</h1>
      </nav>
      </div>

      <div class="left-panel">
        <h2>Tell us a bit about your interview:</h2>
        <form>
          <input type="text" placeholder="Enter your name"></input>
          <input type="text" placeholder="Enter your interviewee's name"></input>
          <input type="text" placeholder="What position are you interviewing for?"></input>
          <label for="job-desc">Upload Job Description</label>
          <input type="file" id="job-desc"></input>
          <div class="buttons">
            <button type="button" id="start">Start Interview</button>
            <button type="button" id="end">End Interview</button>
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
