import React, { useRef, useMemo, useState, useEffect } from 'react'
import { Canvas, useFrame } from '@react-three/fiber'
import { OrbitControls, Stars } from '@react-three/drei'
import * as THREE from 'three'

// Scale factor: 1 km = 1/500 Three.js units
const VISUAL_SCALE = 1 / 500

function Earth() {
  const earthRef = useRef()
  
  useFrame(() => {
    if (earthRef.current) {
      earthRef.current.rotation.y += 0.001
    }
  })

  // Earth radius: 6371 km scaled
  const earthRadius = 6371 * VISUAL_SCALE

  return (
    <mesh ref={earthRef}>
      <sphereGeometry args={[earthRadius, 64, 64]} />
      <meshStandardMaterial 
        color="#1e40af"
        emissive="#0a1f5f"
        emissiveIntensity={0.3}
      />
    </mesh>
  )
}

function Satellite({ position, id, hasCollision }) {
  const meshRef = useRef()
  
  useFrame(() => {
    if (meshRef.current && hasCollision) {
      meshRef.current.material.emissiveIntensity = 
        0.5 + Math.sin(Date.now() * 0.01) * 0.5
    }
  })

  if (!position || position.length !== 3) {
    console.warn(`Invalid position for ${id}:`, position)
    return null
  }

  // Scale position from km to Three.js units
  const scaledPos = [
    position[0] * VISUAL_SCALE,
    position[1] * VISUAL_SCALE,
    position[2] * VISUAL_SCALE
  ]
  
  // Debug: log first satellite position
  if (id === 'SAT-001') {
    console.log('SAT-001 position (km):', position)
    console.log('SAT-001 scaled:', scaledPos)
    console.log('SAT-001 distance from origin:', Math.sqrt(scaledPos[0]**2 + scaledPos[1]**2 + scaledPos[2]**2))
  }

  return (
    <group position={scaledPos}>
      <mesh ref={meshRef}>
        <boxGeometry args={[0.3, 0.3, 0.3]} />
        <meshStandardMaterial 
          color={hasCollision ? "#ff0000" : "#00ff00"}
          emissive={hasCollision ? "#ff0000" : "#00ff00"}
          emissiveIntensity={hasCollision ? 1.0 : 0.8}
        />
      </mesh>
      
      {/* Solar panels */}
      <mesh position={[0.3, 0, 0]}>
        <boxGeometry args={[0.4, 0.02, 0.2]} />
        <meshStandardMaterial color="#1e90ff" metalness={0.8} emissive="#1e90ff" emissiveIntensity={0.3} />
      </mesh>
      <mesh position={[-0.3, 0, 0]}>
        <boxGeometry args={[0.4, 0.02, 0.2]} />
        <meshStandardMaterial color="#1e90ff" metalness={0.8} emissive="#1e90ff" emissiveIntensity={0.3} />
      </mesh>
    </group>
  )
}

function Debris({ position, size }) {
  if (!position || position.length !== 3) return null
  
  // Scale position from km to Three.js units
  const scaledPos = [
    position[0] * VISUAL_SCALE,
    position[1] * VISUAL_SCALE,
    position[2] * VISUAL_SCALE
  ]

  return (
    <mesh position={scaledPos}>
      <sphereGeometry args={[0.08, 8, 8]} />
      <meshStandardMaterial 
        color="#ff6600"
        emissive="#ff3300"
        emissiveIntensity={0.5}
      />
    </mesh>
  )
}

function OrbitLine({ position, velocity, color = "#00ffff" }) {
  const points = useMemo(() => {
    if (!position || !velocity || position.length !== 3 || velocity.length !== 3) {
      return []
    }

    const MU = 398600.4418
    const dt = 60
    const duration = 3600 // 1 hour
    const steps = Math.floor(duration / dt)
    const segments = 80
    
    let state = [...position, ...velocity]
    const orbitPoints = []
    
    function derivatives(s) {
      const pos = s.slice(0, 3)
      const vel = s.slice(3, 6)
      const r = Math.sqrt(pos[0]**2 + pos[1]**2 + pos[2]**2)
      if (r < 1) return [...vel, 0, 0, 0]
      const acc = pos.map(p => -MU * p / (r ** 3))
      return [...vel, ...acc]
    }
    
    for (let i = 0; i < Math.min(steps, segments); i++) {
      const pos = state.slice(0, 3)
      // Scale orbit points
      orbitPoints.push([
        pos[0] * VISUAL_SCALE,
        pos[1] * VISUAL_SCALE,
        pos[2] * VISUAL_SCALE
      ])
      
      const k1 = derivatives(state)
      const k2 = derivatives(state.map((s, i) => s + 0.5 * dt * k1[i]))
      const k3 = derivatives(state.map((s, i) => s + 0.5 * dt * k2[i]))
      const k4 = derivatives(state.map((s, i) => s + dt * k3[i]))
      
      state = state.map((s, i) => s + (dt / 6.0) * (k1[i] + 2*k2[i] + 2*k3[i] + k4[i]))
    }
    
    return orbitPoints
  }, [position, velocity])

  if (points.length < 2) return null

  return (
    <line>
      <bufferGeometry attach="geometry">
        <bufferAttribute
          attach="attributes-position"
          count={points.length}
          array={new Float32Array(points.flat())}
          itemSize={3}
        />
      </bufferGeometry>
      <lineBasicMaterial attach="material" color={color} transparent opacity={0.4} linewidth={1} />
    </line>
  )
}

