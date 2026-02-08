import { Link } from "react-router-dom";

export default function HomePage() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-primary-50 to-white">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <header className="text-center mb-12">
          <h1 className="text-4xl md:text-5xl font-bold text-primary-700 mb-4">SANSA</h1>
          <p className="text-xl md:text-2xl text-gray-600">
            Self-administered Nutrition Screening and Assessment Tool
          </p>
        </header>

        {/* Main Navigation Cards */}
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6 max-w-6xl mx-auto">
          {/* แบบคัดกรองและประเมินภาวะโภชนาการ */}
          <Link
            to="/start"
            className="block p-8 bg-white rounded-xl shadow-lg hover:shadow-xl transition-all border-4 border-primary-600 hover:border-primary-700"
          >
            <div className="text-5xl mb-4">👴👵</div>
            <h2 className="text-2xl font-semibold text-gray-800 mb-2">
              แบบคัดกรองและประเมินภาวะโภชนาการ
            </h2>
            <p className="text-gray-600">ด้วยตนเองสำหรับผู้สูงอายุในชุมชน</p>
          </Link>

          {/* บันทึกการกิน */}
          <Link
            to="/start"
            className="block p-8 bg-white rounded-xl shadow-lg hover:shadow-xl transition-all border-4 border-primary-600 hover:border-primary-700"
          >
            <div className="text-5xl mb-4">📔</div>
            <h2 className="text-2xl font-semibold text-gray-800 mb-2">บันทึกการกิน</h2>
            <p className="text-gray-600">บันทึกอาหารและเครื่องดื่มที่รับประทาน</p>
          </Link>

          {/* ความรู้เรื่องอาหาร */}
          <Link
            to="/knowledge"
            className="block p-8 bg-white rounded-xl shadow-lg hover:shadow-xl transition-all border-4 border-primary-600 hover:border-primary-700"
          >
            <div className="text-5xl mb-4">🔍</div>
            <h2 className="text-2xl font-semibold text-gray-800 mb-2">ความรู้เรื่องอาหาร</h2>
            <p className="text-gray-600">ข้อมูลความรู้เกี่ยวกับโภชนาการและสุขภาพ</p>
          </Link>

          {/* ประเมินความพึงพอใจ */}
          <Link
            to="/start"
            className="block p-8 bg-white rounded-xl shadow-lg hover:shadow-xl transition-all border-4 border-primary-600 hover:border-primary-700"
          >
            <div className="text-5xl mb-4">💻</div>
            <h2 className="text-2xl font-semibold text-gray-800 mb-2">ประเมินความพึงพอใจ</h2>
            <p className="text-gray-600">แบบสอบถามความพึงพอใจต่อระบบ</p>
          </Link>

          {/* ศูนย์บริการสาธารณสุข */}
          <Link
            to="/facilities"
            className="block p-8 bg-white rounded-xl shadow-lg hover:shadow-xl transition-all border-4 border-primary-600 hover:border-primary-700"
          >
            <div className="text-5xl mb-4">🏥</div>
            <h2 className="text-2xl font-semibold text-gray-800 mb-2">ศูนย์บริการสาธารณสุข</h2>
            <p className="text-gray-600">ค้นหาศูนย์บริการสุขภาพใกล้คุณ</p>
          </Link>

          {/* Admin Login */}
          <Link
            to="/admin/login"
            className="block p-8 bg-white rounded-xl shadow-lg hover:shadow-xl transition-all border-4 border-primary-600 hover:border-primary-700"
          >
            <div className="text-5xl mb-4">🔐</div>
            <h2 className="text-2xl font-semibold text-gray-800 mb-2">Admin Login</h2>
            <p className="text-gray-600">เข้าสู่ระบบสำหรับเจ้าหน้าที่</p>
          </Link>
        </div>

        {/* Info Section */}
        <div className="mt-16 max-w-4xl mx-auto bg-white rounded-xl shadow-lg p-8 border-2 border-primary-200">
          <h3 className="text-2xl font-semibold text-primary-800 mb-4">
            ยินดีต้อนรับสู่ระบบ SANSA
          </h3>
          <div className="space-y-4 text-gray-600">
            <p>
              ระบบนี้ออกแบบมาเพื่อช่วยประเมินภาวะโภชนาการผ่านแบบสอบถามคัดกรอง
              และแบบประเมินพฤติกรรมการบริโภคอาหาร
            </p>
            <p>
              <strong>สำหรับผู้เข้าร่วม:</strong> เริ่มการประเมินโดยคลิกที่
              "แบบคัดกรองและประเมินภาวะโภชนาการ" คุณสามารถใช้รหัสผู้เข้าร่วมเดิม
              หรือสร้างรหัสใหม่ได้
            </p>
            <p>
              <strong>สำหรับเจ้าหน้าที่:</strong> เข้าสู่ระบบผ่าน Admin Login
              เพื่อเข้าถึงการจัดการข้อมูล ฟังก์ชันส่งออกข้อมูล และเครื่องมือบริหารจัดการ
            </p>
            <p>ข้อมูลทั้งหมดถูกเก็บรักษาเป็นความลับและใช้เพื่อการวิจัยเท่านั้น</p>
          </div>
        </div>

        {/* Footer */}
        <footer className="mt-16 text-center text-gray-500">
          <p>© 2026 SANSA Research System. All rights reserved.</p>
          <p className="mt-2 text-sm">Version 1.0.0</p>
        </footer>
      </div>
    </div>
  );
}
