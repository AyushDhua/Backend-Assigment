import React, { useState } from 'react';
import api from '../utils/api';

const TradeForm = () => {
  const [symbol, setSymbol] = useState('BTCUSDT');
  const [side, setSide] = useState('BUY');
  const [type, setType] = useState('MARKET');
  const [quantity, setQuantity] = useState('');
  const [price, setPrice] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const payload = { symbol, side, type, quantity: parseFloat(quantity) };
      if (type === 'LIMIT') payload.price = parseFloat(price);

      const response = await api.post('/trades/order', payload);
      setResult(response.data.data);
    } catch (err) {
      setError(err.response?.data?.message || 'Failed to execute trade');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="card">
      <h3 className="section-title">Execute Trade</h3>
      
      {error && <div className="alert-error">{error}</div>}
      
      {result && (
        <div className="alert-success">
          <strong>Trade Executed:</strong> Order ID: {result.order_id} ({result.status})
        </div>
      )}

      <form onSubmit={handleSubmit} className="form">
        <div className="grid-2">
          <div className="input-group">
            <label>Symbol</label>
            <input
              type="text"
              required
              value={symbol}
              onChange={(e) => setSymbol(e.target.value.toUpperCase())}
              className="input-field"
              placeholder="BTCUSDT"
            />
          </div>
          <div className="input-group">
            <label>Quantity</label>
            <input
              type="number"
              step="0.00001"
              required
              value={quantity}
              onChange={(e) => setQuantity(e.target.value)}
              className="input-field"
              placeholder="0.01"
            />
          </div>
          <div className="input-group">
            <label>Side</label>
            <select value={side} onChange={(e) => setSide(e.target.value)} className="input-field">
              <option value="BUY">BUY</option>
              <option value="SELL">SELL</option>
            </select>
          </div>
          <div className="input-group">
            <label>Type</label>
            <select value={type} onChange={(e) => setType(e.target.value)} className="input-field">
              <option value="MARKET">MARKET</option>
              <option value="LIMIT">LIMIT</option>
            </select>
          </div>
        </div>
        
        {type === 'LIMIT' && (
          <div className="input-group">
            <label>Price</label>
            <input
              type="number"
              step="0.01"
              required
              value={price}
              onChange={(e) => setPrice(e.target.value)}
              className="input-field"
              placeholder="65000"
            />
          </div>
        )}
        
        <button type="submit" disabled={loading} className="btn-primary w-full">
          {loading ? 'Executing...' : 'Execute Trade'}
        </button>
      </form>
    </div>
  );
};

export default TradeForm;
