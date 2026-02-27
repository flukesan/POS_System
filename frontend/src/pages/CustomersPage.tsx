import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { customerApi } from '../services/api';
import { Customer } from '../types';
import { formatCurrency, formatDate } from '../utils/format';
import { Search, UserPlus, CreditCard, AlertTriangle, CheckCircle } from 'lucide-react';

export default function CustomersPage() {
  const [search, setSearch] = useState('');
  const [selectedCustomer, setSelectedCustomer] = useState<Customer | null>(null);

  const { data: customers, isLoading } = useQuery({
    queryKey: ['customers', search],
    queryFn: () => customerApi.list({ search, limit: 100 }),
    select: (r) => r.data,
  });

  const { data: creditSummary } = useQuery({
    queryKey: ['credit-summary', selectedCustomer?.id],
    queryFn: () => customerApi.creditSummary(selectedCustomer!.id),
    select: (r) => r.data,
    enabled: !!selectedCustomer,
  });

  const creditStatusBadge: Record<string, { label: string; cls: string; icon: React.ReactNode }> = {
    active: { label: 'ปกติ', cls: 'bg-green-100 text-green-700', icon: <CheckCircle className="w-3.5 h-3.5" /> },
    overdue: { label: 'เกินกำหนด', cls: 'bg-red-100 text-red-700', icon: <AlertTriangle className="w-3.5 h-3.5" /> },
    suspended: { label: 'ระงับ', cls: 'bg-gray-100 text-gray-600', icon: null },
  };

  return (
    <div className="p-6 flex gap-6">
      {/* Customer List */}
      <div className="flex-1 min-w-0">
        <div className="flex items-center justify-between mb-6">
          <h1 className="text-2xl font-bold text-gray-800">ลูกค้า / เครดิต</h1>
          <button className="flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-xl hover:bg-green-700 text-sm font-medium">
            <UserPlus className="w-4 h-4" />
            เพิ่มลูกค้า
          </button>
        </div>

        <div className="relative mb-4">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 w-4 h-4" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="ค้นหาชื่อ / เบอร์โทร / รหัสลูกค้า..."
            className="pl-10 pr-4 py-2.5 border rounded-xl w-full text-sm focus:ring-2 focus:ring-green-500 focus:outline-none"
          />
        </div>

        <div className="bg-white rounded-xl shadow-sm overflow-hidden">
          <table className="w-full text-sm">
            <thead className="bg-gray-50 border-b">
              <tr>
                <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase">ลูกค้า</th>
                <th className="px-4 py-3 text-right text-xs font-semibold text-gray-500 uppercase">วงเงินเครดิต</th>
                <th className="px-4 py-3 text-right text-xs font-semibold text-gray-500 uppercase">ยอดค้าง</th>
                <th className="px-4 py-3 text-center text-xs font-semibold text-gray-500 uppercase">สถานะ</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {isLoading ? (
                <tr><td colSpan={4} className="text-center py-8 text-gray-400">กำลังโหลด...</td></tr>
              ) : customers?.map((c: Customer) => {
                const badge = creditStatusBadge[c.credit_status] || creditStatusBadge.active;
                return (
                  <tr
                    key={c.id}
                    className={`hover:bg-green-50 cursor-pointer transition-colors ${selectedCustomer?.id === c.id ? 'bg-green-50' : ''}`}
                    onClick={() => setSelectedCustomer(c)}
                  >
                    <td className="px-4 py-3">
                      <p className="font-medium text-gray-800">{c.name}</p>
                      <p className="text-xs text-gray-400">{c.code} · {c.phone}</p>
                    </td>
                    <td className="px-4 py-3 text-right">
                      {c.credit_limit > 0 ? (
                        <div className="flex items-center justify-end gap-1">
                          <CreditCard className="w-3.5 h-3.5 text-gray-400" />
                          <span>{formatCurrency(c.credit_limit)}</span>
                        </div>
                      ) : '-'}
                    </td>
                    <td className="px-4 py-3 text-right">
                      {c.credit_balance > 0 ? (
                        <span className={c.credit_status === 'overdue' ? 'text-red-600 font-bold' : 'text-orange-500 font-semibold'}>
                          {formatCurrency(c.credit_balance)}
                        </span>
                      ) : <span className="text-gray-300">-</span>}
                    </td>
                    <td className="px-4 py-3 text-center">
                      <span className={`inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-medium ${badge.cls}`}>
                        {badge.icon}{badge.label}
                      </span>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      {/* Customer Detail Panel */}
      {selectedCustomer && creditSummary && (
        <div className="w-72 shrink-0">
          <div className="bg-white rounded-xl shadow-sm p-5 sticky top-6">
            <h3 className="font-bold text-gray-800 mb-4">{selectedCustomer.name}</h3>
            <div className="space-y-3 text-sm">
              <InfoRow label="รหัส" value={selectedCustomer.code} />
              <InfoRow label="เบอร์โทร" value={selectedCustomer.phone || '-'} />
              <InfoRow label="ที่อยู่" value={selectedCustomer.address || '-'} />
              <InfoRow label="วงเงินเครดิต" value={formatCurrency(creditSummary.credit_limit)} />
              <InfoRow label="ยอดค้าง" value={formatCurrency(creditSummary.credit_balance)} />
              <InfoRow label="วงเงินคงเหลือ" value={formatCurrency(creditSummary.available_credit)} highlight />
              {creditSummary.overdue_amount > 0 && (
                <InfoRow label="ยอดเกินกำหนด" value={formatCurrency(creditSummary.overdue_amount)} danger />
              )}
              <InfoRow label="ออเดอร์ค้าง" value={`${creditSummary.outstanding_orders} รายการ`} />
            </div>

            {creditSummary.credit_balance > 0 && (
              <button className="w-full mt-4 py-2.5 bg-blue-600 text-white rounded-xl text-sm font-semibold hover:bg-blue-700">
                บันทึกรับชำระเครดิต
              </button>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

function InfoRow({ label, value, highlight, danger }: { label: string; value: string; highlight?: boolean; danger?: boolean }) {
  return (
    <div className="flex justify-between">
      <span className="text-gray-400">{label}</span>
      <span className={`font-medium ${danger ? 'text-red-600' : highlight ? 'text-green-600' : 'text-gray-700'}`}>{value}</span>
    </div>
  );
}
