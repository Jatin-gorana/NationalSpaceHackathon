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
    let fallbackInterval = null
    let connectionAttempts = 0
    const maxAttempts = 10

    const connect = () => {
      connectionAttempts++
      console.log(`🔌 Connection attempt ${connectionAttempts}/${maxAttempts}`)
      
      try {
        ws = new WebSocket(wsUrl)

        ws.onopen = () => {
          console.log('✅ WebSocket connected - receiving 20 Hz updates')
          setWsConnected(true)
          setLoading(false)
          connectionAttempts = 0 // Reset on successful connection
          
          // Clear fallback polling if WebSocket works
          if (fallbackInterval) {
            clearInterval(fallbackInterval)
            fallbackInterval = null
          }
        }

        ws.onmessage = (event) => {
          try {
            // Check if data is actually JSON
            if (!event.data || typeof event.data !== 'string') {
              console.warn('⚠️ Received non-string data:', event.data)
              return
            }

            // Check if data starts with JSON characters
            const trimmedData = event.data.trim()
            if (!trimmedData.startsWith('{') && !trimmedData.startsWith('[')) {
              console.warn('⚠️ Received non-JSON data:', trimmedData.substring(0, 100))
              return
            }

            const data = JSON.parse(event.data)
            
            // Validate data structure
            if (!data || typeof data !== 'object') {
              console.warn('⚠️ Received invalid data structure:', data)
              return
            }
            
            // Use enhanced collision data directly from backend
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
              collisions: data.collisions || []  // Use enhanced collision data from backend
            }
            
            setSystemData(transformedData)
            setUpdateCount(prev => prev + 1)
          } catch (error) {
            console.error('❌ Parse error:', error)
            console.error('❌ Raw data received:', event.data?.substring(0, 200))
            
            // Try to handle ping/pong messages
            if (event.data === 'pong') {
              console.log('🏓 Received pong')
              return
            }
            
            // If it's HTML (error page), log it
            if (event.data?.includes('<html>') || event.data?.includes('<!DOCTYPE')) {
              console.error('❌ Received HTML error page instead of JSON')
              console.error('This usually means the backend has an error or wrong endpoint')
            }
          }
        }

        ws.onerror = (error) => {
          console.error('❌ WebSocket error:', error)
          setWsConnected(false)
        }

        ws.onclose = () => {
          console.log('🔌 WebSocket disconnected')
          setWsConnected(false)
          
          // Start fallback polling if WebSocket fails
          if (!fallbackInterval) {
            console.log('🔄 Starting fallback HTTP polling...')
            setLoading(false) // Don't stay on loading screen
            
            fallbackInterval = setInterval(async () => {
              try {
                const response = await fetch('http://localhost:8000/api/telemetry/status')
                if (response.ok) {
                  const data = await response.json()
                  console.log('📡 Fallback data received')
                  
                  // Transform fallback data
                  const transformedData = {
                    status: {
                      total_satellites: data.total_satellites || 0,
                      total_debris: data.total_debris || 0,
                      operational_satellites: data.operational_satellites || 0,
                      critical_satellites: data.critical_satellites || 0,
                      timestamp: new Date().toISOString()
                    },
                    satellites: data.satellites || [],
                    debris: data.debris || [],
                    threats: data.threats || 0,
                    collisions: data.collisions || []
                  }
                  
                  setSystemData(transformedData)
                  setUpdateCount(prev => prev + 1)
                  setLoading(false)
                }
              } catch (error) {
                console.error('❌ Fallback polling error:', error)
              }
            }, 2000) // Poll every 2 seconds as fallback
          }
          
          // Reconnect with exponential backoff
          if (connectionAttempts < maxAttempts) {
            const delay = Math.min(1000 * Math.pow(2, connectionAttempts - 1), 10000) // Max 10 seconds
            console.log(`🔄 Reconnecting in ${delay}ms...`)
            reconnectTimeout = setTimeout(() => {
              connect()
            }, delay)
          } else {
            console.log('❌ Max connection attempts reached, using fallback only')
          }
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
        
        // Start fallback polling immediately if WebSocket fails to connect
        if (!fallbackInterval) {
          console.log('🔄 WebSocket failed, starting immediate fallback...')
          setLoading(false) // Don't stay on loading screen
          
          // Try to get data immediately using quick endpoint first
          (async () => {
            try {
              // Try quick status first
              let response = await fetch('http://localhost:8000/api/quick-status')
              if (!response.ok) {
                // Fallback to full status
                response = await fetch('http://localhost:8000/api/telemetry/status')
              }
              
              if (response.ok) {
                const data = await response.json()
                console.log('📡 Immediate fallback data received')
                
                const transformedData = {
                  status: {
                    total_satellites: data.total_satellites || 0,
                    total_debris: data.total_debris || 0,
                    operational_satellites: data.operational_satellites || 0,
                    critical_satellites: data.critical_satellites || 0,
                    timestamp: new Date().toISOString()
                  },
                  satellites: data.satellites || [],
                  debris: data.debris || [],
                  threats: data.threats || 0,
                  collisions: data.collisions || []
                }
                
                setSystemData(transformedData)
                setUpdateCount(prev => prev + 1)
                setLoading(false)
              }
            } catch (error) {
              console.error('❌ Immediate fallback error:', error)
            }
          })()
          
          fallbackInterval = setInterval(async () => {
            try {
              const response = await fetch('http://localhost:8000/api/telemetry/status')
              if (response.ok) {
                const data = await response.json()
                
                const transformedData = {
                  status: {
                    total_satellites: data.total_satellites || 0,
                    total_debris: data.total_debris || 0,
                    operational_satellites: data.operational_satellites || 0,
                    critical_satellites: data.critical_satellites || 0,
                    timestamp: new Date().toISOString()
                  },
                  satellites: data.satellites || [],
                  debris: data.debris || [],
                  threats: data.threats || 0,
                  collisions: data.collisions || []
                }
                
                setSystemData(transformedData)
                setUpdateCount(prev => prev + 1)
              }
            } catch (error) {
              console.error('❌ Fallback polling error:', error)
            }
          }, 2000)
        }
        
        // Still try to reconnect WebSocket
        if (connectionAttempts < maxAttempts) {
          const delay = Math.min(1000 * connectionAttempts, 5000) // Max 5 seconds
          reconnectTimeout = setTimeout(() => {
            connect()
          }, delay)
        }
      }
    }

    connect()

    // Timeout for loading screen (don't wait more than 10 seconds)
    const loadingTimeout = setTimeout(() => {
      if (loading) {
        console.log('⏰ Loading timeout reached, forcing fallback mode')
        setLoading(false)
        
        // Force fallback if not already started
        if (!fallbackInterval) {
          (async () => {
            try {
              const response = await fetch('http://localhost:8000/api/telemetry/status')
              if (response.ok) {
                const data = await response.json()
                console.log('📡 Timeout fallback data received')
                
                const transformedData = {
                  status: {
                    total_satellites: data.total_satellites || 0,
                    total_debris: data.total_debris || 0,
                    operational_satellites: data.operational_satellites || 0,
                    critical_satellites: data.critical_satellites || 0,
                    timestamp: new Date().toISOString()
                  },
                  satellites: data.satellites || [],
                  debris: data.debris || [],
                  threats: data.threats || 0,
                  collisions: data.collisions || []
                }
                
                setSystemData(transformedData)
                setUpdateCount(prev => prev + 1)
              }
            } catch (error) {
              console.error('❌ Timeout fallback error:', error)
              // Show empty state if backend is completely unavailable
              setSystemData({
                status: { total_satellites: 0, total_debris: 0, operational_satellites: 0, critical_satellites: 0, timestamp: new Date().toISOString() },
                satellites: [],
                debris: [],
                threats: 0,
                collisions: []
              })
            }
          })()
        }
      }
    }, 10000) // 10 second timeout

    return () => {
      if (reconnectTimeout) clearTimeout(reconnectTimeout)
      if (fallbackInterval) clearInterval(fallbackInterval)
      if (loadingTimeout) clearTimeout(loadingTimeout)
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
