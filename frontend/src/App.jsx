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
  const [debugInfo, setDebugInfo] = useState('')

  useEffect(() => {
    // WebSocket connection for real-time updates
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const wsUrl = `${protocol}//${window.location.hostname}:8000/ws`
    
    console.log('Connecting to WebSocket:', wsUrl)
    setDebugInfo(`Connecting to ${wsUrl}...`)
    
    let ws = null
    let reconnectTimeout = null

    const connect = () => {
      try {
        ws = new WebSocket(wsUrl)

        ws.onopen = () => {
          console.log('✅ WebSocket connected')
          setWsConnected(true)
          setLoading(false)
          setDebugInfo('Connected! Receiving data...')
        }

        ws.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data)
            console.log('📡 Received data:', {
              satellites: data.satellites?.length,
              debris: data.debris?.length,
              collisionRisks: data.collision_risks?.length
            })
            
            // Transform data to match expected format
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
              collisions: data.satellites
                ?.filter(s => s.at_risk)
                .map(s => ({
                  satellite_id: s.object_id,
                  severity: s.status === 'critical' ? 'critical' : 'warning',
                  min_distance_meters: s.status === 'critical' ? 50 : 500
                })) || []
            }
            
            setSystemData(transformedData)
            setDebugInfo(`Live: ${transformedData.satellites.length} sats, ${transformedData.debris.length} debris`)
          } catch (error) {
            console.error('❌ Error parsing WebSocket message:', error)
            setDebugInfo(`Parse error: ${error.message}`)
          }
        }

        ws.onerror = (error) => {
          console.error('❌ WebSocket error:', error)
          setWsConnected(false)
          setDebugInfo('Connection error')
        }

        ws.onclose = () => {
          console.log('🔌 WebSocket disconnected')
          setWsConnected(false)
          setDebugInfo('Disconnected. Reconnecting...')
          
          // Attempt to reconnect after 3 seconds
          reconnectTimeout = setTimeout(() => {
            console.log('🔄 Attempting to reconnect...')
            connect()
          }, 3000)
        }

        // Send ping every 30 seconds to keep connection alive
        const pingInterval = setInterval(() => {
          if (ws && ws.readyState === WebSocket.OPEN) {
            ws.send('ping')
          }
        }, 30000)

        return () => {
          clearInterval(pingInterval)
        }
      } catch (error) {
        console.error('❌ WebSocket connection error:', error)
        setWsConnected(false)
        setDebugInfo(`Connection failed: ${error.message}`)
      }
    }

    connect()

    return () => {
      if (reconnectTimeout) clearTimeout(reconnectTimeout)
      if (ws) {
        ws.close()
      }
    }
  }, [])

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen bg-space-dark">
        <div className="text-center">
          <div className="text-cyan-400 text-2xl animate-pulse mb-4">
            INITIALIZING ACM SYSTEM...
          </div>
          <div className="text-gray-400 text-sm mb-2">
            Generating constellation and starting simulation...
          </div>
          <div className="text-gray-500 text-xs">
            {debugInfo}
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
              Autonomous Constellation Manager v2.1 - Real-time Simulation
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
                {wsConnected ? 'LIVE' : 'DISCONNECTED'}
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
                <div className="text-sm">{debugInfo}</div>
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
