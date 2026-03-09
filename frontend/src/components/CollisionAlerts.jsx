import React from 'react'

function CollisionAlerts({ collisions }) {
  const criticalCollisions = collisions.filter(c => c.severity === 'critical')
  const warningCollisions = collisions.filter(c => c.severity === 'warning')

  return (
    <div className="panel">
      <h2 className="panel-title">⚠️ Collision Alerts</h2>
      
      <div className="mb-4">
        <div className="flex justify-between text-sm mb-2">
          <span>Total Threats:</span>
          <span className="font-bold text-red-400">{collisions.length}</span>
        </div>
        <div className="flex justify-between text-sm mb-2">
          <span>Critical:</span>
          <span className="font-bold text-red-500">{criticalCollisions.length}</span>
        </div>
        <div className="flex justify-between text-sm">
          <span>Warnings:</span>
          <span className="font-bold text-yellow-500">{warningCollisions.length}</span>
        </div>
      </div>

      <div className="space-y-2 max-h-96 overflow-y-auto">
        {criticalCollisions.map((collision, idx) => (
          <div key={idx} className="alert-critical">
            <div className="flex justify-between items-start mb-1">
              <span className="font-bold text-red-400">CRITICAL</span>
              <span className="text-xs text-gray-400">
                TCA: {collision.tca_hours?.toFixed(2)}h
              </span>
            </div>
            <div className="text-sm">
              <div>{collision.satellite_id}</div>
              <div className="text-gray-400">vs {collision.debris_id}</div>
              <div className="text-red-300 mt-1">
                {collision.min_distance_meters?.toFixed(0)}m separation
              </div>
            </div>
          </div>
        ))}

        {warningCollisions.slice(0, 5).map((collision, idx) => (
          <div key={idx} className="alert-warning">
            <div className="flex justify-between items-start mb-1">
              <span className="font-bold text-yellow-400">WARNING</span>
              <span className="text-xs text-gray-400">
                TCA: {collision.tca_hours?.toFixed(2)}h
              </span>
            </div>
            <div className="text-sm">
              <div>{collision.satellite_id}</div>
              <div className="text-gray-400">vs {collision.debris_id}</div>
              <div className="text-yellow-300 mt-1">
                {collision.min_distance_meters?.toFixed(0)}m separation
              </div>
            </div>
          </div>
        ))}
      </div>

      {collisions.length === 0 && (
        <div className="text-center text-green-400 py-4">
          ✓ No collision threats detected
        </div>
      )}
    </div>
  )
}

export default CollisionAlerts
