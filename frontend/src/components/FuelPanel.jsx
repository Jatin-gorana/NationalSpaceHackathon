import React from 'react'

function FuelPanel({ satellites }) {
  const avgFuel = satellites.length > 0
    ? satellites.reduce((sum, sat) => sum + (sat.fuel_remaining || 0), 0) / satellites.length
    : 0

  const lowFuelSats = satellites.filter(sat => (sat.fuel_remaining || 0) < 20)

  return (
    <div className="panel">
      <h2 className="panel-title">⛽ Fuel Status</h2>
      
      <div className="mb-4">
        <div className="text-sm text-gray-400 mb-1">Fleet Average</div>
        <div className="stat-value">{avgFuel.toFixed(1)}%</div>
        <div className="w-full bg-gray-700 rounded-full h-2 mt-2">
          <div 
            className={`h-2 rounded-full transition-all ${
              avgFuel > 50 ? 'bg-green-500' : 
              avgFuel > 20 ? 'bg-yellow-500' : 'bg-red-500'
            }`}
            style={{ width: `${avgFuel}%` }}
          />
        </div>
      </div>

      <div className="space-y-2">
        {satellites.map((sat) => {
          const fuel = sat.fuel_remaining || 0
          return (
            <div key={sat.object_id} className="border-l-2 border-cyan-500 pl-3 py-2">
              <div className="flex justify-between items-center mb-1">
                <span className="text-sm font-bold">{sat.object_id}</span>
                <span className={`text-sm font-bold ${
                  fuel > 50 ? 'text-green-400' :
                  fuel > 20 ? 'text-yellow-400' : 'text-red-400'
                }`}>
                  {fuel.toFixed(1)}%
                </span>
              </div>
              <div className="w-full bg-gray-700 rounded-full h-1.5">
                <div 
                  className={`h-1.5 rounded-full transition-all ${
                    fuel > 50 ? 'bg-green-500' :
                    fuel > 20 ? 'bg-yellow-500' : 'bg-red-500'
                  }`}
                  style={{ width: `${fuel}%` }}
                />
              </div>
            </div>
          )
        })}
      </div>

      {lowFuelSats.length > 0 && (
        <div className="mt-4 p-3 bg-red-900 bg-opacity-30 border border-red-500 rounded">
          <div className="text-red-400 font-bold text-sm mb-1">
            ⚠️ LOW FUEL WARNING
          </div>
          <div className="text-xs text-gray-300">
            {lowFuelSats.length} satellite(s) below 20% fuel
          </div>
        </div>
      )}
    </div>
  )
}

export default FuelPanel