function SatelliteViewer({ satellites = [], debris = [], collisions = [] }) {
  const [stats, setStats] = useState({ satellites: 0, debris: 0 })

  useEffect(() => {
    setStats({
      satellites: satellites.length,
      debris: debris.length
    })
    
    // Debug: log data arrival
    if (satellites.length > 0) {
      console.log('📊 Received satellites:', satellites.length)
      console.log('📊 First satellite:', satellites[0])
    }
  }, [satellites, debris])

  const satellitesAtRisk = useMemo(() => {
    return new Set(collisions.map(c => c.satellite_id))
  }, [collisions])

  // Limit debris rendering for performance (show closest 100)
  const visibleDebris = useMemo(() => {
    return debris.slice(0, 100)
  }, [debris])

  return (
    <div className="w-full h-full relative">
      <Canvas 
        camera={{ 
          position: [0, 0, 25], 
          fov: 60,
          near: 0.1,
          far: 1000
        }}
      >
        <color attach="background" args={['#000000']} />
        
        {/* Lighting */}
        <ambientLight intensity={0.3} />
        <pointLight position={[50, 50, 50]} intensity={1.5} />
        <pointLight position={[-50, -50, -50]} intensity={0.5} />
        <pointLight position={[0, 50, 0]} intensity={0.8} color="#ffffff" />

        {/* Stars */}
        <Stars 
          radius={300} 
          depth={50} 
          count={5000} 
          factor={4} 
          saturation={0} 
          fade 
        />

        {/* Earth */}
        <Earth />
        
        {/* Test satellite at fixed position */}
        <mesh position={[14, 0, 0]}>
          <boxGeometry args={[0.3, 0.3, 0.3]} />
          <meshStandardMaterial color="#ffff00" emissive="#ffff00" emissiveIntensity={1.0} />
        </mesh>

        {/* Satellites with orbit lines */}
        {satellites.map((sat) => (
          <React.Fragment key={sat.object_id}>
            <Satellite 
              position={sat.position}
              id={sat.object_id}
              hasCollision={satellitesAtRisk.has(sat.object_id)}
            />
            <OrbitLine 
              position={sat.position}
              velocity={sat.velocity}
              color={satellitesAtRisk.has(sat.object_id) ? "#ff0000" : "#00ffff"}
            />
          </React.Fragment>
        ))}

        {/* Debris (limited for performance) */}
        {visibleDebris.map((deb) => (
          <Debris 
            key={deb.object_id}
            position={deb.position}
            size={deb.size_estimate || 1}
          />
        ))}

        {/* Controls */}
        <OrbitControls 
          enablePan={true}
          enableZoom={true}
          enableRotate={true}
          minDistance={5}
          maxDistance={100}
        />
      </Canvas>

      {/* Enhanced Legend */}
      <div className="absolute bottom-4 left-4 panel text-sm">
        <div className="font-bold text-cyan-400 mb-3">LEGEND</div>
        <div className="space-y-2">
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 bg-green-500"></div>
            <span>Satellites (Safe)</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 bg-red-500 animate-pulse"></div>
            <span>Satellites (At Risk)</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 bg-orange-500 rounded-full"></div>
            <span>Debris Objects</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-8 h-0.5 bg-cyan-500"></div>
            <span>Predicted Orbits</span>
          </div>
        </div>
        <div className="mt-3 pt-3 border-t border-cyan-500 text-xs text-gray-400">
          Scale: 1:{500} • Real-time RK4
        </div>
      </div>

      {/* Stats overlay */}
      <div className="absolute top-4 left-4 panel text-xs">
        <div className="font-bold text-cyan-400 mb-2">VISUALIZATION</div>
        <div className="space-y-1 text-gray-300">
          <div>Satellites: {stats.satellites}</div>
          <div>Debris: {stats.debris}</div>
          <div>Visible: {visibleDebris.length} debris</div>
          <div>Scale: 1:500</div>
        </div>
      </div>

      {/* Camera hint */}
      <div className="absolute bottom-4 right-4 panel text-xs text-gray-400">
        <div className="font-bold text-cyan-400 mb-1">CONTROLS</div>
        <div>🖱️ Left: Rotate</div>
        <div>🖱️ Right: Pan</div>
        <div>🖱️ Scroll: Zoom</div>
      </div>
    </div>
  )
}

export default SatelliteViewer
