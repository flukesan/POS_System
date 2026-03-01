import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { productApi, categoryApi } from '../services/api';
import { Product, Category } from '../types';
import { formatCurrency } from '../utils/format';
import { Plus, Search, Package, QrCode, Edit2, X, Save, Loader2, Tag } from 'lucide-react';
import toast from 'react-hot-toast';

const UNITS = ['kg', 'g', 'l', 'ml', 'bag', 'box', 'piece', 'set', 'bottle', 'pack'];

interface FormData {
  code: string; name: string; category_id: string; unit: string;
  cost_price: string; selling_price: string;
  min_stock_level: string; reorder_point: string;
  chemical_registration: string; description: string; is_active: boolean;
}

const emptyForm: FormData = {
  code: '', name: '', category_id: '', unit: 'piece',
  cost_price: '0', selling_price: '0',
  min_stock_level: '5', reorder_point: '10',
  chemical_registration: '', description: '', is_active: true,
};

function ProductFormModal({ product, onClose }: { product: Product | null; onClose: () => void }) {
  const qc = useQueryClient();
  const [form, setForm] = useState<FormData>(
    product ? {
      code: product.code, name: product.name, category_id: product.category_id || '',
      unit: product.unit, cost_price: String(product.cost_price),
      selling_price: String(product.selling_price),
      min_stock_level: String(product.min_stock_level),
      reorder_point: String(product.reorder_point),
      chemical_registration: product.chemical_registration || '',
      description: product.description || '', is_active: product.is_active,
    } : emptyForm
  );

  const { data: categories } = useQuery({
    queryKey: ['categories'],
    queryFn: () => categoryApi.list(),
    select: (r) => r.data as Category[],
  });

  const set = (field: keyof FormData, value: string | boolean) =>
    setForm((f) => ({ ...f, [field]: value }));

  const mutation = useMutation({
    mutationFn: (data: object) =>
      product ? productApi.update(product.id, data) : productApi.create(data),
    onSuccess: () => {
      toast.success(product ? 'แก้ไขสินค้าสำเร็จ' : 'เพิ่มสินค้าสำเร็จ');
      qc.invalidateQueries({ queryKey: ['products-list'] });
      onClose();
    },
    onError: (err: any) => {
      const msg = err?.response?.data?.detail || 'เกิดข้อผิดพลาด';
      toast.error(typeof msg === 'string' ? msg : JSON.stringify(msg));
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!form.code || !form.name) { toast.error('กรุณากรอกรหัสและชื่อสินค้า'); return; }
    mutation.mutate({
      code: form.code, name: form.name,
      category_id: form.category_id || null, unit: form.unit,
      cost_price: parseFloat(form.cost_price) || 0,
      selling_price: parseFloat(form.selling_price) || 0,
      min_stock_level: parseInt(form.min_stock_level) || 5,
      reorder_point: parseInt(form.reorder_point) || 10,
      chemical_registration: form.chemical_registration || null,
      description: form.description || null, is_active: form.is_active,
    });
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm">
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-2xl max-h-[90vh] overflow-y-auto">
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-100">
          <h2 className="text-lg font-bold text-slate-800">{product ? 'แก้ไขสินค้า' : 'เพิ่มสินค้าใหม่'}</h2>
          <button onClick={onClose} className="p-1.5 hover:bg-slate-100 rounded-lg transition-colors">
            <X className="w-5 h-5 text-slate-500" />
          </button>
        </div>
        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold text-slate-600 mb-1.5">รหัสสินค้า *</label>
              <input value={form.code} onChange={(e) => set('code', e.target.value)}
                placeholder="เช่น PRD-001" className="w-full px-3.5 py-2.5 border border-slate-200 rounded-xl text-sm focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 focus:outline-none" required />
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-600 mb-1.5">หน่วย *</label>
              <select value={form.unit} onChange={(e) => set('unit', e.target.value)}
                className="w-full px-3.5 py-2.5 border border-slate-200 rounded-xl text-sm focus:ring-2 focus:ring-emerald-500 focus:outline-none bg-white">
                {UNITS.map((u) => <option key={u} value={u}>{u}</option>)}
              </select>
            </div>
          </div>
          <div>
            <label className="block text-xs font-semibold text-slate-600 mb-1.5">ชื่อสินค้า *</label>
            <input value={form.name} onChange={(e) => set('name', e.target.value)}
              placeholder="ชื่อสินค้า" className="w-full px-3.5 py-2.5 border border-slate-200 rounded-xl text-sm focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 focus:outline-none" required />
          </div>
          <div>
            <label className="block text-xs font-semibold text-slate-600 mb-1.5">หมวดหมู่</label>
            <select value={form.category_id} onChange={(e) => set('category_id', e.target.value)}
              className="w-full px-3.5 py-2.5 border border-slate-200 rounded-xl text-sm focus:ring-2 focus:ring-emerald-500 focus:outline-none bg-white">
              <option value="">-- ไม่ระบุ --</option>
              {categories?.map((c) => <option key={c.id} value={c.id}>{c.name}</option>)}
            </select>
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold text-slate-600 mb-1.5">ราคาทุน (บาท)</label>
              <input type="number" min="0" step="0.01" value={form.cost_price}
                onChange={(e) => set('cost_price', e.target.value)}
                className="w-full px-3.5 py-2.5 border border-slate-200 rounded-xl text-sm focus:ring-2 focus:ring-emerald-500 focus:outline-none" />
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-600 mb-1.5">ราคาขาย (บาท) *</label>
              <input type="number" min="0" step="0.01" value={form.selling_price}
                onChange={(e) => set('selling_price', e.target.value)}
                className="w-full px-3.5 py-2.5 border border-slate-200 rounded-xl text-sm focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 focus:outline-none" required />
            </div>
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold text-slate-600 mb-1.5">สต๊อกขั้นต่ำ</label>
              <input type="number" min="0" value={form.min_stock_level}
                onChange={(e) => set('min_stock_level', e.target.value)}
                className="w-full px-3.5 py-2.5 border border-slate-200 rounded-xl text-sm focus:ring-2 focus:ring-emerald-500 focus:outline-none" />
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-600 mb-1.5">จุดสั่งซื้อ</label>
              <input type="number" min="0" value={form.reorder_point}
                onChange={(e) => set('reorder_point', e.target.value)}
                className="w-full px-3.5 py-2.5 border border-slate-200 rounded-xl text-sm focus:ring-2 focus:ring-emerald-500 focus:outline-none" />
            </div>
          </div>
          <div>
            <label className="block text-xs font-semibold text-slate-600 mb-1.5">ทะเบียนสารเคมี</label>
            <input value={form.chemical_registration} onChange={(e) => set('chemical_registration', e.target.value)}
              placeholder="เลขทะเบียน (ถ้ามี)"
              className="w-full px-3.5 py-2.5 border border-slate-200 rounded-xl text-sm focus:ring-2 focus:ring-emerald-500 focus:outline-none" />
          </div>
          <div>
            <label className="block text-xs font-semibold text-slate-600 mb-1.5">รายละเอียด</label>
            <textarea value={form.description} onChange={(e) => set('description', e.target.value)}
              rows={2} className="w-full px-3.5 py-2.5 border border-slate-200 rounded-xl text-sm focus:ring-2 focus:ring-emerald-500 focus:outline-none resize-none"
              placeholder="รายละเอียดสินค้า (ไม่บังคับ)" />
          </div>
          <label className="flex items-center gap-2 cursor-pointer">
            <input type="checkbox" checked={form.is_active} onChange={(e) => set('is_active', e.target.checked)}
              className="w-4 h-4 rounded accent-emerald-500" />
            <span className="text-sm text-slate-600">เปิดใช้งานสินค้า</span>
          </label>
          <div className="flex gap-3 pt-2">
            <button type="button" onClick={onClose}
              className="flex-1 py-2.5 border border-slate-200 rounded-xl text-sm font-medium text-slate-600 hover:bg-slate-50 transition-all">
              ยกเลิก
            </button>
            <button type="submit" disabled={mutation.isPending}
              className="flex-1 flex items-center justify-center gap-2 py-2.5 rounded-xl text-sm font-semibold text-white transition-all disabled:opacity-60 active:scale-95"
              style={{ background: 'linear-gradient(135deg, #10b981, #0d9488)' }}>
              {mutation.isPending ? <Loader2 className="w-4 h-4 animate-spin" /> : <Save className="w-4 h-4" />}
              {product ? 'บันทึกการแก้ไข' : 'เพิ่มสินค้า'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default function ProductsPage() {
  const [search, setSearch] = useState('');
  const [showForm, setShowForm] = useState(false);
  const [editProduct, setEditProduct] = useState<Product | null>(null);

  const { data: products, isLoading } = useQuery({
    queryKey: ['products-list', search],
    queryFn: () => productApi.list({ search, limit: 200 }),
    select: (r) => r.data,
  });

  const openAdd = () => { setEditProduct(null); setShowForm(true); };
  const openEdit = (p: Product) => { setEditProduct(p); setShowForm(true); };

  return (
    <div className="p-6 min-h-full bg-slate-50">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-slate-800">จัดการสินค้า</h1>
          <p className="text-sm text-slate-500 mt-0.5">รายการสินค้าทั้งหมด</p>
        </div>
        <button onClick={openAdd}
          className="flex items-center gap-2 px-4 py-2.5 text-white text-sm font-semibold rounded-xl transition-all active:scale-95 shadow-lg shadow-emerald-500/25"
          style={{ background: 'linear-gradient(135deg, #10b981, #0d9488)' }}>
          <Plus className="w-4 h-4" />เพิ่มสินค้า
        </button>
      </div>

      <div className="relative mb-4">
        <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400 w-4 h-4" />
        <input type="text" value={search} onChange={(e) => setSearch(e.target.value)}
          placeholder="ค้นหาชื่อ รหัส บาร์โค้ด..."
          className="pl-10 pr-4 py-2.5 border border-slate-200 rounded-xl w-full max-w-md text-sm bg-white focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 focus:outline-none" />
      </div>

      <div className="bg-white rounded-2xl shadow-sm border border-slate-100 overflow-hidden">
        <table className="w-full text-sm">
          <thead>
            <tr className="bg-slate-50 border-b border-slate-100">
              <th className="px-4 py-3.5 text-left text-xs font-bold text-slate-500 uppercase tracking-wider">สินค้า</th>
              <th className="px-4 py-3.5 text-left text-xs font-bold text-slate-500 uppercase tracking-wider">รหัส</th>
              <th className="px-4 py-3.5 text-left text-xs font-bold text-slate-500 uppercase tracking-wider">หมวดหมู่</th>
              <th className="px-4 py-3.5 text-right text-xs font-bold text-slate-500 uppercase tracking-wider">ราคาทุน</th>
              <th className="px-4 py-3.5 text-right text-xs font-bold text-slate-500 uppercase tracking-wider">ราคาขาย</th>
              <th className="px-4 py-3.5 text-center text-xs font-bold text-slate-500 uppercase tracking-wider">สถานะ</th>
              <th className="px-4 py-3.5 text-center text-xs font-bold text-slate-500 uppercase tracking-wider">จัดการ</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {isLoading ? (
              <tr><td colSpan={7} className="text-center py-12 text-slate-400">
                <Loader2 className="w-6 h-6 animate-spin mx-auto mb-2" />กำลังโหลด...
              </td></tr>
            ) : products?.length === 0 ? (
              <tr><td colSpan={7} className="text-center py-16 text-slate-400">
                <Package className="w-12 h-12 mx-auto mb-3 opacity-30" />
                <p>ไม่พบสินค้า</p>
                <button onClick={openAdd} className="mt-3 text-emerald-600 text-sm font-medium hover:underline">+ เพิ่มสินค้าแรก</button>
              </td></tr>
            ) : (
              products?.map((p: Product) => (
                <tr key={p.id} className="hover:bg-slate-50/60 transition-colors group">
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-3">
                      {p.main_image_url ? (
                        <img src={p.main_image_url} className="w-10 h-10 rounded-xl object-cover border border-slate-100" alt="" />
                      ) : (
                        <div className="w-10 h-10 bg-gradient-to-br from-slate-100 to-slate-200 rounded-xl flex items-center justify-center">
                          <Package className="w-5 h-5 text-slate-400" />
                        </div>
                      )}
                      <div>
                        <p className="font-semibold text-slate-800">{p.name}</p>
                        {p.chemical_registration && (
                          <span className="inline-flex items-center gap-1 text-xs text-blue-600 bg-blue-50 px-1.5 py-0.5 rounded-md mt-0.5">
                            <Tag className="w-3 h-3" />{p.chemical_registration}
                          </span>
                        )}
                      </div>
                    </div>
                  </td>
                  <td className="px-4 py-3 font-mono text-xs text-slate-500">{p.code}</td>
                  <td className="px-4 py-3 text-xs text-slate-500">{p.category?.name || '-'}</td>
                  <td className="px-4 py-3 text-right text-slate-500">{formatCurrency(p.cost_price)}</td>
                  <td className="px-4 py-3 text-right">
                    <span className="font-bold text-emerald-600">{formatCurrency(p.selling_price)}</span>
                    <span className="text-xs text-slate-400 ml-1">/{p.unit}</span>
                  </td>
                  <td className="px-4 py-3 text-center">
                    <span className={`px-2.5 py-1 rounded-full text-xs font-semibold ${p.is_active ? 'bg-emerald-100 text-emerald-700' : 'bg-slate-100 text-slate-500'}`}>
                      {p.is_active ? 'ใช้งาน' : 'ปิด'}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-center">
                    <div className="flex items-center justify-center gap-1.5 opacity-0 group-hover:opacity-100 transition-opacity">
                      <button onClick={() => openEdit(p)}
                        className="p-1.5 bg-indigo-100 text-indigo-600 rounded-lg hover:bg-indigo-200 transition-colors" title="แก้ไข">
                        <Edit2 className="w-3.5 h-3.5" />
                      </button>
                      <button
                        onClick={() => productApi.getQR(p.id).then((r) => {
                          const w = window.open(''); w?.document.write(`<img src="${r.data.qr_image_base64}" /><p>${p.name} (${p.code})</p>`);
                        })}
                        className="p-1.5 bg-sky-100 text-sky-600 rounded-lg hover:bg-sky-200 transition-colors" title="QR Code">
                        <QrCode className="w-3.5 h-3.5" />
                      </button>
                    </div>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
        {products && products.length > 0 && (
          <div className="px-4 py-2.5 bg-slate-50 border-t border-slate-100 text-xs text-slate-400">ทั้งหมด {products.length} รายการ</div>
        )}
      </div>

      {showForm && (
        <ProductFormModal product={editProduct} onClose={() => { setShowForm(false); setEditProduct(null); }} />
      )}
    </div>
  );
}
