import React, { useRef, useMemo, useState } from 'react'
import { Canvas, useFrame } from '@react-three/fiber'
import { OrbitControls, Stars, Line } from '@react-three/drei'
import * as THREE from 'three'

function Earth() {
  const earthRef = useRef()
  
  useFrame(() => {
    if (earthRef.current) {
      earthRef.current.rotation.y += 0.001
    }
  })

  return (
    <mesh ref={earthRef}>
      <sphereGeometry args={[6.371, 64, 64]} />
      <meshStandardMaterial 
        color="#1e40af"
        emissive="#0a1f5f"
        emissiveIntensity={0.3}
      />
    </mesh>
  )
}

function Satellite({ position, id, hasCollision, velocity }) {
  const meshRef = useRef()
  const [hovered, setHovered] = useState(false)
  
  useFrame(() => {
    if (meshRef.current && hasCollision) {
      meshRef.current.material.emissiveIntensity = 
        0.5 + Math.sin(Date.now() * 0.01) * 0.5
    }
  })

  const pos = new THREE.Vector3(position[0], position[2], position[1])

  return (
    <group position={pos}>
      <mesh 
        ref={meshRef}
        onPointerOver={() => setHovered(true)}
        onPointerOut={() => setHovered(false)}
      >
        <boxGeometry args={[0.3, 0.3, 0.3]} />
        <meshStandardMaterial 
          color={hasCollision ? "#ff0000" : "#00ff00"}
          emissive={hasCollision ? "#ff0000" : "#00ff00"}
          emissiveIntensity={hasCollision ? 1.0 : 0.5}
        />
      </mesh>
      
      {/* Solar panels */}
      <mesh position={[0.5, 0, 0]}>
        <boxGeometry args={[0.8, 0.05, 0.4]} />
        <meshStandardMaterial color="#1e90ff" metalness={0.8} />
      </mesh>
      <mesh position={[-0.5, 0, 0]}>
        <boxGeometry args={[0.8, 0.05, 0.4]} />
        <meshStandardMaterial color="#1e90ff" metalness={0.8} />
      </mesh>
      
      {/* Label */}
      {hovered && (
        <sprite scale={[3, 1.5, 1]} position={[0, 1.5, 0]}>
          <spriteMaterial 
            color="#00ffff"
            transparent
            opacity={0.9}
          />
        </sprite>
      )}
    </group>
  )
}

function Debris({ position, size }) {
  const pos = new THREE.Vector3(position[0], position[2], position[1])

  return (
    <mesh position={pos}>
      <sphereGeometry args={[size * 0.05, 8, 8]} />
      <meshStandardMaterial 
        color="#ff6600"
        emissive="#ff3300"
        emissiveIntensity={0.3}
      />
    </mesh>
  )
}

function RealTimeOrbitLine({ position, velocity, color = "#00ffff", segments = 200 }) {
  const points = useMemo(() => {
    // Real-time RK4 orbital propagation
    const MU = 398600.4418
    const dt = 60 // 60 second timestep
    const duration = 5400 // 1.5 hours ahead
    const steps = Math.floor(duration / dt)
    
    let state = [...position, ...velocity]
    const orbitPoints = []
    
    // RK4 integration
    for (let i = 0; i < Math.min(steps, segments); i++) {
      const pos = state.slice(0, 3)
      orbitPoints.push(new THREE.Vector3(pos[0], pos[2], pos[1]))
      
      // RK4 step
      const k1 = derivatives(state)
      const k2 = derivatives(state.map((s, i) => s + 0.5 * dt * k1[i]))
      const k3 = derivatives(state.map((s, i) => s + 0.5 * dt * k2[i]))
      const k4 = derivatives(state.map((s, i) => s + dt * k3[i]))
      
      state = state.map((s, i) => s + (dt / 6.0) * (k1[i] + 2*k2[i] + 2*k3[i] + k4[i]))
    }
    
    function derivatives(s) {
      const pos = s.slice(0, 3)
      const vel = s.slice(3, 6)
      const r = Math.sqrt(pos[0]**2 + pos[1]**2 + pos[2]**2)
      const acc = pos.map(p => -MU * p / (r ** 3))
      return [...vel, ...acc]
    }
    
    return orbitPoints
  }, [position, velocity, segments])

  return (
    <Line
      points={points}
      color={color}
      lineWidth={2}
      transparent
      opacity={0.6}
    />
  )
}

