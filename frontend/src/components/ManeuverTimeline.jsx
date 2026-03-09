import React, { useState, useEffect } from 'react'
import { getScheduledManeuvers, optimizeManeuvers } from '../api/acmApi'
import axios from 'axios'

function ManeuverTimeline({ satellites }) {
  const [selectedSat, setSelectedSat] = useState(null)
  const [maneuvers, setManeuvers] = useState([])
  const [loading, setLoading] = useState(false)
  const [aiLoading, setAiLoading] = useState(false)

  useEffect(() => {
    if (selectedSat) {
      loadManeuvers(selectedSat)
    }
  }, [selectedSat])

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

  return (
    <div className="panel">
      <h2 className="panel-title">🚀 Maneuver Timeline</h2>
      
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
              {sat.object_id}
            </option>
          ))}
        </select>
      </div>

      {selectedSat && (
        <>
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
                return (
                  <div 
                    key={idx}
                    className={`border rounded p-3 bg-gray-800 bg-opacity-50 ${
                      isAI ? 'border-purple-500' : 'border-cyan-500'
                    }`}
                  >
                    <div className="flex justify-between items-start mb-2">
                      <span className={`text-xs font-bold px-2 py-1 rounded ${
                        isAI ? 'bg-gradient-to-r from-purple-600 to-pink-600' :
                        maneuver.maneuver_type === 'collision_avoidance' 
                          ? 'bg-red-600' 
                          : 'bg-blue-600'
                      }`}>
                        {isAI && '🧠 '}
                        {maneuver.maneuver_type?.toUpperCase()}
                      </span>
                      <span className="text-xs text-gray-400">
                        T+{maneuver.execution_time_hours?.toFixed(1)}h
                      </span>
                    </div>
                    
                    <div className="text-sm space-y-1">
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
