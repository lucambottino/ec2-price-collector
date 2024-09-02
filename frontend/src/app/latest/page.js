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

  // Function to calculate bid and ask spreads
  const calculateSpreads = (coinex, binance) => {
    if (
      coinex.best_bid !== null &&
      coinex.best_ask !== null &&
      binance.best_bid !== null &&
      binance.best_ask !== null
    ) {
      const bidSpread = (
        (coinex.best_bid / binance.best_ask - 1) *
        100
      ).toFixed(2);
      const askSpread = (
        (coinex.best_ask / binance.best_bid - 1) *
        100
      ).toFixed(2);
      return { bidSpread, askSpread };
    }
    return { bidSpread: "N/A", askSpread: "N/A" };
  };

  // Function to render data in a compact table with alternating row colors
  const renderTable = () => {
    return binanceData.map((binanceCoin) => {
      const coinexCoin = coinexData.find(
        (coin) => coin.coin.coin_name === binanceCoin.coin.coin_name
      );

      if (coinexCoin) {
        const { bidSpread, askSpread } = calculateSpreads(
          coinexCoin,
          binanceCoin
        );

        return (
          <tr
            key={binanceCoin.data_id}
            className="hover:bg-gray-700 text-xs sm:text-sm even:bg-gray-800 odd:bg-gray-700"
          >
            <td className="p-1 sm:p-2 text-center text-white font-semibold">
              {binanceCoin.coin.coin_name}
            </td>
            <td
              className={`p-1 sm:p-2 text-center ${
                bidSpread >= 0 ? "text-green-500" : "text-red-500"
              }`}
            >
              {bidSpread}%
            </td>
            <td
              className={`p-1 sm:p-2 text-center ${
                askSpread >= 0 ? "text-green-500" : "text-red-500"
              }`}
            >
              {askSpread}%
            </td>
          </tr>
        );
      }

      return null;
    });
  };

  return (
    <div className="trading-dashboard min-h-screen bg-gray-900 flex justify-center items-center p-4 sm:p-6">
      <div className="w-full max-w-5xl mx-4 sm:mx-8 lg:mx-12">
        <h1 className="text-lg sm:text-xl font-bold text-center text-gray-100 mb-4 sm:mb-6">
          COINEX/BINANCE
        </h1>
        <div className="overflow-x-auto">
          <table className="min-w-full bg-gray-900 text-gray-100 border border-gray-700 rounded-lg">
            <thead>
              <tr className="bg-gray-800 text-xs sm:text-sm">
                <th className="p-2 text-center">Coin</th>
                <th className="p-2 text-center">Bid Spread (%)</th>
                <th className="p-2 text-center">Ask Spread (%)</th>
              </tr>
            </thead>
            <tbody>{renderTable()}</tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
