import React from 'react';

function CommoditySelector({ commodities, selectedCommodity, onSelect, disabled }) {
  return (
    <div className="commodity-selector">
      <label htmlFor="commodity-select">Select Commodity:</label>
      <select
        id="commodity-select"
        value={selectedCommodity}
        onChange={(e) => onSelect(e.target.value)}
        disabled={disabled}
      >
        <option value="">-- Choose a commodity --</option>
        {commodities.map((commodity) => (
          <option key={commodity.id} value={commodity.id}>
            {commodity.icon} {commodity.name} ({commodity.category})
          </option>
        ))}
      </select>
    </div>
  );
}

export default CommoditySelector;