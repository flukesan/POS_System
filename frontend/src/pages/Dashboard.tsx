import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { reportApi } from '../services/api';
import { formatCurrency } from '../utils/format';
import { ShoppingCart, TrendingUp, AlertTriangle, CreditCard, Users, Package } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

export default function Dashboard() {
  const { data: stats } = useQuery({
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
          color: 'bg-green-500',
        },
        {
          label: 'ยอดขายเดือนนี้',
          value: formatCurrency(stats.this_month.total_sales),
          sub: `${stats.this_month.order_count} รายการ`,
          icon: TrendingUp,
          color: 'bg-blue-500',
        },
        {
          label: 'สินค้าใกล้หมด',
          value: stats.low_stock_products,
          sub: 'รายการ',
          icon: AlertTriangle,
          color: 'bg-orange-500',
        },
        {
          label: 'ยอดเครดิตค้างชำระ',
          value: formatCurrency(stats.total_outstanding_credit),
          sub: `ลูกค้าเกินกำหนด ${stats.overdue_customers} ราย`,
          icon: CreditCard,
          color: 'bg-red-500',
        },
      ]
    : [];

  return (
    <div className="p-6 space-y-6">
      <h1 className="text-2xl font-bold text-gray-800">แดชบอร์ด</h1>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {kpis.map((kpi) => (
          <div key={kpi.label} className="bg-white rounded-xl shadow-sm p-5 flex items-start gap-4">
            <div className={`${kpi.color} p-3 rounded-xl`}>
              <kpi.icon className="w-6 h-6 text-white" />
            </div>
            <div>
              <p className="text-sm text-gray-500">{kpi.label}</p>
              <p className="text-xl font-bold text-gray-800">{kpi.value}</p>
              <p className="text-xs text-gray-400">{kpi.sub}</p>
            </div>
          </div>
        ))}
      </div>

      {/* Sales Chart */}
      <div className="bg-white rounded-xl shadow-sm p-5">
        <h2 className="text-lg font-semibold text-gray-700 mb-4">ยอดขาย 30 วันที่ผ่านมา</h2>
        <ResponsiveContainer width="100%" height={280}>
          <BarChart data={dailySales || []}>
            <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
            <XAxis dataKey="date" tick={{ fontSize: 11 }} />
            <YAxis tick={{ fontSize: 11 }} tickFormatter={(v) => `฿${(v / 1000).toFixed(0)}K`} />
            <Tooltip formatter={(v: number) => [formatCurrency(v), 'ยอดขาย']} />
            <Bar dataKey="total_sales" fill="#16a34a" radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
