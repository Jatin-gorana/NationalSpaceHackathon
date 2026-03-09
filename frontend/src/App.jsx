import React, { useState, useEffect } from 'react'
import SatelliteViewer from './components/SatelliteViewer'
import CollisionAlerts from './components/CollisionAlerts'
import FuelPanel from './components/FuelPanel'
import ManeuverTimeline from './components/ManeuverTimeline'
import SystemStatus from './components/SystemStatus'
import { fetchSystemData } from './api/acmApi'

function App() {
  const [systemData, setSystemData] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const loadData = async () => {
      try {
        const data = await fetchSystemData()
        setSystemData(data)
        setLoading(false)
      } catch (error) {
        console.error('Failed to load system data:', error)
        setLoading(false)
      }
    }

    loadData()
    const interval = setInterval(loadData, 5000) // Refresh every 5 seconds

    return () => clearInterval(interval)
  }, [])

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-cyan-400 text-2xl animate-pulse">
          INITIALIZING ACM SYSTEM...
        </div>
      </div>
    )
  }

  return (
    <div className="h-screen w-screen overflow-hidden bg-space-dark">
      {/* Header */}
      <header className="absolute top-0 left-0 right-0 z-10 bg-gray-900 bg-opacity-90 border-b border-cyan-500 p-4">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-cyan-400 tracking-wider">
              ACM MISSION CONTROL
            </h1>
            <p className="text-sm text-gray-400">Autonomous Constellation Manager v2.0</p>
          </div>
          <SystemStatus data={systemData} />
        </div>
      </header>

      {/* Main Content */}
      <div className="flex h-full pt-20">
        {/* Left Panel */}
        <div className="w-80 p-4 space-y-4 overflow-y-auto">
          <CollisionAlerts collisions={systemData?.collisions || []} />
          <FuelPanel satellites={systemData?.satellites || []} />
        </div>

        {/* Center - 3D Visualization */}
        <div className="flex-1 relative">
          <SatelliteViewer 
            satellites={systemData?.satellites || []}
            debris={systemData?.debris || []}
            collisions={systemData?.collisions || []}
          />
        </div>

        {/* Right Panel */}
        <div className="w-80 p-4 overflow-y-auto">
          <ManeuverTimeline satellites={systemData?.satellites || []} />
        </div>
      </div>
    </div>
  )
}

export default App
