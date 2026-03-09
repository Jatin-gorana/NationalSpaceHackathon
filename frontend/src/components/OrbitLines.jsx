import React, { useMemo } from 'react'
import * as THREE from 'three'

function OrbitLines({ position, velocity }) {
  const points = useMemo(() => {
    // Simple orbital propagation for visualization
    const MU = 398600.4418
    const dt = 60
    const steps = 100
    
    let state = [...position, ...velocity]
    const orbitPoints = []
    
    for (let i = 0; i < steps; i++) {
      const pos = state.slice(0, 3)
      orbitPoints.push(new THREE.Vector3(pos[0], pos[2], pos[1]))
      
      // Simple RK4 step
      const r = Math.sqrt(pos[0]**2 + pos[1]**2 + pos[2]**2)
      const acc = pos.map(p => -MU * p / (r ** 3))
      
      state[0] += state[3] * dt
      state[1] += state[4] * dt
      state[2] += state[5] * dt
      state[3] += acc[0] * dt
      state[4] += acc[1] * dt
      state[5] += acc[2] * dt
    }
    
    return orbitPoints
  }, [position, velocity])

  const lineGeometry = useMemo(() => {
    const geometry = new THREE.BufferGeometry().setFromPoints(points)
    return geometry
  }, [points])

  return (
    <line geometry={lineGeometry}>
      <lineBasicMaterial 
        color="#00ffff" 
        transparent 
        opacity={0.3}
        linewidth={1}
      />
    </line>
  )
}

export default OrbitLines
