import { useEffect } from "react";
import { Navigate, Route, BrowserRouter as Router, Routes, useParams } from "react-router-dom";
import AdminRoutes from "./pages/admin/AdminRoutes";
import AdminLoginPage from "./pages/AdminLoginPage";
import BIAMeasurementPage from "./pages/BIAMeasurementPage";
import FacilitiesPage from "./pages/FacilitiesPage";
import FoodDiaryPage from "./pages/FoodDiaryPage";
import GeneralInfoPage from "./pages/GeneralInfoPage";
import HomePage from "./pages/HomePage";
import KnowledgePage from "./pages/KnowledgePage";
import MNAAssessmentPage from "./pages/MNAAssessmentPage";
import RespondentStartPage from "./pages/RespondentStartPage";
import ResultPage from "./pages/ResultPage";
import SANSAFormPage from "./pages/SANSAFormPage";
import SatisfactionPage from "./pages/SatisfactionPage";
import { useUIStore } from "./stores/uiStore";

function VisitResultRedirect() {
  const { visitId } = useParams();
  return <Navigate to={`/result/${visitId}`} replace />;
}

function App() {
  const { largeTextMode } = useUIStore();

  useEffect(() => {
    if (largeTextMode) {
      document.body.classList.add("large-text-mode");
    } else {
      document.body.classList.remove("large-text-mode");
    }
  }, [largeTextMode]);

  return (
    <Router>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/start" element={<RespondentStartPage />} />
        <Route path="/general-info/:respondentCode" element={<GeneralInfoPage />} />
        <Route path="/sansa/:respondentCode" element={<SANSAFormPage />} />
        <Route path="/result/:visitId" element={<ResultPage />} />
        <Route path="/visit/:visitId/result" element={<VisitResultRedirect />} />
        <Route path="/satisfaction/:visitId" element={<SatisfactionPage />} />
        <Route path="/mna/:visitId" element={<MNAAssessmentPage />} />
        <Route path="/bia/:visitId" element={<BIAMeasurementPage />} />
        <Route path="/food-diary/:respondentCode" element={<FoodDiaryPage />} />
        <Route path="/knowledge" element={<KnowledgePage />} />
        <Route path="/facilities" element={<FacilitiesPage />} />
        <Route path="/admin/login" element={<AdminLoginPage />} />
        <Route path="/admin/*" element={<AdminRoutes />} />
      </Routes>
    </Router>
  );
}

export default App;
