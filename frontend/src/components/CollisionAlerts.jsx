import React, { useState } from 'react'

function CollisionAlerts({ collisions = [] }) {
  const [resolving, setResolving] = useState(false)
  const [resolveMessage, setResolveMessage] = useState('')
  
  const threatCount = collisions.length

  const handleAutoResolve = async () => {
    setResolving(true)
    setResolveMessage('')
    
    try {
      // This will be handled by the ManeuverTimeline component
      // Just show a message here
      setResolveMessage('✅ Maneuvers executing...')
      setTimeout(() => setResolveMessage(''), 3000)
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
          <span>Active Threats:</span>
          <span className={`font-bold ${threatCount > 0 ? 'text-red-400 animate-pulse' : 'text-green-400'}`}>
            {threatCount}
          </span>
        </div>
        {threatCount > 0 && (
          <div className="text-xs text-red-300 bg-red-900 bg-opacity-30 p-2 rounded">
            ⚠️ {threatCount} satellite{threatCount !== 1 ? 's' : ''} at collision risk
          </div>
        )}
      </div>

      {threatCount > 0 && (
        <div className="space-y-2 max-h-96 overflow-y-auto mb-4">
          {collisions.map((collision, idx) => (
            <div key={idx} className="alert-critical">
              <div className="flex justify-between items-start mb-1">
                <span className="font-bold text-red-400">🚨 THREAT</span>
                <span className="text-xs text-gray-400">#{idx + 1}</span>
              </div>
              <div className="text-sm">
                <div className="text-red-300 font-mono">{collision.satellite_id}</div>
                <div className="text-gray-400 text-xs mt-1">
                  Collision risk detected
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {threatCount === 0 && (
        <div className="text-center text-green-400 py-4">
          ✓ No collision threats detected
        </div>
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
    </div>
  )
}

export default CollisionAlerts
