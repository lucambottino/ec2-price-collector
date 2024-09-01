"use client";

import { useEffect, useState } from "react";

export default function LatestCoinData() {
  const [binanceData, setBinanceData] = useState([]);
  const [coinexData, setCoinexData] = useState([]);

  // Function to fetch data for a specific exchange
  const fetchData = async (exchange, setData) => {
    try {
      const response = await fetch(`/api/coin-data?exchange=${exchange}`);
      if (!response.ok) {
        throw new Error(`Failed to fetch data from ${exchange}`);
      }
      const data = await response.json();
      setData(
        data.sort((a, b) => a.coin.coin_name.localeCompare(b.coin.coin_name))
      );
    } catch (error) {
      console.error(`Error fetching data for ${exchange}:`, error);
    }
  };

  // Fetch data every second for both exchanges
  useEffect(() => {
    const intervalId = setInterval(() => {
      fetchData("BINANCE", setBinanceData);
      fetchData("COINEX", setCoinexData);
    }, 1000);

    // Clear interval on component unmount
    return () => clearInterval(intervalId);
  }, []);

  // Function to calculate bid-ask spread
  const calculateSpread = (bid, ask) => {
    if (bid !== null && ask !== null) {
      return (ask - bid).toFixed(4);
    }
    return "N/A";
  };

  // Function to render data in a grid-like layout
  const renderGrid = (data, exchangeName) => (
    <div className="exchange-container w-full mb-6">
      <h2 className="text-lg font-semibold text-gray-300 mb-2">
        {exchangeName}
      </h2>
      <div className="grid grid-cols-1 gap-4">
        {data.length > 0 ? (
          data.map((coin) => (
            <div
              key={coin.data_id}
              className="grid grid-cols-4 p-3 bg-gray-800 rounded-md shadow"
            >
              <div className="coin-name col-span-1 text-white font-bold">
                {coin.coin.coin_name}
              </div>
              <div className="value col-span-1 text-green-400 font-medium">
                <span>Bid:</span>{" "}
                {coin.best_bid !== null ? coin.best_bid.toFixed(4) : "N/A"}
              </div>
              <div className="value col-span-1 text-red-400 font-medium">
                <span>Ask:</span>{" "}
                {coin.best_ask !== null ? coin.best_ask.toFixed(4) : "N/A"}
              </div>
              <div className="value col-span-1 text-blue-400 font-medium">
                <span>Spread:</span>{" "}
                {calculateSpread(coin.best_bid, coin.best_ask)}
              </div>
              <div className="value col-span-1 text-yellow-400 font-medium">
                <span>Mark:</span>{" "}
                {coin.mark_price !== null ? coin.mark_price.toFixed(4) : "N/A"}
              </div>
            </div>
          ))
        ) : (
          <div className="grid-item text-gray-400">Loading...</div>
        )}
      </div>
    </div>
  );

  return (
    <div className="trading-dashboard min-h-screen bg-gray-900 p-10">
      <h1 className="text-2xl font-bold text-center text-gray-100 mb-8">
        Live Coin Data
      </h1>
      <div className="data-container flex justify-center gap-10">
        {renderGrid(binanceData, "BINANCE")}
        {renderGrid(coinexData, "COINEX")}
      </div>
    </div>
  );
}
