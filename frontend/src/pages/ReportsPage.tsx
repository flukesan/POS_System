import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { reportApi } from '../services/api';
import { formatCurrency, formatNumber } from '../utils/format';
import { BarChart2, TrendingUp, Package, CreditCard } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell, Legend } from 'recharts';

type ReportTab = 'sales' | 'products' | 'credit' | 'stock';

const COLORS = ['#16a34a', '#2563eb', '#ea580c', '#7c3aed', '#dc2626', '#0891b2'];

export default function ReportsPage() {
  const [tab, setTab] = useState<ReportTab>('sales');

  const { data: dailySales } = useQuery({
    queryKey: ['report-daily'],
    queryFn: () => reportApi.dailySales(),
    select: (r) => r.data,
    enabled: tab === 'sales',
  });

  const { data: topProducts } = useQuery({
    queryKey: ['report-top-products'],
    queryFn: () => reportApi.topProducts({ limit: 10 }),
    select: (r) => r.data,
    enabled: tab === 'products',
  });

  const { data: creditReport } = useQuery({
    queryKey: ['report-credit'],
    queryFn: () => reportApi.outstandingCredit(),
    select: (r) => r.data,
    enabled: tab === 'credit',
  });

  const { data: stockValuation } = useQuery({
    queryKey: ['report-stock'],
    queryFn: () => reportApi.stockValuation(),
    select: (r) => r.data,
    enabled: tab === 'stock',
  });

  const tabs = [
    { id: 'sales' as ReportTab, label: 'ยอดขาย', icon: BarChart2 },
    { id: 'products' as ReportTab, label: 'สินค้าขายดี', icon: TrendingUp },
    { id: 'credit' as ReportTab, label: 'เครดิตค้างชำระ', icon: CreditCard },
    { id: 'stock' as ReportTab, label: 'มูลค่าสต๊อก', icon: Package },
  ];

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold text-gray-800 mb-6">รายงาน</h1>

      <div className="flex gap-1 mb-6 bg-gray-100 p-1 rounded-xl w-fit">
        {tabs.map(({ id, label, icon: Icon }) => (
          <button
            key={id}
            onClick={() => setTab(id)}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all ${
              tab === id ? 'bg-white shadow text-gray-800' : 'text-gray-500 hover:text-gray-700'
            }`}
          >
            <Icon className="w-4 h-4" />{label}
          </button>
        ))}
      </div>

      {tab === 'sales' && (
        <div className="bg-white rounded-xl shadow-sm p-6">
          <h2 className="text-lg font-semibold mb-4">ยอดขายรายวัน (30 วัน)</h2>
          <ResponsiveContainer width="100%" height={350}>
            <BarChart data={dailySales || []}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis dataKey="date" tick={{ fontSize: 11 }} />
              <YAxis tick={{ fontSize: 11 }} tickFormatter={(v) => `฿${(v / 1000).toFixed(0)}K`} />
              <Tooltip formatter={(v: number) => [formatCurrency(v), 'ยอดขาย']} />
              <Bar dataKey="total_sales" fill="#16a34a" radius={[4, 4, 0, 0]} name="ยอดขาย" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}

      {tab === 'products' && topProducts && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="bg-white rounded-xl shadow-sm p-6">
            <h2 className="text-lg font-semibold mb-4">สินค้าขายดีสูงสุด (ยอดขาย)</h2>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={topProducts} layout="vertical">
                <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                <XAxis type="number" tick={{ fontSize: 11 }} tickFormatter={(v) => `฿${(v / 1000).toFixed(0)}K`} />
                <YAxis dataKey="product_name" type="category" width={120} tick={{ fontSize: 11 }} />
                <Tooltip formatter={(v: number) => [formatCurrency(v), 'รายได้']} />
                <Bar dataKey="total_revenue" fill="#2563eb" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
          <div className="bg-white rounded-xl shadow-sm p-6">
            <h2 className="text-lg font-semibold mb-4">สัดส่วนรายได้</h2>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie data={topProducts?.slice(0, 6)} dataKey="total_revenue" nameKey="product_name" cx="50%" cy="50%" outerRadius={100} label>
                  {topProducts?.slice(0, 6).map((_: any, i: number) => (
                    <Cell key={i} fill={COLORS[i % COLORS.length]} />
                  ))}
                </Pie>
                <Legend />
                <Tooltip formatter={(v: number) => formatCurrency(v)} />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}

      {tab === 'credit' && creditReport && (
        <div className="space-y-4">
          <div className="grid grid-cols-3 gap-4">
            <div className="bg-white rounded-xl p-4 shadow-sm text-center">
              <p className="text-sm text-gray-500">ยอดค้างทั้งหมด</p>
              <p className="text-2xl font-bold text-red-600">{formatCurrency(creditReport.total_outstanding)}</p>
            </div>
            <div className="bg-white rounded-xl p-4 shadow-sm text-center">
              <p className="text-sm text-gray-500">จำนวนลูกค้า</p>
              <p className="text-2xl font-bold text-gray-800">{creditReport.total_customers} ราย</p>
            </div>
            <div className="bg-white rounded-xl p-4 shadow-sm text-center">
              <p className="text-sm text-gray-500">เกินกำหนด</p>
              <p className="text-2xl font-bold text-orange-600">{creditReport.overdue_customers} ราย</p>
            </div>
          </div>
          <div className="bg-white rounded-xl shadow-sm overflow-hidden">
            <table className="w-full text-sm">
              <thead className="bg-gray-50 border-b">
                <tr>
                  <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase">ลูกค้า</th>
                  <th className="px-4 py-3 text-right text-xs font-semibold text-gray-500 uppercase">วงเงิน</th>
                  <th className="px-4 py-3 text-right text-xs font-semibold text-gray-500 uppercase">ค้างชำระ</th>
                  <th className="px-4 py-3 text-right text-xs font-semibold text-gray-500 uppercase">คงเหลือ</th>
                  <th className="px-4 py-3 text-center text-xs font-semibold text-gray-500 uppercase">สถานะ</th>
                </tr>
              </thead>
              <tbody className="divide-y">
                {creditReport.customers.map((c: any) => (
                  <tr key={c.id} className={`hover:bg-gray-50 ${c.credit_status === 'overdue' ? 'bg-red-50/30' : ''}`}>
                    <td className="px-4 py-3">
                      <p className="font-medium text-gray-800">{c.name}</p>
                      <p className="text-xs text-gray-400">{c.code}</p>
                    </td>
                    <td className="px-4 py-3 text-right text-gray-600">{formatCurrency(c.credit_limit)}</td>
                    <td className="px-4 py-3 text-right font-bold text-red-600">{formatCurrency(c.credit_balance)}</td>
                    <td className="px-4 py-3 text-right text-green-600">{formatCurrency(c.available_credit)}</td>
                    <td className="px-4 py-3 text-center">
                      <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${c.credit_status === 'overdue' ? 'bg-red-100 text-red-700' : 'bg-green-100 text-green-700'}`}>
                        {c.credit_status === 'overdue' ? 'เกินกำหนด' : 'ปกติ'}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {tab === 'stock' && stockValuation && (
        <div className="space-y-4">
          <div className="grid grid-cols-3 gap-4">
            <div className="bg-white rounded-xl p-4 shadow-sm text-center">
              <p className="text-sm text-gray-500">มูลค่าทุน</p>
              <p className="text-2xl font-bold text-blue-600">{formatCurrency(stockValuation.total_cost_value)}</p>
            </div>
            <div className="bg-white rounded-xl p-4 shadow-sm text-center">
              <p className="text-sm text-gray-500">มูลค่าขาย</p>
              <p className="text-2xl font-bold text-green-600">{formatCurrency(stockValuation.total_selling_value)}</p>
            </div>
            <div className="bg-white rounded-xl p-4 shadow-sm text-center">
              <p className="text-sm text-gray-500">กำไรที่เป็นไปได้</p>
              <p className="text-2xl font-bold text-purple-600">{formatCurrency(stockValuation.potential_profit)}</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
