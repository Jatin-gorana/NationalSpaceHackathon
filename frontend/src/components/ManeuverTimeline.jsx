import React, { useState, useEffect } from 'react'
import { getScheduledManeuvers, optimizeManeuvers } from '../api/acmApi'
import axios from 'axios'

function ManeuverTimeline({ satellites }) {
  const [selectedSat, setSelectedSat] = useState(null)
  const [maneuvers, setManeuvers] = useState([])
  const [loading, setLoading] = useState(false)
  const [aiLoading, setAiLoading] = useState(false)
  const [autoResolveLoading, setAutoResolveLoading] = useState(false)

  useEffect(() => {
    if (selectedSat) {
      loadManeuvers(selectedSat)
    }
  }, [selectedSat])

  // Auto-refresh maneuvers from satellite data
  useEffect(() => {
    if (selectedSat && satellites) {
      const sat = satellites.find(s => s.object_id === selectedSat)
      if (sat && sat.scheduled_maneuvers) {
        setManeuvers(sat.scheduled_maneuvers)
      }
    }
  }, [satellites, selectedSat])

  const loadManeuvers = async (satId) => {
    try {
      const data = await getScheduledManeuvers(satId)
      setManeuvers(data.scheduled_maneuvers || [])
    } catch (error) {
      console.error('Failed to load maneuvers:', error)
    }
  }

  const handleOptimize = async () => {
    if (!selectedSat) return
    
    setLoading(true)
    try {
      await optimizeManeuvers(selectedSat)
      await loadManeuvers(selectedSat)
    } catch (error) {
      console.error('Optimization failed:', error)
    }
    setLoading(false)
  }

  const handleAIOptimize = async () => {
    if (!selectedSat) return
    
    setAiLoading(true)
    try {
      const response = await axios.post(`/api/ai/optimize/${selectedSat}`)
      console.log('AI Optimization result:', response.data)
      await loadManeuvers(selectedSat)
    } catch (error) {
      console.error('AI optimization failed:', error)
    }
    setAiLoading(false)
  }

  const handleAutoResolve = async () => {
    setAutoResolveLoading(true)
    try {
      const response = await axios.post('/api/ai/auto-resolve')
      console.log('✅ Auto-resolve result:', response.data)
      
      // Show success message
      if (response.data.satellites_resolved > 0) {
        alert(`✅ Scheduled maneuvers for ${response.data.satellites_resolved} satellites at risk!`)
      } else {
        alert('ℹ️ No collision risks detected')
      }
      
      // Reload maneuvers if satellite is selected
      if (selectedSat) {
        await loadManeuvers(selectedSat)
      }
    } catch (error) {
      console.error('Auto-resolve failed:', error)
      alert('❌ Auto-resolve failed')
    }
    setAutoResolveLoading(false)
  }

  const getManeuverStatus = (maneuver, simulationTime) => {
    const execTime = maneuver.execution_time_seconds || 0
    const timeUntil = execTime - (simulationTime || 0)
    
    if (timeUntil <= 0) {
      return { status: 'executed', color: 'text-green-400', icon: '✅' }
    } else if (timeUntil < 60) {
      return { status: 'executing', color: 'text-yellow-400 animate-pulse', icon: '⚡' }
    } else {
      return { status: 'scheduled', color: 'text-cyan-400', icon: '📅' }
    }
  }

  const selectedSatellite = satellites.find(s => s.object_id === selectedSat)

  return (
    <div className="panel">
      <h2 className="panel-title">🚀 Maneuver Timeline</h2>
      
      {/* Auto-Resolve All Button */}
      <div className="mb-4">
        <button 
          onClick={handleAutoResolve}
          disabled={autoResolveLoading}
          className="w-full bg-gradient-to-r from-red-600 to-orange-600 hover:from-red-700 hover:to-orange-700 text-white font-bold py-3 px-4 rounded transition-colors shadow-lg"
        >
          {autoResolveLoading ? (
            <span className="flex items-center justify-center gap-2">
              <span className="animate-spin">🤖</span>
              SCHEDULING MANEUVERS...
            </span>
          ) : (
            <span className="flex items-center justify-center gap-2">
              🤖 AUTO-RESOLVE ALL THREATS
            </span>
          )}
        </button>
        <div className="text-xs text-gray-400 mt-1 text-center">
          Automatically schedule collision avoidance for all at-risk satellites
        </div>
      </div>

      {/* Satellite Selector */}
      <div className="mb-4">
        <label className="text-xs text-gray-400 mb-2 block">Select Satellite</label>
        <select 
          className="w-full bg-gray-800 border border-cyan-500 rounded px-3 py-2 text-cyan-400"
          value={selectedSat || ''}
          onChange={(e) => setSelectedSat(e.target.value)}
        >
          <option value="">-- Select --</option>
          {satellites.map(sat => (
            <option key={sat.object_id} value={sat.object_id}>
              {sat.object_id} {sat.at_risk ? '⚠️' : ''} {sat.in_recovery ? '🔄' : ''}
            </option>
          ))}
        </select>
      </div>

      {selectedSat && (
        <>
          {/* Satellite Status */}
          {selectedSatellite && (
            <div className="mb-4 p-3 bg-gray-800 rounded border border-gray-700">
              <div className="text-xs space-y-1">
                <div className="flex justify-between">
                  <span className="text-gray-400">Status:</span>
                  <span className={`font-bold ${
                    selectedSatellite.status === 'critical' ? 'text-red-400' :
                    selectedSatellite.status === 'warning' ? 'text-yellow-400' :
                    selectedSatellite.status === 'maneuvering' ? 'text-cyan-400' :
                    selectedSatellite.status === 'graveyard' ? 'text-gray-400' :
                    'text-green-400'
                  }`}>
                    {selectedSatellite.status?.toUpperCase()}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Fuel:</span>
                  <span className={`font-bold ${
                    selectedSatellite.fuel_remaining < 10 ? 'text-red-400' :
                    selectedSatellite.fuel_remaining < 30 ? 'text-yellow-400' :
                    'text-green-400'
                  }`}>
                    {selectedSatellite.fuel_remaining?.toFixed(1)}%
                  </span>
                </div>
                {selectedSatellite.in_recovery && (
                  <div className="text-cyan-400 text-center mt-2">
                    🔄 Orbit Recovery Active
                  </div>
                )}
              </div>
            </div>
          )}

          <div className="space-y-2 mb-4">
            <button 
              onClick={handleOptimize}
              disabled={loading}
              className="btn-primary w-full"
            >
              {loading ? 'OPTIMIZING...' : '⚡ STANDARD OPTIMIZE'}
            </button>

            <button 
              onClick={handleAIOptimize}
              disabled={aiLoading}
              className="w-full bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white font-bold py-2 px-4 rounded transition-colors"
            >
              {aiLoading ? (
                <span className="flex items-center justify-center gap-2">
                  <span className="animate-spin">🧠</span>
                  AI OPTIMIZING...
                </span>
              ) : (
                <span className="flex items-center justify-center gap-2">
                  🧠 AI OPTIMIZE (GA)
                </span>
              )}
            </button>
          </div>

          <div className="text-xs text-gray-400 mb-4 p-2 bg-gray-800 rounded">
            <div className="font-bold text-cyan-400 mb-1">AI Optimization:</div>
            <div>• Genetic Algorithm</div>
            <div>• Multi-objective fitness</div>
            <div>• Minimum fuel usage</div>
            <div>• Collision avoidance</div>
          </div>

          <div className="space-y-3">
            {maneuvers.length === 0 ? (
              <div className="text-center text-gray-500 py-4">
                No scheduled maneuvers
              </div>
            ) : (
              maneuvers.map((maneuver, idx) => {
                const isAI = maneuver.optimization_method === 'genetic_algorithm'
                const status = getManeuverStatus(maneuver, 0)
                
                return (
                  <div 
                    key={idx}
                    className={`border rounded p-3 bg-gray-800 bg-opacity-50 ${
                      isAI ? 'border-purple-500' :
                      maneuver.maneuver_type === 'graveyard_orbit' ? 'border-gray-500' :
                      maneuver.maneuver_type === 'orbit_recovery' ? 'border-blue-500' :
                      'border-cyan-500'
                    }`}
                  >
                    <div className="flex justify-between items-start mb-2">
                      <span className={`text-xs font-bold px-2 py-1 rounded ${
                        isAI ? 'bg-gradient-to-r from-purple-600 to-pink-600' :
                        maneuver.maneuver_type === 'collision_avoidance' ? 'bg-red-600' :
                        maneuver.maneuver_type === 'graveyard_orbit' ? 'bg-gray-600' :
                        maneuver.maneuver_type === 'orbit_recovery' ? 'bg-blue-600' :
                        'bg-cyan-600'
                      }`}>
                        {isAI && '🧠 '}
                        {maneuver.maneuver_type === 'graveyard_orbit' && '🪦 '}
                        {maneuver.maneuver_type === 'orbit_recovery' && '🔄 '}
                        {maneuver.maneuver_type?.replace(/_/g, ' ').toUpperCase()}
                      </span>
                      <span className={`text-xs ${status.color}`}>
                        {status.icon} {status.status.toUpperCase()}
                      </span>
                    </div>
                    
                    <div className="text-sm space-y-1">
                      <div className="flex justify-between">
                        <span className="text-gray-400">Exec Time:</span>
                        <span className="text-cyan-400 font-mono">
                          T+{maneuver.execution_time_hours?.toFixed(2)}h
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-400">ΔV:</span>
                        <span className="text-cyan-400 font-mono">
                          {maneuver.delta_v_magnitude?.toFixed(4)} km/s
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-400">Fuel:</span>
                        <span className="text-yellow-400">
                          {maneuver.fuel_cost_percent?.toFixed(2)}%
                        </span>
                      </div>
                      {maneuver.priority && (
                        <div className="flex justify-between">
                          <span className="text-gray-400">Priority:</span>
                          <span className={`font-bold ${
                            maneuver.priority === 'critical' ? 'text-red-400' :
                            maneuver.priority === 'high' ? 'text-orange-400' :
                            'text-cyan-400'
                          }`}>
                            {maneuver.priority.toUpperCase()}
                          </span>
                        </div>
                      )}
                      {isAI && (
                        <div className="text-xs text-purple-400 mt-1">
                          ✨ AI-optimized for minimum fuel
                        </div>
                      )}
                      {maneuver.reason && (
                        <div className="text-xs text-gray-500 mt-2 italic">
                          {maneuver.reason}
                        </div>
                      )}
                    </div>
                  </div>
                )
              })
            )}
          </div>
        </>
      )}
    </div>
  )
}

export default ManeuverTimeline
