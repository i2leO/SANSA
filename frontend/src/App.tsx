import { useEffect } from "react";
import { Navigate, Route, BrowserRouter as Router, Routes, useParams, useLocation, Link } from "react-router-dom";
import AdminRoutes from "./pages/admin/AdminRoutes";
import AdminLoginPage from "./pages/AdminLoginPage";
import FacilitiesPage from "./pages/FacilitiesPage";
import FoodDiaryPage from "./pages/FoodDiaryPage";
import GeneralInfoPage from "./pages/GeneralInfoPage";
import HomePage from "./pages/HomePage";
import KnowledgePage from "./pages/KnowledgePage";
import ParticipantHomePage from "./pages/ParticipantHomePage";
import ParticipantWaistPage from "./pages/ParticipantWaistPage";
import RespondentStartPage from "./pages/RespondentStartPage";
import ResultPage from "./pages/ResultPage";
import SANSAFormPage from "./pages/SANSAFormPage";
import SatisfactionPage from "./pages/SatisfactionPage";
import { useUIStore } from "./stores/uiStore";

function VisitResultRedirect() {
  const { visitId } = useParams();
  return <Navigate to={`/result/${visitId}`} replace />;
}

function RouteTheme({ children }: { children: React.ReactNode }) {
  const {pathname}=useLocation();
  const participantCode=sessionStorage.getItem('participantCode');
  const participantHome=participantCode?`/participant/${encodeURIComponent(participantCode)}`:'/';
  const assessment=!pathname.startsWith('/admin') && !['/', '/facilities', '/knowledge', '/start', '/login'].includes(pathname);
  return <div className={assessment ? 'sansa-assessment' : ''}>{assessment && <header className="sansa-public-header"><Link to={participantHome} className="flex items-center gap-3 font-bold text-primary-700"><span className="sansa-brand-icon text-3xl" aria-hidden>ϟ</span><span>SANSA</span></Link><Link to="/start" onClick={()=>{sessionStorage.removeItem('participantToken');sessionStorage.removeItem('participantCode');}} className="text-sm text-primary-700">ออกจากระบบผู้เข้าร่วม</Link></header>}{children}</div>;
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
      <RouteTheme><Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/start" element={<RespondentStartPage />} />
        <Route path="/login" element={<RespondentStartPage />} />
        <Route path="/participant/:respondentCode" element={<ParticipantHomePage />} />
        <Route path="/general-info/:respondentCode" element={<GeneralInfoPage />} />
        <Route path="/sansa/:respondentCode" element={<SANSAFormPage />} />
        <Route path="/result/:visitId" element={<ResultPage />} />
        <Route path="/visit/:visitId/result" element={<VisitResultRedirect />} />
        <Route path="/satisfaction/:visitId" element={<SatisfactionPage />} />
        <Route path="/mna/:visitId" element={<Navigate to="/" replace />} />
        <Route path="/bia/:visitId" element={<ParticipantWaistPage />} />
        <Route path="/food-diary/:respondentCode" element={<FoodDiaryPage />} />
        <Route path="/knowledge" element={<KnowledgePage />} />
        <Route path="/facilities" element={<FacilitiesPage />} />
        <Route path="/admin/login" element={<AdminLoginPage />} />
        <Route path="/admin/*" element={<AdminRoutes />} />
      </Routes></RouteTheme>
    </Router>
  );
}

export default App;
