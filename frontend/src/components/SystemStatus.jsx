import React from 'react'

function SystemStatus({ data }) {
  const status = data?.status || {}
  const collisionCount = data?.collisions?.length || 0

  return (
    <div className="flex gap-6 items-center">
      <div className="text-right">
        <div className="text-xs text-gray-400">SATELLITES</div>
        <div className="text-xl font-bold text-green-400">
          {status.total_satellites || 0}
        </div>
      </div>
      
      <div className="text-right">
        <div className="text-xs text-gray-400">DEBRIS</div>
        <div className="text-xl font-bold text-orange-400">
          {status.total_debris || 0}
        </div>
      </div>
      
      <div className="text-right">
        <div className="text-xs text-gray-400">THREATS</div>
        <div className={`text-xl font-bold ${
          collisionCount > 0 ? 'text-red-400 animate-pulse' : 'text-green-400'
        }`}>
          {collisionCount}
        </div>
      </div>

      <div className="flex items-center gap-2">
        <div className={`w-3 h-3 rounded-full ${
          status.operational_satellites > 0 ? 'bg-green-500 animate-pulse' : 'bg-gray-500'
        }`} />
        <span className="text-xs text-gray-400">SYSTEM ONLINE</span>
      </div>
    </div>
  )
}

export default SystemStatus
