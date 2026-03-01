import React from 'react';
import { Product } from '../../types';
import { formatCurrency } from '../../utils/format';
import { Package, ShoppingCart } from 'lucide-react';

interface Props {
  products: Product[];
  onSelect: (product: Product) => void;
}

export default function ProductGrid({ products, onSelect }: Props) {
  if (products.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center h-48 text-slate-400">
        <Package className="w-12 h-12 mb-2 opacity-40" />
        <p className="text-sm">ไม่พบสินค้า</p>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-3">
      {products.map((product) => (
        <button
          key={product.id}
          onClick={() => onSelect(product)}
          className="bg-white rounded-2xl border border-slate-100 p-3 text-left hover:shadow-lg hover:border-emerald-300 hover:-translate-y-0.5 transition-all duration-150 active:scale-95 group relative overflow-hidden"
        >
          {/* Image */}
          {product.main_image_url ? (
            <img
              src={product.main_image_url}
              alt={product.name}
              className="w-full h-24 object-cover rounded-xl mb-2 bg-slate-100"
            />
          ) : (
            <div className="w-full h-24 bg-gradient-to-br from-slate-100 to-slate-200 rounded-xl mb-2 flex items-center justify-center">
              <Package className="w-8 h-8 text-slate-300" />
            </div>
          )}

          {/* Add to cart overlay */}
          <div className="absolute inset-0 bg-emerald-500/0 group-hover:bg-emerald-500/5 rounded-2xl transition-all duration-150 flex items-center justify-center opacity-0 group-hover:opacity-100">
            <div className="absolute top-2 right-2 w-7 h-7 bg-emerald-500 rounded-full flex items-center justify-center shadow-lg scale-0 group-hover:scale-100 transition-transform">
              <ShoppingCart className="w-3.5 h-3.5 text-white" />
            </div>
          </div>

          <p className="text-xs text-slate-400 font-mono truncate">{product.code}</p>
          <p className="text-sm font-semibold text-slate-800 line-clamp-2 leading-tight mt-0.5">{product.name}</p>
          <div className="flex items-baseline gap-1 mt-1.5">
            <span className="text-base font-bold text-emerald-600">{formatCurrency(product.selling_price)}</span>
            <span className="text-xs text-slate-400">/{product.unit}</span>
          </div>
        </button>
      ))}
    </div>
  );
}
