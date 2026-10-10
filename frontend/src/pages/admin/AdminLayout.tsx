import AdminIcon from '@/pages/admin/AdminIcon';
import { useAuthStore } from '@/stores/authStore';
import { FormEvent, ReactNode, useState } from 'react';
import { Link, Navigate, NavLink, useNavigate } from 'react-router-dom';

import { adminMenu } from './adminMenu';

export default function AdminLayout({ children, title }: { children: ReactNode; title: string }) {
  const { isAuthenticated, user, logout } = useAuthStore();
  const navigate = useNavigate();
  const [query,setQuery]=useState('');
  const [notificationsOpen,setNotificationsOpen]=useState(false);
  if (!isAuthenticated) return <Navigate to="/login" replace />;
  if (user?.role !== 'staff' && user?.role !== 'admin') return <Navigate to="/" replace />;
  const name = user?.full_name || user?.username || 'ผู้ใช้งาน';
  const initials = name.split(' ').map(part => part[0]).slice(0, 2).join('').toUpperCase();
  const searchMenu=(event:FormEvent)=>{event.preventDefault();const key=query.trim().toLowerCase();if(!key)return;const found=adminMenu.find(item=>`${item.title} ${item.heading} ${item.detail} ${item.path}`.toLowerCase().includes(key));if(found)navigate(`/admin/${found.path}`);};
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
      <header className="sansa-admin-header"><form onSubmit={searchMenu} className="sansa-admin-search" title="พิมพ์ชื่อเมนูแล้วกด Enter เพื่อเปิดเมนู"><span aria-hidden>⌕</span><input value={query} onChange={e=>setQuery(e.target.value)} aria-label="ค้นหาเมนู" placeholder="ค้นหาเมนู เช่น ผู้เข้าร่วม" /></form><div className="sansa-header-actions"><div className="relative"><button className="sansa-header-icon" aria-label="การแจ้งเตือน" title="ดูการแจ้งเตือน" onClick={()=>setNotificationsOpen(value=>!value)}>♧<i /></button>{notificationsOpen&&<div className="sansa-notification-popover"><b>การแจ้งเตือน</b><p>ไม่มีการแจ้งเตือนใหม่</p></div>}</div><Link to="/" className="sansa-header-icon" aria-label="เปิดหน้าเว็บไซต์" title="เปิดหน้าเว็บไซต์สำหรับผู้ใช้งาน">↗</Link><div className="hidden sm:flex items-center gap-3 border-l border-slate-200 pl-5"><span className="sansa-avatar">{initials}</span><div><p className="font-semibold">{name}</p><p className="text-xs text-slate-500">{user?.role === 'admin' ? 'Admin' : 'Staff'}</p></div></div></div></header>
      <main className="p-5 md:p-8 min-w-0" aria-label={title}>{children}</main>
    </div>
  </div>;
}
