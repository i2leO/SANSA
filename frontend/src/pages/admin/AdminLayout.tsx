import apiClient from '@/lib/api';
import AdminIcon from '@/pages/admin/AdminIcon';
import { useAuthStore } from '@/stores/authStore';
import { FormEvent, ReactNode, useState } from 'react';
import { Link, Navigate, NavLink, useLocation, useNavigate, useSearchParams } from 'react-router-dom';

import { adminMenu } from './adminMenu';

type DashboardStatus = {
  respondents: number;
  visits_today: number;
  knowledge: number;
  facilities: number;
  incomplete_visits: number;
  knowledge_drafts: number;
  facilities_inactive: number;
};

type NotificationItem = { label: string; path: string; count: number };

export default function AdminLayout({ children, title }: { children: ReactNode; title: string }) {
  const { isAuthenticated, user, logout } = useAuthStore();
  const navigate = useNavigate();
  const location = useLocation();
  const [searchParams, setSearchParams] = useSearchParams();
  const [notificationsOpen, setNotificationsOpen] = useState(false);
  const [notificationItems, setNotificationItems] = useState<NotificationItem[]>([]);
  const [notificationsLoading, setNotificationsLoading] = useState(false);
  const [notificationsError, setNotificationsError] = useState(false);
  const searchPlaceholders: Record<string, string> = {
    '/admin/dashboard': 'ค้นหาเมนูจัดการในหน้านี้',
    '/admin/respondents': 'ค้นหารหัสผู้เข้าร่วม อายุ หรือข้อมูลติดต่อ',
    '/admin/exports': 'ค้นหารายการส่งออกข้อมูล',
    '/admin/knowledge': 'ค้นหาหัวข้อ หมวดหมู่ หรือเนื้อหาความรู้',
    '/admin/facilities': 'ค้นหาชื่อ ที่อยู่ หรือเบอร์โทรศูนย์บริการ',
    '/admin/scoring': 'ค้นหารายการกฎคะแนน',
    '/admin/users': 'ค้นหาชื่อบัญชี ชื่อผู้ใช้ หรือสิทธิ์',
  };
  const searchPlaceholder = searchPlaceholders[location.pathname];
  const query = searchParams.get('q') || '';

  if (!isAuthenticated) return <Navigate to="/login" replace />;
  if (user?.role !== 'staff' && user?.role !== 'admin') return <Navigate to="/" replace />;

  const name = user?.full_name || user?.username || 'ผู้ใช้งาน';
  const initials = name.split(' ').map(part => part[0]).slice(0, 2).join('').toUpperCase();
  const setQuery = (value: string) => {
    setSearchParams(previous => {
      const next = new URLSearchParams(previous);
      if (value.trim()) next.set('q', value);
      else next.delete('q');
      return next;
    }, { replace: true });
  };
  const submitSearch = (event: FormEvent) => {
    event.preventDefault();
  };
  const loadNotifications = async () => {
    setNotificationsLoading(true);
    setNotificationsError(false);
    try {
      const { data } = await apiClient.get<DashboardStatus>('/admin/dashboard');
      setNotificationItems([
        { label: 'รอบประเมินที่ข้อมูล SANSA / MNA / BIA ยังไม่ครบ', path: 'respondents', count: data.incomplete_visits },
        { label: 'บทความที่ยังเป็นฉบับร่าง', path: 'knowledge', count: data.knowledge_drafts },
        { label: 'ศูนย์บริการที่ปิดใช้งาน', path: 'facilities', count: data.facilities_inactive },
      ].filter(item => item.count > 0));
    } catch {
      setNotificationItems([]);
      setNotificationsError(true);
    } finally {
      setNotificationsLoading(false);
    }
  };
  const toggleNotifications = () => {
    const next = !notificationsOpen;
    setNotificationsOpen(next);
    if (next) void loadNotifications();
  };

  return <div className="sansa-admin">
    <aside className="sansa-sidebar">
      <Link to="/admin/dashboard" className="flex items-center gap-4 px-3 py-5"><span className="sansa-brand-icon text-3xl" aria-hidden>ϟ</span><span><strong className="text-xl text-primary-600">SANSA</strong><span className="block mt-1 text-xs tracking-[.2em] text-slate-500">ADMIN PANEL</span></span></Link>
      <nav aria-label="เมนูผู้ดูแลระบบ" className="sansa-admin-nav">
        <NavLink to="/admin/dashboard" title="ภาพรวมข้อมูลและทางลัดสำหรับผู้ดูแลระบบ"><AdminIcon name="home" />Home</NavLink>
        {adminMenu.filter(item => item.path !== 'users' || user?.role === 'admin').map(item => <NavLink key={item.path} to={`/admin/${item.path}`} title={item.detail}><AdminIcon name={item.path} />{item.title}</NavLink>)}
      </nav>
      <div className="mt-auto border-t border-slate-200 pt-5 px-2 flex items-center gap-3">
        <span className="sansa-avatar">{initials}</span><div className="min-w-0 flex-1"><p className="truncate font-semibold">{name}</p><p className="text-xs text-slate-500">{user?.role === 'admin' ? 'ผู้ดูแลระบบ' : 'เจ้าหน้าที่'}</p></div>
        <button aria-label="ออกจากระบบ" title="ออกจากระบบ" className="p-2 text-slate-500 text-xl" onClick={() => { logout(); navigate('/login'); }}>↪</button>
      </div>
    </aside>
    <div className="sansa-admin-workspace">
      <header className="sansa-admin-header">
        {searchPlaceholder ? <form onSubmit={submitSearch} className="sansa-admin-search-wrap" role="search">
          <div className="sansa-admin-search"><span aria-hidden>⌕</span><input value={query} onChange={event => setQuery(event.target.value)} aria-label={searchPlaceholder} autoComplete="off" placeholder={searchPlaceholder} />{query && <button type="button" onClick={() => setQuery('')} aria-label="ล้างคำค้นหา" title="ล้างคำค้นหา">×</button>}</div>
        </form> : <div className="flex-1" />}
        <div className="sansa-header-actions"><div className="relative"><button className="sansa-header-icon" aria-label="การแจ้งเตือน" aria-expanded={notificationsOpen} title="ดูการแจ้งเตือน" onClick={toggleNotifications}>♧{notificationItems.length > 0 && <i />}</button>{notificationsOpen && <div className="sansa-notification-popover"><div className="flex items-center justify-between gap-3"><b>รายการที่ต้องตรวจสอบ</b><button type="button" className="text-primary-700" onClick={() => void loadNotifications()} disabled={notificationsLoading}>รีเฟรช</button></div>{notificationsLoading ? <p>กำลังโหลด…</p> : notificationsError ? <p className="text-red-700">โหลดการแจ้งเตือนไม่สำเร็จ</p> : notificationItems.length === 0 ? <p>ไม่มีรายการที่ต้องตรวจสอบ</p> : <ul>{notificationItems.map(item => <li key={item.path}><button type="button" onClick={() => { setNotificationsOpen(false); navigate(`/admin/${item.path}`); }}><span>{item.label}</span><b>{item.count}</b></button></li>)}</ul>}</div>}</div><Link to="/" className="sansa-header-icon" aria-label="เปิดหน้าเว็บไซต์" title="เปิดหน้าเว็บไซต์สำหรับผู้ใช้งาน">↗</Link><div className="hidden sm:flex items-center gap-3 border-l border-slate-200 pl-5"><span className="sansa-avatar">{initials}</span><div><p className="font-semibold">{name}</p><p className="text-xs text-slate-500">{user?.role === 'admin' ? 'Admin' : 'Staff'}</p></div></div></div>
      </header>
      <main className="p-5 md:p-8 min-w-0" aria-label={title}>{children}</main>
    </div>
  </div>;
}
