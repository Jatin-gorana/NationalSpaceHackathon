import React, { useState } from 'react'

function CollisionAlerts({ collisions }) {
  const [resolving, setResolving] = useState(false)
  const [resolveMessage, setResolveMessage] = useState('')
  
  const criticalCollisions = collisions.filter(c => c.severity === 'critical')
  const warningCollisions = collisions.filter(c => c.severity === 'warning')

  const handleAutoResolve = async () => {
    setResolving(true)
    setResolveMessage('')
    
    try {
      const response = await fetch('http://localhost:8000/api/ai/auto-resolve', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        }
      })
      
      const data = await response.json()
      
      if (data.status === 'resolved') {
        setResolveMessage(`✅ Resolved ${data.satellites_resolved} collision risks`)
      } else if (data.status === 'no_risks') {
        setResolveMessage('✓ No collision risks to resolve')
      }
      
      setTimeout(() => setResolveMessage(''), 5000)
    } catch (error) {
      console.error('Auto-resolve error:', error)
      setResolveMessage('❌ Failed to resolve collisions')
      setTimeout(() => setResolveMessage(''), 5000)
    } finally {
      setResolving(false)
    }
  }

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

      {collisions.length > 0 && (
        <button
          onClick={handleAutoResolve}
          disabled={resolving}
          className="w-full mb-4 px-4 py-2 bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 disabled:from-gray-600 disabled:to-gray-700 text-white font-bold rounded transition-all duration-200 flex items-center justify-center gap-2"
        >
          {resolving ? (
            <>
              <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
              <span>Optimizing...</span>
            </>
          ) : (
            <>
              <span>🤖</span>
              <span>AI Auto-Resolve</span>
            </>
          )}
        </button>
      )}

      {resolveMessage && (
        <div className={`mb-4 p-2 rounded text-sm text-center ${
          resolveMessage.includes('✅') ? 'bg-green-900 bg-opacity-30 text-green-400' :
          resolveMessage.includes('❌') ? 'bg-red-900 bg-opacity-30 text-red-400' :
          'bg-cyan-900 bg-opacity-30 text-cyan-400'
        }`}>
          {resolveMessage}
        </div>
      )}

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
