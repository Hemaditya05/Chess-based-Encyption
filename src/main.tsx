import React from 'react'
import ReactDOM from 'react-dom/client'
import './index.css'       // ← add this import
import App from './App'

ReactDOM.createRoot(document.getElementById('root') as HTMLElement).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)