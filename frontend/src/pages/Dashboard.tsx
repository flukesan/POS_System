import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { reportApi } from '../services/api';
import { formatCurrency } from '../utils/format';
import { ShoppingCart, TrendingUp, AlertTriangle, CreditCard, ArrowRight, RefreshCw } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

export default function Dashboard() {
  const navigate = useNavigate();

  const { data: stats, isLoading, refetch } = useQuery({
    queryKey: ['dashboard'],
    queryFn: () => reportApi.dashboard(),
    select: (r) => r.data,
    refetchInterval: 60000,
  });

  const { data: dailySales } = useQuery({
    queryKey: ['daily-sales-chart'],
    queryFn: () => reportApi.dailySales(),
    select: (r) => r.data,
  });

  const kpis = stats
    ? [
        {
          label: 'ยอดขายวันนี้',
          value: formatCurrency(stats.today.total_sales),
          sub: `${stats.today.order_count} รายการ`,
          icon: ShoppingCart,
          gradient: 'from-emerald-500 to-teal-600',
          bg: 'from-emerald-50 to-teal-50',
          text: 'text-emerald-700',
          link: '/pos',
        },
        {
          label: 'ยอดขายเดือนนี้',
          value: formatCurrency(stats.this_month.total_sales),
          sub: `${stats.this_month.order_count} รายการ`,
          icon: TrendingUp,
          gradient: 'from-blue-500 to-indigo-600',
          bg: 'from-blue-50 to-indigo-50',
          text: 'text-blue-700',
          link: '/reports',
        },
        {
          label: 'สินค้าใกล้หมด',
          value: stats.low_stock_products,
          sub: 'รายการที่ต้องสั่งซื้อ',
          icon: AlertTriangle,
          gradient: 'from-amber-500 to-orange-600',
          bg: 'from-amber-50 to-orange-50',
          text: 'text-amber-700',
          link: '/stock',
        },
        {
          label: 'เครดิตค้างชำระ',
          value: formatCurrency(stats.total_outstanding_credit),
          sub: `เกินกำหนด ${stats.overdue_customers} ราย`,
          icon: CreditCard,
          gradient: 'from-rose-500 to-pink-600',
          bg: 'from-rose-50 to-pink-50',
          text: 'text-rose-700',
          link: '/customers',
        },
      ]
    : [];

  return (
    <div className="p-6 space-y-6 min-h-full bg-slate-50">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-800">แดชบอร์ด</h1>
          <p className="text-sm text-slate-500 mt-0.5">ภาพรวมยอดขายและสต๊อกสินค้า</p>
        </div>
        <div className="flex gap-3">
          <button
            onClick={() => refetch()}
            className="flex items-center gap-2 px-3 py-2 text-sm text-slate-600 bg-white border border-slate-200 rounded-xl hover:bg-slate-50 transition-all"
          >
            <RefreshCw className="w-4 h-4" />
            รีเฟรช
          </button>
          <button
            onClick={() => navigate('/pos')}
            className="flex items-center gap-2 px-4 py-2 text-sm font-semibold text-white rounded-xl transition-all active:scale-95"
            style={{ background: 'linear-gradient(135deg, #10b981, #0d9488)' }}
          >
            <ShoppingCart className="w-4 h-4" />
            เปิดหน้าขาย
          </button>
        </div>
      </div>

      {/* KPI Cards */}
      {isLoading ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {[1,2,3,4].map(i => (
            <div key={i} className="bg-white rounded-2xl p-5 h-32 animate-pulse">
              <div className="h-4 bg-slate-200 rounded w-1/2 mb-3" />
              <div className="h-7 bg-slate-200 rounded w-3/4 mb-2" />
              <div className="h-3 bg-slate-200 rounded w-1/3" />
            </div>
          ))}
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {kpis.map((kpi) => (
            <button
              key={kpi.label}
              onClick={() => navigate(kpi.link)}
              className={`bg-gradient-to-br ${kpi.bg} rounded-2xl p-5 text-left border border-white shadow-sm hover:shadow-md transition-all active:scale-95 group`}
            >
              <div className="flex items-start justify-between mb-3">
                <div className={`p-2.5 rounded-xl bg-gradient-to-br ${kpi.gradient} shadow-md`}>
                  <kpi.icon className="w-5 h-5 text-white" />
                </div>
                <ArrowRight className={`w-4 h-4 ${kpi.text} opacity-0 group-hover:opacity-100 transition-opacity mt-1`} />
              </div>
              <p className="text-xs font-medium text-slate-500 mb-1">{kpi.label}</p>
              <p className={`text-2xl font-bold ${kpi.text}`}>{kpi.value}</p>
              <p className="text-xs text-slate-400 mt-0.5">{kpi.sub}</p>
            </button>
          ))}
        </div>
      )}

      {/* Chart */}
      <div className="bg-white rounded-2xl shadow-sm border border-slate-100 p-6">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-base font-semibold text-slate-700">ยอดขาย 30 วันที่ผ่านมา</h2>
          <span className="text-xs text-slate-400 bg-slate-100 px-3 py-1 rounded-full">รายวัน</span>
        </div>
        {dailySales && dailySales.length > 0 ? (
          <ResponsiveContainer width="100%" height={260}>
            <BarChart data={dailySales} barSize={14}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" vertical={false} />
              <XAxis dataKey="date" tick={{ fontSize: 10, fill: '#94a3b8' }} axisLine={false} tickLine={false} />
              <YAxis tick={{ fontSize: 10, fill: '#94a3b8' }} tickFormatter={(v) => `฿${(v/1000).toFixed(0)}K`} axisLine={false} tickLine={false} />
              <Tooltip
                formatter={(v: number) => [formatCurrency(v), 'ยอดขาย']}
                contentStyle={{ borderRadius: '12px', border: 'none', boxShadow: '0 4px 20px rgba(0,0,0,0.1)', fontSize: '12px' }}
              />
              <Bar dataKey="total_sales" fill="url(#barGradient)" radius={[6, 6, 0, 0]} />
              <defs>
                <linearGradient id="barGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#10b981" />
                  <stop offset="100%" stopColor="#0d9488" />
                </linearGradient>
              </defs>
            </BarChart>
          </ResponsiveContainer>
        ) : (
          <div className="flex flex-col items-center justify-center h-64 text-slate-400">
            <TrendingUp className="w-12 h-12 mb-3 opacity-30" />
            <p className="text-sm">ยังไม่มีข้อมูลยอดขาย</p>
          </div>
        )}
      </div>
    </div>
  );
}
