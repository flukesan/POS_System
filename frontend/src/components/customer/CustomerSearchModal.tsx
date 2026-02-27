import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { customerApi } from '../../services/api';
import { Customer } from '../../types';
import { X, Search, UserPlus, CreditCard } from 'lucide-react';
import { formatCurrency } from '../../utils/format';

interface Props {
  onSelect: (customer: Customer) => void;
  onClose: () => void;
}

export default function CustomerSearchModal({ onSelect, onClose }: Props) {
  const [search, setSearch] = useState('');

  const { data: customers, isLoading } = useQuery({
    queryKey: ['customers-search', search],
    queryFn: () => customerApi.list({ search, limit: 20 }),
    select: (r) => r.data,
    enabled: search.length > 0 || true,
  });

  const creditStatusColor: Record<string, string> = {
    active: 'bg-green-100 text-green-700',
    overdue: 'bg-red-100 text-red-700',
    suspended: 'bg-gray-100 text-gray-600',
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-md mx-4 max-h-[80vh] flex flex-col">
        <div className="flex items-center justify-between p-4 border-b">
          <h2 className="text-lg font-bold text-gray-800">เลือกลูกค้า</h2>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-600">
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="p-4 border-b">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 w-4 h-4" />
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="ค้นหาชื่อ / เบอร์โทร / รหัสลูกค้า..."
              className="w-full pl-10 pr-4 py-2 border rounded-lg text-sm focus:ring-2 focus:ring-green-500 focus:outline-none"
              autoFocus
            />
          </div>
        </div>

        <div className="flex-1 overflow-y-auto p-2">
          {isLoading ? (
            <div className="text-center py-8 text-gray-400 text-sm">กำลังโหลด...</div>
          ) : customers?.length === 0 ? (
            <div className="text-center py-8 text-gray-400 text-sm">ไม่พบลูกค้า</div>
          ) : (
            customers?.map((customer: Customer) => (
              <button
                key={customer.id}
                onClick={() => onSelect(customer)}
                className="w-full text-left px-4 py-3 hover:bg-gray-50 rounded-xl transition-colors"
              >
                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-medium text-gray-800">{customer.name}</p>
                    <p className="text-xs text-gray-400">{customer.code} · {customer.phone}</p>
                  </div>
                  {customer.credit_limit > 0 && (
                    <div className="text-right">
                      <p className={`text-xs px-2 py-0.5 rounded-full ${creditStatusColor[customer.credit_status] || 'bg-gray-100'}`}>
                        {customer.credit_status === 'overdue' ? 'เกินกำหนด' : 'เครดิต'}
                      </p>
                      <div className="flex items-center gap-1 mt-0.5">
                        <CreditCard className="w-3 h-3 text-gray-400" />
                        <p className="text-xs text-gray-500">
                          {formatCurrency(customer.credit_limit - customer.credit_balance)} คงเหลือ
                        </p>
                      </div>
                    </div>
                  )}
                </div>
              </button>
            ))
          )}
        </div>
      </div>
    </div>
  );
}
