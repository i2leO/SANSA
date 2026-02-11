import { useAuthStore } from "@/stores/authStore";
import { ReactNode } from "react";
import { Navigate, useLocation, useNavigate } from "react-router-dom";

export default function AdminLayout({ children, title }: { children: ReactNode; title: string }) {
  const { isAuthenticated, user, logout } = useAuthStore();
  const navigate = useNavigate();
  const location = useLocation();

  const isDashboard =
    location.pathname === "/admin" ||
    location.pathname === "/admin/" ||
    location.pathname === "/admin/dashboard";

  if (!isAuthenticated) {
    return <Navigate to="/admin/login" replace />;
  }

  const handleLogout = () => {
    logout();
    navigate("/admin/login");
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-primary-50 to-white">
      <header className="bg-white shadow-md border-b-4 border-primary-600">
        <div className="container mx-auto px-4 py-4 flex justify-between items-center">
          <div>
            <button
              onClick={() => navigate("/admin/dashboard")}
              className="text-2xl font-bold text-primary-700 hover:text-primary-800"
            >
              SANSA Admin
            </button>
            <p className="text-sm text-gray-600">{title}</p>
          </div>

          <div className="flex items-center gap-4">
            <div className="text-right">
              <p className="text-sm text-gray-600">ผู้ใช้งาน</p>
              <p className="font-semibold text-gray-800">{user?.full_name || user?.username}</p>
              <p className="text-xs text-gray-500">
                {user?.role === "admin" ? "ผู้ดูแลระบบ" : "เจ้าหน้าที่"}
              </p>
            </div>
            <button
              onClick={handleLogout}
              className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
            >
              ออกจากระบบ
            </button>
          </div>
        </div>
      </header>

      <div className="container mx-auto px-4 py-8">
        {!isDashboard && (
          <div className="mb-6">
            <button
              onClick={() => navigate("/admin/dashboard")}
              className="text-primary-600 hover:text-primary-700 font-medium"
            >
              ← กลับหน้าแดชบอร์ด
            </button>
          </div>
        )}

        {children}
      </div>
    </div>
  );
}
