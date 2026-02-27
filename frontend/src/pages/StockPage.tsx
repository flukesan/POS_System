import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { stockApi } from '../services/api';
import { StockItem } from '../types';
import { formatNumber } from '../utils/format';
import { AlertTriangle, Package, TrendingDown, Warehouse, ArrowDownToLine } from 'lucide-react';

type Tab = 'stock' | 'receive' | 'alerts';

export default function StockPage() {
  const [tab, setTab] = useState<Tab>('stock');
  const [search, setSearch] = useState('');
  const [lowOnly, setLowOnly] = useState(false);

  const { data: stockItems, isLoading } = useQuery({
    queryKey: ['stock', lowOnly],
    queryFn: () => stockApi.list({ low_stock_only: lowOnly }),
    select: (r) => r.data,
  });

  const { data: alerts } = useQuery({
    queryKey: ['low-stock-alerts'],
    queryFn: () => stockApi.lowStockAlerts(),
    select: (r) => r.data,
  });

  const filtered = stockItems?.filter((s: StockItem) =>
    !search || s.product_name.toLowerCase().includes(search.toLowerCase()) || s.product_code.includes(search)
  );

  const tabs: { id: Tab; label: string; icon: React.ReactNode }[] = [
    { id: 'stock', label: 'สต๊อกปัจจุบัน', icon: <Package className="w-4 h-4" /> },
    { id: 'receive', label: 'รับของเข้า', icon: <ArrowDownToLine className="w-4 h-4" /> },
    { id: 'alerts', label: `แจ้งเตือน (${alerts?.length || 0})`, icon: <AlertTriangle className="w-4 h-4" /> },
  ];

  return (
    <div className="p-6">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold text-gray-800">สต๊อกสินค้า</h1>
      </div>

      {/* Tabs */}
      <div className="flex gap-1 mb-6 bg-gray-100 p-1 rounded-xl w-fit">
        {tabs.map((t) => (
          <button
            key={t.id}
            onClick={() => setTab(t.id)}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all ${
              tab === t.id ? 'bg-white shadow text-gray-800' : 'text-gray-500 hover:text-gray-700'
            }`}
          >
            {t.icon}{t.label}
          </button>
        ))}
      </div>

      {tab === 'stock' && (
        <>
          <div className="flex gap-3 mb-4">
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="ค้นหาสินค้า..."
              className="px-4 py-2 border rounded-xl text-sm focus:ring-2 focus:ring-green-500 focus:outline-none flex-1 max-w-sm"
            />
            <label className="flex items-center gap-2 text-sm text-gray-600 cursor-pointer">
              <input type="checkbox" checked={lowOnly} onChange={(e) => setLowOnly(e.target.checked)} className="rounded" />
              แสดงเฉพาะสินค้าใกล้หมด
            </label>
          </div>

          <div className="bg-white rounded-xl shadow-sm overflow-hidden">
            <table className="w-full text-sm">
              <thead className="bg-gray-50 border-b">
                <tr>
                  <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase">สินค้า</th>
                  <th className="px-4 py-3 text-center text-xs font-semibold text-gray-500 uppercase">คงเหลือ</th>
                  <th className="px-4 py-3 text-center text-xs font-semibold text-gray-500 uppercase">จอง</th>
                  <th className="px-4 py-3 text-center text-xs font-semibold text-gray-500 uppercase">พร้อมขาย</th>
                  <th className="px-4 py-3 text-center text-xs font-semibold text-gray-500 uppercase">จุดสั่งซื้อ</th>
                  <th className="px-4 py-3 text-center text-xs font-semibold text-gray-500 uppercase">สถานะ</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {isLoading ? (
                  <tr><td colSpan={6} className="text-center py-8 text-gray-400">กำลังโหลด...</td></tr>
                ) : filtered?.map((item: StockItem) => (
                  <tr key={item.stock_id} className={`hover:bg-gray-50 ${item.is_low ? 'bg-red-50/50' : ''}`}>
                    <td className="px-4 py-3">
                      <p className="font-medium text-gray-800">{item.product_name}</p>
                      <p className="text-xs text-gray-400 font-mono">{item.product_code}</p>
                    </td>
                    <td className="px-4 py-3 text-center font-bold">{formatNumber(item.quantity, 0)} {item.unit}</td>
                    <td className="px-4 py-3 text-center text-orange-500">{formatNumber(item.reserved, 0)}</td>
                    <td className="px-4 py-3 text-center text-green-600 font-semibold">{formatNumber(item.available, 0)}</td>
                    <td className="px-4 py-3 text-center text-gray-400">{item.reorder_point}</td>
                    <td className="px-4 py-3 text-center">
                      {item.is_low ? (
                        <span className="flex items-center justify-center gap-1 text-red-600 text-xs font-medium">
                          <TrendingDown className="w-3.5 h-3.5" />ใกล้หมด
                        </span>
                      ) : (
                        <span className="text-green-600 text-xs font-medium">ปกติ</span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </>
      )}

      {tab === 'alerts' && (
        <div className="space-y-3">
          {alerts?.length === 0 ? (
            <div className="text-center py-12 text-gray-400">
              <Package className="w-12 h-12 mx-auto mb-2 opacity-30" />
              <p>ไม่มีสินค้าใกล้หมด</p>
            </div>
          ) : (
            alerts?.map((item: any) => (
              <div key={item.product_id} className="bg-white rounded-xl p-4 shadow-sm border-l-4 border-red-400 flex items-center justify-between">
                <div>
                  <p className="font-medium text-gray-800">{item.product_name}</p>
                  <p className="text-sm text-gray-400">{item.product_code}</p>
                </div>
                <div className="text-right">
                  <p className="text-red-600 font-bold">{item.current_stock} ชิ้น</p>
                  <p className="text-xs text-gray-400">ต้องสั่งเมื่อ ≤ {item.reorder_point}</p>
                </div>
              </div>
            ))
          )}
        </div>
      )}

      {tab === 'receive' && (
        <div className="bg-white rounded-xl shadow-sm p-6">
          <h2 className="text-lg font-semibold text-gray-700 mb-4">บันทึกรับสินค้า</h2>
          <p className="text-gray-400 text-sm">ฟีเจอร์นี้จะเปิดตัวฟอร์มสร้าง Purchase Order</p>
        </div>
      )}
    </div>
  );
}
