import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { customerApi } from '../services/api';
import { Customer } from '../types';
import { formatCurrency } from '../utils/format';
import { Search, UserPlus, CreditCard, AlertTriangle, CheckCircle, X, Save, Loader2, Phone, MapPin, ChevronRight, Edit2 } from 'lucide-react';
import toast from 'react-hot-toast';

interface CustomerForm {
  name: string; phone: string; email: string; address: string;
  customer_type: string; credit_limit: string; credit_days: string;
}
const emptyForm: CustomerForm = { name: '', phone: '', email: '', address: '', customer_type: 'individual', credit_limit: '0', credit_days: '30' };

function CustomerFormModal({ customer, onClose }: { customer: Customer | null; onClose: () => void }) {
  const qc = useQueryClient();
  const [form, setForm] = useState<CustomerForm>(
    customer ? {
      name: customer.name, phone: customer.phone || '', email: customer.email || '',
      address: customer.address || '', customer_type: customer.customer_type,
      credit_limit: String(customer.credit_limit), credit_days: String(customer.credit_days),
    } : emptyForm
  );

  const set = (field: keyof CustomerForm, value: string) => setForm((f) => ({ ...f, [field]: value }));

  const mutation = useMutation({
    mutationFn: (data: object) => customer ? customerApi.update(customer.id, data) : customerApi.create(data),
    onSuccess: () => {
      toast.success(customer ? 'แก้ไขข้อมูลสำเร็จ' : 'เพิ่มลูกค้าสำเร็จ');
      qc.invalidateQueries({ queryKey: ['customers'] });
      onClose();
    },
    onError: (err: any) => toast.error(err?.response?.data?.detail || 'เกิดข้อผิดพลาด'),
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!form.name) { toast.error('กรุณากรอกชื่อลูกค้า'); return; }
    mutation.mutate({
      name: form.name, phone: form.phone || null, email: form.email || null,
      address: form.address || null, customer_type: form.customer_type,
      credit_limit: parseFloat(form.credit_limit) || 0,
      credit_days: parseInt(form.credit_days) || 30,
    });
  };

  const inputCls = "w-full px-3.5 py-2.5 border border-slate-200 rounded-xl text-sm focus:ring-2 focus:ring-violet-500 focus:border-violet-500 focus:outline-none";

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm">
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-lg">
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-100">
          <h2 className="text-lg font-bold text-slate-800">{customer ? 'แก้ไขข้อมูลลูกค้า' : 'เพิ่มลูกค้าใหม่'}</h2>
          <button onClick={onClose} className="p-1.5 hover:bg-slate-100 rounded-lg transition-colors">
            <X className="w-5 h-5 text-slate-500" />
          </button>
        </div>
        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          <div>
            <label className="block text-xs font-semibold text-slate-600 mb-1.5">ชื่อ-นามสกุล / ชื่อบริษัท *</label>
            <input value={form.name} onChange={(e) => set('name', e.target.value)} placeholder="ชื่อลูกค้า" className={inputCls} required />
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold text-slate-600 mb-1.5">เบอร์โทรศัพท์</label>
              <input value={form.phone} onChange={(e) => set('phone', e.target.value)} placeholder="08x-xxxxxxx" className={inputCls} />
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-600 mb-1.5">ประเภทลูกค้า</label>
              <select value={form.customer_type} onChange={(e) => set('customer_type', e.target.value)} className={inputCls + " bg-white"}>
                <option value="individual">บุคคลทั่วไป</option>
                <option value="corporate">นิติบุคคล</option>
                <option value="farmer">เกษตรกร</option>
              </select>
            </div>
          </div>
          <div>
            <label className="block text-xs font-semibold text-slate-600 mb-1.5">ที่อยู่</label>
            <textarea value={form.address} onChange={(e) => set('address', e.target.value)}
              rows={2} className={inputCls + " resize-none"} placeholder="ที่อยู่ (ไม่บังคับ)" />
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold text-slate-600 mb-1.5">วงเงินเครดิต (บาท)</label>
              <input type="number" min="0" value={form.credit_limit} onChange={(e) => set('credit_limit', e.target.value)} className={inputCls} />
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-600 mb-1.5">จำนวนวันเครดิต</label>
              <input type="number" min="0" value={form.credit_days} onChange={(e) => set('credit_days', e.target.value)} className={inputCls} />
            </div>
          </div>
          <div className="flex gap-3 pt-2">
            <button type="button" onClick={onClose}
              className="flex-1 py-2.5 border border-slate-200 rounded-xl text-sm font-medium text-slate-600 hover:bg-slate-50 transition-all">ยกเลิก</button>
            <button type="submit" disabled={mutation.isPending}
              className="flex-1 flex items-center justify-center gap-2 py-2.5 rounded-xl text-sm font-semibold text-white transition-all disabled:opacity-60 active:scale-95"
              style={{ background: 'linear-gradient(135deg, #6366f1, #8b5cf6)' }}>
              {mutation.isPending ? <Loader2 className="w-4 h-4 animate-spin" /> : <Save className="w-4 h-4" />}
              {customer ? 'บันทึก' : 'เพิ่มลูกค้า'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

const creditBadge: Record<string, { label: string; cls: string; icon: React.ReactNode }> = {
  active:    { label: 'ปกติ',      cls: 'bg-emerald-100 text-emerald-700', icon: <CheckCircle className="w-3 h-3" /> },
  overdue:   { label: 'เกินกำหนด', cls: 'bg-rose-100 text-rose-700',      icon: <AlertTriangle className="w-3 h-3" /> },
  suspended: { label: 'ระงับ',     cls: 'bg-slate-100 text-slate-500',    icon: null },
  paid:      { label: 'ชำระแล้ว',  cls: 'bg-blue-100 text-blue-700',      icon: <CheckCircle className="w-3 h-3" /> },
};

export default function CustomersPage() {
  const [search, setSearch] = useState('');
  const [selectedCustomer, setSelectedCustomer] = useState<Customer | null>(null);
  const [showForm, setShowForm] = useState(false);
  const [editCustomer, setEditCustomer] = useState<Customer | null>(null);

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

  const openAdd = () => { setEditCustomer(null); setShowForm(true); };
  const openEdit = (c: Customer) => { setEditCustomer(c); setShowForm(true); };

  return (
    <div className="p-6 min-h-full bg-slate-50">
      <div className="flex gap-6">
        {/* List */}
        <div className="flex-1 min-w-0">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h1 className="text-2xl font-bold text-slate-800">ลูกค้า / เครดิต</h1>
              <p className="text-sm text-slate-500 mt-0.5">จัดการข้อมูลลูกค้าและวงเงินเครดิต</p>
            </div>
            <button onClick={openAdd}
              className="flex items-center gap-2 px-4 py-2.5 text-white text-sm font-semibold rounded-xl transition-all active:scale-95 shadow-lg shadow-violet-500/25"
              style={{ background: 'linear-gradient(135deg, #6366f1, #8b5cf6)' }}>
              <UserPlus className="w-4 h-4" />เพิ่มลูกค้า
            </button>
          </div>

          <div className="relative mb-4">
            <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400 w-4 h-4" />
            <input type="text" value={search} onChange={(e) => setSearch(e.target.value)}
              placeholder="ค้นหาชื่อ / เบอร์โทร / รหัสลูกค้า..."
              className="pl-10 pr-4 py-2.5 border border-slate-200 rounded-xl w-full text-sm bg-white focus:ring-2 focus:ring-violet-500 focus:border-violet-500 focus:outline-none" />
          </div>

          <div className="bg-white rounded-2xl shadow-sm border border-slate-100 overflow-hidden">
            <table className="w-full text-sm">
              <thead>
                <tr className="bg-slate-50 border-b border-slate-100">
                  <th className="px-4 py-3.5 text-left text-xs font-bold text-slate-500 uppercase tracking-wider">ลูกค้า</th>
                  <th className="px-4 py-3.5 text-right text-xs font-bold text-slate-500 uppercase tracking-wider">วงเงินเครดิต</th>
                  <th className="px-4 py-3.5 text-right text-xs font-bold text-slate-500 uppercase tracking-wider">ยอดค้าง</th>
                  <th className="px-4 py-3.5 text-center text-xs font-bold text-slate-500 uppercase tracking-wider">สถานะ</th>
                  <th className="px-4 py-3.5"></th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {isLoading ? (
                  <tr><td colSpan={5} className="text-center py-12 text-slate-400">
                    <Loader2 className="w-6 h-6 animate-spin mx-auto mb-2" />กำลังโหลด...
                  </td></tr>
                ) : customers?.length === 0 ? (
                  <tr><td colSpan={5} className="text-center py-16 text-slate-400">
                    <UserPlus className="w-12 h-12 mx-auto mb-3 opacity-30" />
                    <p>ยังไม่มีลูกค้า</p>
                    <button onClick={openAdd} className="mt-3 text-violet-600 text-sm font-medium hover:underline">+ เพิ่มลูกค้าแรก</button>
                  </td></tr>
                ) : (
                  customers?.map((c: Customer) => {
                    const badge = creditBadge[c.credit_status] || creditBadge.active;
                    const isSelected = selectedCustomer?.id === c.id;
                    return (
                      <tr key={c.id}
                        onClick={() => setSelectedCustomer(isSelected ? null : c)}
                        className={`cursor-pointer transition-colors group ${isSelected ? 'bg-violet-50 border-l-2 border-violet-500' : 'hover:bg-slate-50/60'}`}>
                        <td className="px-4 py-3.5">
                          <div className="flex items-center gap-3">
                            <div className="w-9 h-9 rounded-full flex items-center justify-center text-sm font-bold text-white flex-shrink-0"
                              style={{ background: `hsl(${(c.name.charCodeAt(0) * 7) % 360}, 60%, 55%)` }}>
                              {c.name[0]}
                            </div>
                            <div>
                              <p className="font-semibold text-slate-800">{c.name}</p>
                              <p className="text-xs text-slate-400 mt-0.5 flex items-center gap-1.5">
                                <span>{c.code}</span>
                                {c.phone && <><span>·</span><Phone className="w-3 h-3" />{c.phone}</>}
                              </p>
                            </div>
                          </div>
                        </td>
                        <td className="px-4 py-3.5 text-right">
                          {c.credit_limit > 0 ? <span className="font-medium text-slate-700">{formatCurrency(c.credit_limit)}</span> : <span className="text-slate-300">-</span>}
                        </td>
                        <td className="px-4 py-3.5 text-right">
                          {c.credit_balance > 0 ? (
                            <span className={`font-bold ${c.credit_status === 'overdue' ? 'text-rose-600' : 'text-amber-600'}`}>
                              {formatCurrency(c.credit_balance)}
                            </span>
                          ) : <span className="text-slate-300">-</span>}
                        </td>
                        <td className="px-4 py-3.5 text-center">
                          <span className={`inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-semibold ${badge.cls}`}>
                            {badge.icon}{badge.label}
                          </span>
                        </td>
                        <td className="px-4 py-3.5 text-center w-10">
                          <button onClick={(e) => { e.stopPropagation(); openEdit(c); }}
                            className="opacity-0 group-hover:opacity-100 p-1.5 text-slate-400 hover:text-indigo-600 hover:bg-indigo-50 rounded-lg transition-all">
                            <Edit2 className="w-3.5 h-3.5" />
                          </button>
                        </td>
                      </tr>
                    );
                  })
                )}
              </tbody>
            </table>
          </div>
        </div>

        {/* Detail Panel */}
        {selectedCustomer && (
          <div className="w-72 shrink-0">
            <div className="bg-white rounded-2xl shadow-sm border border-slate-100 p-5 sticky top-6">
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center gap-3">
                  <div className="w-11 h-11 rounded-full flex items-center justify-center text-base font-bold text-white shadow-md"
                    style={{ background: `hsl(${(selectedCustomer.name.charCodeAt(0) * 7) % 360}, 60%, 55%)` }}>
                    {selectedCustomer.name[0]}
                  </div>
                  <div>
                    <p className="font-bold text-slate-800 leading-tight">{selectedCustomer.name}</p>
                    <p className="text-xs text-slate-400">{selectedCustomer.code}</p>
                  </div>
                </div>
                <button onClick={() => openEdit(selectedCustomer)}
                  className="p-1.5 text-slate-400 hover:text-indigo-600 hover:bg-indigo-50 rounded-lg transition-all">
                  <ChevronRight className="w-4 h-4" />
                </button>
              </div>

              <div className="space-y-2 text-sm mb-4">
                {selectedCustomer.phone && (
                  <div className="flex items-center gap-2 text-slate-600">
                    <Phone className="w-3.5 h-3.5 text-slate-400 flex-shrink-0" />{selectedCustomer.phone}
                  </div>
                )}
                {selectedCustomer.address && (
                  <div className="flex items-start gap-2 text-slate-600">
                    <MapPin className="w-3.5 h-3.5 text-slate-400 mt-0.5 flex-shrink-0" />
                    <span className="text-xs leading-relaxed">{selectedCustomer.address}</span>
                  </div>
                )}
              </div>

              {creditSummary && (
                <div className="pt-4 border-t border-slate-100 space-y-2.5">
                  <InfoRow label="วงเงินเครดิต" value={formatCurrency(creditSummary.credit_limit)} />
                  <InfoRow label="ยอดค้าง" value={formatCurrency(creditSummary.credit_balance)} />
                  <InfoRow label="วงเงินคงเหลือ" value={formatCurrency(creditSummary.available_credit)} highlight />
                  {creditSummary.overdue_amount > 0 && (
                    <InfoRow label="เกินกำหนด" value={formatCurrency(creditSummary.overdue_amount)} danger />
                  )}
                  <InfoRow label="ออเดอร์ค้าง" value={`${creditSummary.outstanding_orders} รายการ`} />
                </div>
              )}

              {selectedCustomer.credit_balance > 0 && (
                <button className="w-full mt-4 py-2.5 text-white rounded-xl text-sm font-semibold transition-all active:scale-95"
                  style={{ background: 'linear-gradient(135deg, #3b82f6, #6366f1)' }}>
                  <CreditCard className="w-4 h-4 inline mr-2" />บันทึกรับชำระ
                </button>
              )}
            </div>
          </div>
        )}
      </div>

      {showForm && (
        <CustomerFormModal customer={editCustomer} onClose={() => { setShowForm(false); setEditCustomer(null); }} />
      )}
    </div>
  );
}

function InfoRow({ label, value, highlight, danger }: { label: string; value: string; highlight?: boolean; danger?: boolean }) {
  return (
    <div className="flex justify-between items-center">
      <span className="text-xs text-slate-400">{label}</span>
      <span className={`text-sm font-semibold ${danger ? 'text-rose-600' : highlight ? 'text-emerald-600' : 'text-slate-700'}`}>{value}</span>
    </div>
  );
}
