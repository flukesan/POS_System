import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard, ShoppingCart, Package, Warehouse,
  Users, BarChart2, Settings, LogOut, Sprout
} from 'lucide-react';
import { useAuthStore } from '../../store/authStore';
import clsx from 'clsx';

const navItems = [
  { to: '/', icon: LayoutDashboard, label: 'แดชบอร์ด', exact: true },
  { to: '/pos', icon: ShoppingCart, label: 'ขายสินค้า (POS)' },
  { to: '/products', icon: Package, label: 'สินค้า' },
  { to: '/stock', icon: Warehouse, label: 'สต๊อก / รับของ' },
  { to: '/customers', icon: Users, label: 'ลูกค้า / เครดิต' },
  { to: '/reports', icon: BarChart2, label: 'รายงาน' },
  { to: '/settings', icon: Settings, label: 'ตั้งค่า' },
];

const roleLabel: Record<string, string> = {
  admin: 'ผู้ดูแลระบบ',
  manager: 'ผู้จัดการ',
  cashier: 'แคชเชียร์',
  warehouse: 'คลังสินค้า',
};

export default function Sidebar() {
  const { user, logout } = useAuthStore();

  return (
    <aside className="w-64 flex flex-col h-screen shrink-0 bg-gradient-to-b from-slate-900 via-slate-900 to-indigo-950 shadow-2xl">
      {/* Logo */}
      <div className="px-5 py-5 border-b border-white/10">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-gradient-to-br from-emerald-400 to-teal-500 rounded-xl flex items-center justify-center shadow-lg">
            <Sprout className="w-6 h-6 text-white" />
          </div>
          <div>
            <p className="font-bold text-white text-base tracking-wide">AgriPOS</p>
            <p className="text-xs text-slate-400">ระบบจัดการร้านค้าเกษตร</p>
          </div>
        </div>
      </div>

      {/* Nav */}
      <nav className="flex-1 px-3 py-4 space-y-0.5 overflow-y-auto">
        {navItems.map(({ to, icon: Icon, label, exact }) => (
          <NavLink
            key={to}
            to={to}
            end={exact}
            className={({ isActive }) =>
              clsx(
                'flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-all duration-150',
                isActive
                  ? 'bg-white/10 text-white border border-white/10'
                  : 'text-slate-400 hover:bg-white/5 hover:text-white'
              )
            }
          >
            {({ isActive }) => (
              <>
                <span className={clsx(
                  'flex items-center justify-center w-8 h-8 rounded-lg transition-all',
                  isActive ? 'bg-emerald-500/20' : ''
                )}>
                  <Icon className={clsx('w-4 h-4', isActive ? 'text-emerald-400' : '')} />
                </span>
                <span>{label}</span>
                {isActive && <span className="ml-auto w-1.5 h-1.5 bg-emerald-400 rounded-full" />}
              </>
            )}
          </NavLink>
        ))}
      </nav>

      {/* User */}
      <div className="px-3 py-4 border-t border-white/10">
        <div className="flex items-center gap-3 px-3 py-2.5 rounded-xl bg-white/5 mb-2">
          <div className="w-9 h-9 bg-gradient-to-br from-indigo-400 to-violet-500 rounded-full flex items-center justify-center text-sm font-bold text-white shadow-md flex-shrink-0">
            {user?.full_name?.[0] || 'U'}
          </div>
          <div className="min-w-0 flex-1">
            <p className="text-sm font-semibold text-white truncate">{user?.full_name}</p>
            <p className="text-xs text-slate-400">{roleLabel[user?.role || ''] || user?.role}</p>
          </div>
        </div>
        <button
          onClick={logout}
          className="w-full flex items-center gap-2.5 px-3 py-2 text-slate-400 hover:text-rose-400 hover:bg-rose-500/10 rounded-xl text-sm transition-all"
        >
          <LogOut className="w-4 h-4" />
          ออกจากระบบ
        </button>
      </div>
    </aside>
  );
}
