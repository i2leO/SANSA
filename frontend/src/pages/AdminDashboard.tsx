import { useEffect, useState } from 'react';
import apiClient from '@/lib/api';
import AdminIcon from '@/pages/admin/AdminIcon';
import AdminLayout from '@/pages/admin/AdminLayout';
import { adminMenu } from '@/pages/admin/adminMenu';
import { useAuthStore } from '@/stores/authStore';
import { Link } from 'react-router-dom';

export default function AdminDashboard() {
  const { user } = useAuthStore();
  const [stats, setStats] = useState<number[] | null>(null);
  const [statsError, setStatsError] = useState(false);
  useEffect(() => { let active = true; apiClient.get<{respondents:number;visits_today:number;knowledge:number;facilities:number}>('/admin/dashboard').then(({data}) => { if(active) setStats([data.respondents,data.visits_today,data.knowledge,data.facilities]); }).catch(() => { if(active) setStatsError(true); }); return () => {active=false;}; }, []);
  const hour = new Date().getHours();
  const greeting = hour < 12 ? 'สวัสดีตอนเช้า' : hour < 17 ? 'สวัสดีตอนบ่าย' : 'สวัสดีตอนเย็น';
  const targets=[200,50,30,20];
  return <AdminLayout title="ภาพรวมระบบ">
    <section className="sansa-banner p-7 md:p-9 mb-7"><div className="relative"><h2 className="text-2xl md:text-3xl font-bold">☀ {greeting}, {user?.full_name || user?.username}!</h2><p className="mt-3 text-white/90">ยินดีต้อนรับสู่ระบบจัดการ SANSA — เลือกเมนูด้านล่างเพื่อจัดการข้อมูล</p></div></section>
    <section aria-label="สถิติระบบ" className="grid sm:grid-cols-2 xl:grid-cols-4 gap-5 mb-8">
      {['ผู้เข้าร่วมทั้งหมด','การประเมินวันนี้','บทความความรู้','ศูนย์บริการ'].map((label,index) => <div key={label} className={`sansa-panel sansa-stat-card stat-${index}`}><div><p>{stats?.[index] ?? "—"}</p><h2>{label}</h2><small>{statsError ? "โหลดสถิติไม่สำเร็จ" : stats ? "ข้อมูลล่าสุด" : "กำลังโหลด…"}</small></div><span>{stats?.[index] ?? "—"}<small>/ {targets[index]}</small></span></div>)}
    </section>
    <h2 className="font-bold text-lg text-primary-600 mb-5">เมนูจัดการ</h2>
    <div className="grid md:grid-cols-2 xl:grid-cols-3 gap-5">
      {adminMenu.filter(item => item.path !== 'users' || user?.role === 'admin').map(item => <Link key={item.path} to={`/admin/${item.path}`} className="sansa-panel sansa-tile p-6"><span aria-hidden className={`sansa-menu-icon sansa-icon-${item.color}`}><AdminIcon name={item.path} /></span><h3 className="font-bold text-lg mt-4">{item.heading}</h3><p className="text-sm text-slate-500 mt-2">{item.detail}</p></Link>)}
    </div>
  </AdminLayout>;
}
