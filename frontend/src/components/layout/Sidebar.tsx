import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard, ShoppingCart, Package, Warehouse,
  Users, BarChart2, Settings, LogOut, Leaf
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

export default function Sidebar() {
  const { user, logout } = useAuthStore();

  return (
    <aside className="w-64 bg-gray-900 text-white flex flex-col h-screen shrink-0">
      {/* Logo */}
      <div className="px-6 py-5 border-b border-gray-700">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-green-500 rounded-xl flex items-center justify-center">
            <Leaf className="w-6 h-6 text-white" />
          </div>
          <div>
            <p className="font-bold text-white text-sm">AgriPOS</p>
            <p className="text-xs text-gray-400">ระบบจัดการร้านค้า</p>
          </div>
        </div>
      </div>

      {/* Nav */}
      <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
        {navItems.map(({ to, icon: Icon, label, exact }) => (
          <NavLink
            key={to}
            to={to}
            end={exact}
            className={({ isActive }) =>
              clsx(
                'flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-colors',
                isActive
                  ? 'bg-green-600 text-white'
                  : 'text-gray-400 hover:bg-gray-800 hover:text-white'
              )
            }
          >
            <Icon className="w-5 h-5 shrink-0" />
            {label}
          </NavLink>
        ))}
      </nav>

      {/* User */}
      <div className="px-4 py-4 border-t border-gray-700">
        <div className="flex items-center gap-3 mb-3">
          <div className="w-8 h-8 bg-green-500 rounded-full flex items-center justify-center text-sm font-bold">
            {user?.full_name?.[0] || 'U'}
          </div>
          <div className="min-w-0">
            <p className="text-sm font-medium text-white truncate">{user?.full_name}</p>
            <p className="text-xs text-gray-400">{user?.role}</p>
          </div>
        </div>
        <button
          onClick={logout}
          className="w-full flex items-center gap-2 px-3 py-2 text-gray-400 hover:text-red-400 hover:bg-gray-800 rounded-lg text-sm transition-colors"
        >
          <LogOut className="w-4 h-4" />
          ออกจากระบบ
        </button>
      </div>
    </aside>
  );
}
