import React from 'react';
import { useCartStore } from '../../store/cartStore';
import { formatCurrency } from '../../utils/format';
import { Minus, Plus, Trash2 } from 'lucide-react';

export default function CartPanel() {
  const { items, updateQty, removeItem, updateDiscount } = useCartStore();

  if (items.length === 0) {
    return (
      <div className="flex-1 flex items-center justify-center text-gray-400 text-sm">
        ยังไม่มีสินค้าในรายการ
      </div>
    );
  }

  return (
    <div className="flex-1 overflow-y-auto">
      {items.map((item) => (
        <div key={item.product.id} className="px-4 py-3 border-b hover:bg-gray-50 group">
          <div className="flex items-start gap-2">
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-gray-800 truncate">{item.product.name}</p>
              <p className="text-xs text-gray-400">{item.product.code}</p>
              <div className="flex items-center gap-2 mt-1">
                <span className="text-sm text-gray-600">
                  {formatCurrency(item.unit_price)} × {item.quantity}
                </span>
                {item.discount_percent > 0 && (
                  <span className="text-xs bg-red-100 text-red-600 px-1.5 py-0.5 rounded">
                    -{item.discount_percent}%
                  </span>
                )}
              </div>
            </div>
            <div className="text-right">
              <p className="text-sm font-bold text-green-600">{formatCurrency(item.total_amount)}</p>
            </div>
          </div>

          <div className="flex items-center justify-between mt-2">
            {/* Quantity Controls */}
            <div className="flex items-center gap-1">
              <button
                onClick={() => {
                  if (item.quantity > 1) updateQty(item.product.id, item.quantity - 1);
                  else removeItem(item.product.id);
                }}
                className="w-7 h-7 flex items-center justify-center rounded-full bg-gray-100 hover:bg-gray-200 text-gray-600"
              >
                <Minus className="w-3.5 h-3.5" />
              </button>
              <input
                type="number"
                value={item.quantity}
                min={1}
                onChange={(e) => {
                  const v = parseFloat(e.target.value);
                  if (v > 0) updateQty(item.product.id, v);
                }}
                className="w-12 text-center text-sm border rounded-md py-0.5 focus:ring-1 focus:ring-green-500 focus:outline-none"
              />
              <button
                onClick={() => updateQty(item.product.id, item.quantity + 1)}
                className="w-7 h-7 flex items-center justify-center rounded-full bg-gray-100 hover:bg-gray-200 text-gray-600"
              >
                <Plus className="w-3.5 h-3.5" />
              </button>
            </div>

            {/* Discount */}
            <div className="flex items-center gap-1">
              <label className="text-xs text-gray-400">ส่วนลด%</label>
              <input
                type="number"
                value={item.discount_percent}
                min={0}
                max={100}
                onChange={(e) => updateDiscount(item.product.id, parseFloat(e.target.value) || 0)}
                className="w-14 text-center text-xs border rounded-md py-0.5 focus:ring-1 focus:ring-green-500 focus:outline-none"
              />
            </div>

            <button
              onClick={() => removeItem(item.product.id)}
              className="text-gray-300 hover:text-red-500 transition-colors"
            >
              <Trash2 className="w-4 h-4" />
            </button>
          </div>
        </div>
      ))}
    </div>
  );
}
