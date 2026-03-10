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
    console.log('🔌 Initializing WebSocket connection...')
    
    let ws = null
    let reconnectTimeout = null
    let connectionAttempts = 0
    const maxAttempts = 5

    const connect = () => {
      connectionAttempts++
      console.log(`🔌 Connection attempt ${connectionAttempts}/${maxAttempts}`)
      
      // Use direct WebSocket connection
      const wsUrl = 'ws://localhost:8000/ws/simulation'
      console.log('🔗 Connecting to:', wsUrl)
      
      try {
        ws = new WebSocket(wsUrl)

        ws.onopen = () => {
          console.log('✅ WebSocket connected successfully!')
          setWsConnected(true)
          setLoading(false)
          connectionAttempts = 0
          
          // Send ping every 30 seconds
          const pingInterval = setInterval(() => {
            if (ws && ws.readyState === WebSocket.OPEN) {
              ws.send('ping')
            } else {
              clearInterval(pingInterval)
            }
          }, 30000)
        }

        ws.onmessage = (event) => {
          try {
            // Handle pong messages
            if (event.data === 'pong') {
              console.log('🏓 Received pong')
              return
            }

            // Parse JSON data
            const data = JSON.parse(event.data)
            console.log('📡 Received simulation data:', {
              satellites: data.satellites?.length || 0,
              debris: data.debris?.length || 0,
              threats: data.threats || 0
            })
            
            // Transform data for frontend - handle new payload structure
            const transformedData = {
              status: {
                total_satellites: data.satellites?.length || 0,
                total_debris: data.debris?.length || 0,
                operational_satellites: data.satellites?.filter(s => s.risk_status === 'safe').length || 0,
                critical_satellites: data.satellites?.filter(s => s.risk_status === 'danger').length || 0,
                timestamp: data.timestamp
              },
              satellites: (data.satellites || []).map(sat => ({
                object_id: sat.id,
                position: sat.position,
                velocity: sat.velocity,
                fuel_remaining: sat.fuel,
                status: sat.risk_status === 'danger' ? 'critical' : 'operational',
                risk_status: sat.risk_status
              })),
              debris: (data.debris || []).map(deb => ({
                object_id: deb.id,
                position: deb.position,
                velocity: deb.velocity,
                size_estimate: 1.0
              })),
              threats: data.threats || 0,
              collisions: (data.satellites || [])
                .filter(sat => sat.risk_status === 'danger')
                .map((sat, idx) => ({
                  satellite_id: sat.id,
                  debris_id: `THREAT-${idx}`,
                  severity: 'high'
                }))
            }
            
            setSystemData(transformedData)
            setUpdateCount(prev => prev + 1)
            
          } catch (error) {
            console.error('❌ Parse error:', error)
            console.error('Raw data:', event.data?.substring(0, 200))
          }
        }

        ws.onerror = (error) => {
          console.error('❌ WebSocket error:', error)
          setWsConnected(false)
        }

        ws.onclose = (event) => {
          console.log(`🔌 WebSocket closed: ${event.code} - ${event.reason}`)
          setWsConnected(false)
          
          // Reconnect with exponential backoff
          if (connectionAttempts < maxAttempts) {
            const delay = Math.min(1000 * Math.pow(2, connectionAttempts - 1), 10000)
            console.log(`🔄 Reconnecting in ${delay}ms...`)
            reconnectTimeout = setTimeout(connect, delay)
          } else {
            console.log('❌ Max connection attempts reached')
            setLoading(false)
          }
        }

      } catch (error) {
        console.error('❌ WebSocket creation error:', error)
        setWsConnected(false)
        setLoading(false)
      }
    }

    // Start connection
    connect()

    // Timeout for loading screen
    const loadingTimeout = setTimeout(() => {
      if (loading) {
        console.log('⏰ Loading timeout - showing UI anyway')
        setLoading(false)
      }
    }, 10000)

    return () => {
      if (reconnectTimeout) clearTimeout(reconnectTimeout)
      if (loadingTimeout) clearTimeout(loadingTimeout)
      if (ws) {
        console.log('🧹 Cleaning up WebSocket connection')
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
