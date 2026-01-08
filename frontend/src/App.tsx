import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { useEffect } from 'react'
import HomePage from './pages/HomePage'
import RespondentStartPage from './pages/RespondentStartPage'
import GeneralInfoPage from './pages/GeneralInfoPage'
import SANSAFormPage from './pages/SANSAFormPage'
import ResultPage from './pages/ResultPage'
import SatisfactionPage from './pages/SatisfactionPage'
import FoodDiaryPage from './pages/FoodDiaryPage'
import KnowledgePage from './pages/KnowledgePage'
import FacilitiesPage from './pages/FacilitiesPage'
import AdminLoginPage from './pages/AdminLoginPage'
import AdminDashboard from './pages/AdminDashboard'
import { useUIStore } from './stores/uiStore'

function App() {
  const { largeTextMode } = useUIStore()

  useEffect(() => {
    if (largeTextMode) {
      document.body.classList.add('large-text-mode')
    } else {
      document.body.classList.remove('large-text-mode')
    }
  }, [largeTextMode])

  return (
    <Router>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/start" element={<RespondentStartPage />} />
        <Route path="/general-info/:respondentCode" element={<GeneralInfoPage />} />
        <Route path="/sansa/:respondentCode" element={<SANSAFormPage />} />
        <Route path="/result/:visitId" element={<ResultPage />} />
        <Route path="/satisfaction/:visitId" element={<SatisfactionPage />} />
        <Route path="/food-diary/:respondentCode" element={<FoodDiaryPage />} />
        <Route path="/knowledge" element={<KnowledgePage />} />
        <Route path="/facilities" element={<FacilitiesPage />} />
        <Route path="/admin/login" element={<AdminLoginPage />} />
        <Route path="/admin/*" element={<AdminDashboard />} />
      </Routes>
    </Router>
  )
}

export default App
