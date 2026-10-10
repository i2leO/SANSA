import AdminDashboard from "@/pages/AdminDashboard";
import AdminExportsPage from "@/pages/admin/AdminExportsPage";
import AdminFacilitiesAdminPage from "@/pages/admin/AdminFacilitiesAdminPage";
import AdminKnowledgePage from "@/pages/admin/AdminKnowledgePage";
import AdminRespondentDetailPage from "@/pages/admin/AdminRespondentDetailPage";
import AdminRespondentsPage from "@/pages/admin/AdminRespondentsPage";
import AdminResultPage from "@/pages/admin/AdminResultPage";
import AdminScoringPage from "@/pages/admin/AdminScoringPage";
import AdminUsersPage from "@/pages/admin/AdminUsersPage";
import BIAMeasurementPage from "@/pages/BIAMeasurementPage";
import MNAAssessmentPage from "@/pages/MNAAssessmentPage";
import { Navigate, Route, Routes } from "react-router-dom";
import { useAuthStore } from "@/stores/authStore";

export default function AdminRoutes() {
  const {isAuthenticated,user}=useAuthStore();
  if(!isAuthenticated)return <Navigate to="/login" replace />;
  if(user?.role !== 'staff' && user?.role !== 'admin')return <Navigate to="/" replace />;
  return (
    <Routes>
      <Route path="dashboard" element={<AdminDashboard />} />
      <Route path="respondents" element={<AdminRespondentsPage />} />
      <Route path="respondents/:respondentCode" element={<AdminRespondentDetailPage />} />
      <Route path="results/:visitId" element={<AdminResultPage />} />
      <Route path="results/:visitId/bia" element={<BIAMeasurementPage staffMode />} />
      <Route path="results/:visitId/mna" element={<MNAAssessmentPage staffMode />} />
      <Route path="exports" element={<AdminExportsPage />} />
      <Route path="knowledge" element={<AdminKnowledgePage />} />
      <Route path="facilities" element={<AdminFacilitiesAdminPage />} />
      <Route path="scoring" element={<AdminScoringPage />} />
      <Route path="users" element={<AdminUsersPage />} />

      <Route path="" element={<Navigate to="dashboard" replace />} />
      <Route path="*" element={<Navigate to="dashboard" replace />} />
    </Routes>
  );
}
