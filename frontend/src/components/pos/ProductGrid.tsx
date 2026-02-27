import React from 'react';
import { Product } from '../../types';
import { formatCurrency } from '../../utils/format';
import { Package } from 'lucide-react';

interface Props {
  products: Product[];
  onSelect: (product: Product) => void;
}

export default function ProductGrid({ products, onSelect }: Props) {
  if (products.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center h-48 text-gray-400">
        <Package className="w-12 h-12 mb-2" />
        <p>ไม่พบสินค้า</p>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-3">
      {products.map((product) => (
        <button
          key={product.id}
          onClick={() => onSelect(product)}
          className="bg-white rounded-xl shadow-sm border border-gray-100 p-3 text-left hover:shadow-md hover:border-green-400 transition-all active:scale-95 group"
        >
          {product.main_image_url ? (
            <img
              src={product.main_image_url}
              alt={product.name}
              className="w-full h-24 object-cover rounded-lg mb-2 bg-gray-100"
            />
          ) : (
            <div className="w-full h-24 bg-gray-100 rounded-lg mb-2 flex items-center justify-center">
              <Package className="w-8 h-8 text-gray-300" />
            </div>
          )}
          <p className="text-xs text-gray-400 font-mono">{product.code}</p>
          <p className="text-sm font-medium text-gray-800 line-clamp-2 leading-tight">{product.name}</p>
          <p className="text-base font-bold text-green-600 mt-1">
            {formatCurrency(product.selling_price)}
            <span className="text-xs text-gray-400 font-normal ml-1">/{product.unit}</span>
          </p>
        </button>
      ))}
    </div>
  );
}
