import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { productApi } from '../services/api';
import { Product } from '../types';
import { formatCurrency } from '../utils/format';
import { Plus, Search, Package, QrCode, Edit } from 'lucide-react';
import toast from 'react-hot-toast';

export default function ProductsPage() {
  const [search, setSearch] = useState('');
  const [showForm, setShowForm] = useState(false);
  const [editProduct, setEditProduct] = useState<Product | null>(null);
  const qc = useQueryClient();

  const { data: products, isLoading } = useQuery({
    queryKey: ['products-list', search],
    queryFn: () => productApi.list({ search, limit: 200 }),
    select: (r) => r.data,
  });

  return (
    <div className="p-6">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold text-gray-800">จัดการสินค้า</h1>
        <button
          onClick={() => { setEditProduct(null); setShowForm(true); }}
          className="flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-xl hover:bg-green-700 text-sm font-medium"
        >
          <Plus className="w-4 h-4" />
          เพิ่มสินค้า
        </button>
      </div>

      {/* Search */}
      <div className="relative mb-4">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 w-4 h-4" />
        <input
          type="text"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="ค้นหาชื่อ รหัส บาร์โค้ด..."
          className="pl-10 pr-4 py-2.5 border rounded-xl w-full max-w-md text-sm focus:ring-2 focus:ring-green-500 focus:outline-none"
        />
      </div>

      {/* Table */}
      <div className="bg-white rounded-xl shadow-sm overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-gray-50 border-b">
            <tr>
              <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase">สินค้า</th>
              <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase">รหัส</th>
              <th className="px-4 py-3 text-right text-xs font-semibold text-gray-500 uppercase">ราคาทุน</th>
              <th className="px-4 py-3 text-right text-xs font-semibold text-gray-500 uppercase">ราคาขาย</th>
              <th className="px-4 py-3 text-center text-xs font-semibold text-gray-500 uppercase">หน่วย</th>
              <th className="px-4 py-3 text-center text-xs font-semibold text-gray-500 uppercase">สถานะ</th>
              <th className="px-4 py-3 text-center text-xs font-semibold text-gray-500 uppercase">QR</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {isLoading ? (
              <tr><td colSpan={7} className="text-center py-8 text-gray-400">กำลังโหลด...</td></tr>
            ) : products?.length === 0 ? (
              <tr><td colSpan={7} className="text-center py-8 text-gray-400">ไม่พบสินค้า</td></tr>
            ) : (
              products?.map((p: Product) => (
                <tr key={p.id} className="hover:bg-gray-50 transition-colors">
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-3">
                      {p.main_image_url ? (
                        <img src={p.main_image_url} className="w-10 h-10 rounded-lg object-cover" alt="" />
                      ) : (
                        <div className="w-10 h-10 bg-gray-100 rounded-lg flex items-center justify-center">
                          <Package className="w-5 h-5 text-gray-300" />
                        </div>
                      )}
                      <div>
                        <p className="font-medium text-gray-800">{p.name}</p>
                        {p.chemical_registration && (
                          <p className="text-xs text-blue-500">ทะเบียน: {p.chemical_registration}</p>
                        )}
                      </div>
                    </div>
                  </td>
                  <td className="px-4 py-3 font-mono text-gray-500">{p.code}</td>
                  <td className="px-4 py-3 text-right text-gray-600">{formatCurrency(p.cost_price)}</td>
                  <td className="px-4 py-3 text-right font-semibold text-green-600">{formatCurrency(p.selling_price)}</td>
                  <td className="px-4 py-3 text-center text-gray-500">{p.unit}</td>
                  <td className="px-4 py-3 text-center">
                    <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${p.is_active ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-500'}`}>
                      {p.is_active ? 'ใช้งาน' : 'ปิด'}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-center">
                    <button
                      onClick={() => {
                        productApi.getQR(p.id).then((r) => {
                          const w = window.open('');
                          w?.document.write(`<img src="${r.data.qr_image_base64}" /><p>${p.name} (${p.code})</p>`);
                        });
                      }}
                      className="text-blue-500 hover:text-blue-700"
                    >
                      <QrCode className="w-4 h-4" />
                    </button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
