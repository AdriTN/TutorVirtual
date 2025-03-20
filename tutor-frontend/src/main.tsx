import { createRoot } from 'react-dom/client'
import { CssBaseline } from '@mui/material'
import './index.css'
import App from './App.tsx'

createRoot(document.getElementById('root')!).render(
  <CssBaseline>
    <App />
  </CssBaseline>,
)
