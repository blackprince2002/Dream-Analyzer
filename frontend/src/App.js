import React, { useState } from 'react';
import axios from 'axios';
import './App.css';  // Import styles
import 'bootstrap/dist/css/bootstrap.min.css';  // Import Bootstrap for additional styling
import logo from './logo.png';  // Make sure you have your Algo Craft logo saved as logo.png in the src folder

function App() {
  const [dreamText, setDreamText] = useState('');
  const [response, setResponse] = useState(null);
  const [isLoading, setIsLoading] = useState(false);  // For loading state

  // Function to handle the submit and call Flask backend
  // Function to handle the submit and call Flask backend
  const handleAnalyzeDream = () => {
    setIsLoading(true);  // Set loading state to true when the request starts
    axios.post('http://localhost:5000/analyze', { dream: dreamText })
      .then((res) => {
        setResponse(res.data); // Set the response from the backend
        console.log(res.data);  // Optionally log the response
        setIsLoading(false);  // Set loading state to false when the request finishes
      })
      .catch((error) => {
        console.error('Error:', error);
        setIsLoading(false);  // Set loading state to false if there's an error
      });
  };

  // Function for typewriter effect
  const simulateTyping = (text) => {
    let index = 0;
    let result = '';
    const interval = setInterval(() => {
      result += text[index];
      setResponse(result); // Update the result one character at a time
      index++;
      if (index === text.length) {
        clearInterval(interval); // Stop the typing once done
      }
    }, 50); // Adjust speed by changing 50ms
  };

  // Render categories in a structured format
  const renderCategories = (categories) => {
    return Object.keys(categories).map((category, index) => (
      <div key={index} className="category">
        <h3>{category}</h3>
        <div className="category-content">
          {Object.keys(categories[category]).map((subCategory, i) => (
            <div key={i}>
              <h5>{subCategory.charAt(0).toUpperCase() + subCategory.slice(1)}:</h5>
              <ul>
                {categories[category][subCategory].map((item, j) => (
                  <li key={j}>{item}</li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      </div>
    ));
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>Dream Analyzer</h1>

        {/* Powered by Algo Craft directly below Dream Analyzer title */}
        <div className="powered-by">
          <p>Powered by <img src={logo} alt="Algo Craft" className="logo" /></p>
        </div>

        {/* Dream Analyzer 1.0 (BETA) on top-right corner */}
        <div className="dream-analyzer-beta">Dream Analyzer 1.0
            (BETA)</div>

        <textarea
          value={dreamText}
          onChange={(e) => setDreamText(e.target.value)}
          placeholder="Type your dream here..."
          rows="4"
          cols="50"
        />
        <button onClick={handleAnalyzeDream} disabled={isLoading}>
          {isLoading ? 'Analyzing...' : 'Analyze Dream'}
        </button>

        {response && (
          <div className="result-container">
            <h2>Analysis Result:</h2>
            <div className="sentiment">
              <h4>Sentiment: <span className={response.sentiment.toLowerCase()}>{response.sentiment}</span></h4>
            </div>

            <div className="categories">
              <h3>Categories:</h3>
              {renderCategories(response.categories)}
            </div>
          </div>
        )}
      </header>
    </div>
  );
}

export default App;
