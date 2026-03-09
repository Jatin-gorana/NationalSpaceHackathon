import React, { useState, useEffect } from 'react'
import SatelliteViewer from './components/SatelliteViewer'
import CollisionAlerts from './components/CollisionAlerts'
import FuelPanel from './components/FuelPanel'
import ManeuverTimeline from './components/ManeuverTimeline'
import SystemStatus from './components/SystemStatus'

function App() {
  const [systemData, setSystemData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [wsConnected, setWsConnected] = useState(false)
  const [updateCount, setUpdateCount] = useState(0)

  useEffect(() => {
    // WebSocket connection for real-time updates (20 Hz)
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const wsUrl = `${protocol}//${window.location.hostname}:8000/ws/simulation`
    
    console.log('🔌 Connecting to WebSocket:', wsUrl)
    
    let ws = null
    let reconnectTimeout = null

    const connect = () => {
      try {
        ws = new WebSocket(wsUrl)

        ws.onopen = () => {
          console.log('✅ WebSocket connected - receiving 20 Hz updates')
          setWsConnected(true)
          setLoading(false)
        }

        ws.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data)
            
            // Transform data
            const transformedData = {
              status: {
                total_satellites: data.satellites?.length || 0,
                total_debris: data.debris?.length || 0,
                operational_satellites: data.satellites?.filter(s => s.status === 'operational').length || 0,
                critical_satellites: data.satellites?.filter(s => s.status === 'critical').length || 0,
                timestamp: data.timestamp
              },
              satellites: data.satellites || [],
              debris: data.debris || [],
              threats: data.threats || 0,
              collisions: data.satellites
                ?.filter(s => s.at_risk)
                .map(s => ({
                  satellite_id: s.object_id,
                  severity: s.status === 'critical' ? 'critical' : 'warning',
                  min_distance_meters: s.status === 'critical' ? 50 : 500
                })) || []
            }
            
            setSystemData(transformedData)
            setUpdateCount(prev => prev + 1)
          } catch (error) {
            console.error('❌ Parse error:', error)
          }
        }

        ws.onerror = (error) => {
          console.error('❌ WebSocket error:', error)
          setWsConnected(false)
        }

        ws.onclose = () => {
          console.log('🔌 WebSocket disconnected')
          setWsConnected(false)
          
          // Reconnect after 3 seconds
          reconnectTimeout = setTimeout(() => {
            console.log('🔄 Reconnecting...')
            connect()
          }, 3000)
        }

        // Ping every 30 seconds
        const pingInterval = setInterval(() => {
          if (ws && ws.readyState === WebSocket.OPEN) {
            ws.send('ping')
          }
        }, 30000)

        return () => clearInterval(pingInterval)
      } catch (error) {
        console.error('❌ Connection error:', error)
        setWsConnected(false)
      }
    }

    connect()

    return () => {
      if (reconnectTimeout) clearTimeout(reconnectTimeout)
      if (ws) ws.close()
    }
  }, [])

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen bg-space-dark">
        <div className="text-center">
          <div className="text-cyan-400 text-2xl animate-pulse mb-4">
            INITIALIZING ACM SYSTEM...
          </div>
          <div className="text-gray-400 text-sm">
            Generating 50 satellites and 500 debris objects...
          </div>
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
            <p className="text-sm text-gray-400">
              Real-Time Simulation • 20 Hz Updates • {updateCount} frames
            </p>
          </div>
          <div className="flex items-center gap-4">
            <div className={`flex items-center gap-2 px-3 py-1 rounded ${
              wsConnected ? 'bg-green-900 bg-opacity-30' : 'bg-red-900 bg-opacity-30'
            }`}>
              <div className={`w-2 h-2 rounded-full ${
                wsConnected ? 'bg-green-500 animate-pulse' : 'bg-red-500'
              }`} />
              <span className="text-xs text-gray-300">
                {wsConnected ? 'LIVE 20Hz' : 'DISCONNECTED'}
              </span>
            </div>
            <SystemStatus data={systemData} />
          </div>
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
          {systemData && systemData.satellites && systemData.satellites.length > 0 ? (
            <SatelliteViewer 
              satellites={systemData.satellites}
              debris={systemData.debris || []}
              collisions={systemData.collisions || []}
            />
          ) : (
            <div className="flex items-center justify-center h-full">
              <div className="text-center text-gray-400">
                <div className="text-xl mb-2">Waiting for simulation data...</div>
              </div>
            </div>
          )}
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
