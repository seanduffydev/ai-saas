/**
 * @fileoverview Dropdown selector for choosing a commodity.
 */

import React from 'react';

/**
 * Renders a select dropdown of commodities with optional disabled state.
 * @param {Object} props - Component props.
 * @param {Array<{id: string, name: string, category: string, icon: string}>} props.commodities - List of commodities.
 * @param {string} props.selectedCommodity - Currently selected commodity id.
 * @param {function(string): void} props.onSelect - Called with commodity id when selection changes.
 * @param {boolean} [props.disabled] - Whether the select is disabled.
 * @return {JSX.Element} Commodity select element with label.
 */
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