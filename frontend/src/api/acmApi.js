import axios from 'axios'

const API_BASE = '/api'

export const fetchSystemData = async () => {
  try {
    const [statusRes, satellitesRes, debrisRes, collisionsRes] = await Promise.all([
      axios.get(`${API_BASE}/telemetry/status`),
      axios.get(`${API_BASE}/telemetry/satellites`),
      axios.get(`${API_BASE}/telemetry/debris`),
      axios.get(`${API_BASE}/collisions?hours_ahead=24`)
    ])

    return {
      status: statusRes.data,
      satellites: satellitesRes.data.satellites || [],
      debris: debrisRes.data.debris || [],
      collisions: collisionsRes.data.collisions || []
    }
  } catch (error) {
    console.error('API Error:', error)
    return {
      status: {},
      satellites: [],
      debris: [],
      collisions: []
    }
  }
}

export const scheduleManeuver = async (satelliteId, maneuverTime, deltaV) => {
  const response = await axios.post(`${API_BASE}/maneuver/schedule`, {
    satellite_id: satelliteId,
    maneuver_time: maneuverTime,
    delta_v_vector: deltaV
  })
  return response.data
}

export const optimizeManeuvers = async (satelliteId) => {
  const response = await axios.post(`${API_BASE}/maneuver/optimize/${satelliteId}`)
  return response.data
}

export const getScheduledManeuvers = async (satelliteId) => {
  const response = await axios.get(`${API_BASE}/maneuver/schedule/${satelliteId}`)
  return response.data
}
