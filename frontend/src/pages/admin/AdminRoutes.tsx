import AdminDashboard from "@/pages/AdminDashboard";
import AdminExportsPage from "@/pages/admin/AdminExportsPage";
import AdminFacilitiesAdminPage from "@/pages/admin/AdminFacilitiesAdminPage";
import AdminKnowledgePage from "@/pages/admin/AdminKnowledgePage";
import AdminRespondentDetailPage from "@/pages/admin/AdminRespondentDetailPage";
import AdminRespondentsPage from "@/pages/admin/AdminRespondentsPage";
import AdminResultPage from "@/pages/admin/AdminResultPage";
import AdminScoringPage from "@/pages/admin/AdminScoringPage";
import AdminUsersPage from "@/pages/admin/AdminUsersPage";
import { Navigate, Route, Routes } from "react-router-dom";

export default function AdminRoutes() {
  return (
    <Routes>
      <Route path="dashboard" element={<AdminDashboard />} />
      <Route path="respondents" element={<AdminRespondentsPage />} />
      <Route path="respondents/:respondentCode" element={<AdminRespondentDetailPage />} />
      <Route path="results/:visitId" element={<AdminResultPage />} />
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