function CollisionWarningLine({ sat1Pos, sat2Pos }) {
  const points = useMemo(() => {
    return [
      new THREE.Vector3(sat1Pos[0], sat1Pos[2], sat1Pos[1]),
      new THREE.Vector3(sat2Pos[0], sat2Pos[2], sat2Pos[1])
    ]
  }, [sat1Pos, sat2Pos])

  return (
    <Line
      points={points}
      color="#ff0000"
      lineWidth={3}
      transparent
      opacity={0.8}
      dashed
      dashScale={50}
      dashSize={1}
      gapSize={0.5}
    />
  )
}

function SatelliteViewer({ satellites, debris, collisions }) {
  const satellitesAtRisk = new Set(
    collisions.map(c => c.satellite_id)
  )

  // Create collision warning lines
  const collisionLines = useMemo(() => {
    return collisions.slice(0, 10).map(collision => {
      const sat = satellites.find(s => s.object_id === collision.satellite_id)
      const deb = debris.find(d => d.object_id === collision.debris_id)
      
      if (sat && deb) {
        return {
          id: `${collision.satellite_id}-${collision.debris_id}`,
          sat1Pos: sat.position,
          sat2Pos: deb.position
        }
      }
      return null
    }).filter(Boolean)
  }, [collisions, satellites, debris])

  return (
    <div className="w-full h-full">
      <Canvas camera={{ position: [30, 30, 30], fov: 60 }}>
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

        {/* Satellites with real-time orbit prediction */}
        {satellites.map((sat) => (
          <React.Fragment key={sat.object_id}>
            <Satellite 
              position={sat.position}
              velocity={sat.velocity}
              id={sat.object_id}
              hasCollision={satellitesAtRisk.has(sat.object_id)}
            />
            <RealTimeOrbitLine 
              position={sat.position}
              velocity={sat.velocity}
              color={satellitesAtRisk.has(sat.object_id) ? "#ff0000" : "#00ffff"}
            />
          </React.Fragment>
        ))}

        {/* Debris with orbit lines */}
        {debris.map((deb) => (
          <React.Fragment key={deb.object_id}>
            <Debris 
              position={deb.position}
              size={deb.size_estimate || 1}
            />
            <RealTimeOrbitLine 
              position={deb.position}
              velocity={deb.velocity}
              color="#ff6600"
              segments={100}
            />
          </React.Fragment>
        ))}

        {/* Collision warning lines */}
        {collisionLines.map((line) => (
          <CollisionWarningLine
            key={line.id}
            sat1Pos={line.sat1Pos}
            sat2Pos={line.sat2Pos}
          />
        ))}

        {/* Controls */}
        <OrbitControls 
          enablePan={true}
          enableZoom={true}
          enableRotate={true}
          minDistance={10}
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
          <div className="flex items-center gap-2">
            <div className="w-8 h-0.5 bg-red-500" style={{borderTop: '2px dashed'}}></div>
            <span>Collision Paths</span>
          </div>
        </div>
        <div className="mt-3 pt-3 border-t border-cyan-500 text-xs text-gray-400">
          Real-time RK4 propagation
        </div>
      </div>

      {/* Stats overlay */}
      <div className="absolute top-4 left-4 panel text-xs">
        <div className="font-bold text-cyan-400 mb-2">VISUALIZATION</div>
        <div className="space-y-1 text-gray-300">
          <div>Satellites: {satellites.length}</div>
          <div>Debris: {debris.length}</div>
          <div>Orbit Lines: {satellites.length + debris.length}</div>
          <div>Warning Lines: {collisionLines.length}</div>
        </div>
      </div>
    </div>
  )
}

export default SatelliteViewer
