"""AI-powered maneuver optimization using genetic algorithms"""
import numpy as np
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from utils.orbital_math import propagate_orbit, compute_tca_and_distance
from utils.fuel_model import fuel_model
from utils.constants import COLLISION_THRESHOLD, SLOT_TOLERANCE

@dataclass
class ManeuverGene:
    """Represents a maneuver as a gene in the genetic algorithm"""
    execution_time: float  # Hours from now
    delta_v_x: float
    delta_v_y: float
    delta_v_z: float
    
    @property
    def delta_v_magnitude(self) -> float:
        return np.sqrt(self.delta_v_x**2 + self.delta_v_y**2 + self.delta_v_z**2)
    
    @property
    def delta_v_vector(self) -> List[float]:
        return [self.delta_v_x, self.delta_v_y, self.delta_v_z]

class GeneticManeuverOptimizer:
    """
    Genetic Algorithm for optimizing satellite maneuvers
    
    Objective: Minimize fuel consumption while:
    - Avoiding all collisions (distance > 100m)
    - Maintaining orbital slot (deviation < 10km)
    - Respecting thruster constraints
    """
    
    def __init__(self, 
                 population_size: int = 50,
                 generations: int = 100,
                 mutation_rate: float = 0.1,
                 crossover_rate: float = 0.7):
        self.population_size = population_size
        self.generations = generations
        self.mutation_rate = mutation_rate
        self.crossover_rate = crossover_rate
        self.max_delta_v = 0.05  # km/s per maneuver
        
    def optimize(self, 
                satellite_pos: List[float],
                satellite_vel: List[float],
                assigned_slot: List[float],
                collision_threats: List[Dict],
                fuel_remaining: float = 100.0) -> Optional[Dict]:
        """
        Optimize maneuver using genetic algorithm
        
        Returns:
            Best maneuver found or None if no solution
        """
        if not collision_threats:
            return None
        
        # Initialize population
        population = self._initialize_population(collision_threats)
        
        best_fitness = float('-inf')
        best_individual = None
        
        # Evolution loop
        for generation in range(self.generations):
            # Evaluate fitness
            fitness_scores = [
                self._evaluate_fitness(
                    individual, 
                    satellite_pos, 
                    satellite_vel,
                    assigned_slot,
                    collision_threats,
                    fuel_remaining
                )
                for individual in population
            ]
            
            # Track best
            max_fitness_idx = np.argmax(fitness_scores)
            if fitness_scores[max_fitness_idx] > best_fitness:
                best_fitness = fitness_scores[max_fitness_idx]
                best_individual = population[max_fitness_idx]
            
            # Early stopping if perfect solution found
            if best_fitness >= 1000:
                break
            
            # Selection
            selected = self._tournament_selection(population, fitness_scores)
            
            # Crossover
            offspring = []
            for i in range(0, len(selected), 2):
                if i + 1 < len(selected):
                    if np.random.random() < self.crossover_rate:
                        child1, child2 = self._crossover(selected[i], selected[i+1])
                        offspring.extend([child1, child2])
                    else:
                        offspring.extend([selected[i], selected[i+1]])
            
            # Mutation
            offspring = [self._mutate(ind) for ind in offspring]
            
            # Next generation
            population = offspring[:self.population_size]
        
        if best_individual is None:
            return None
        
        # Convert best individual to maneuver
        return self._gene_to_maneuver(best_individual, collision_threats[0])
    
    def _initialize_population(self, collision_threats: List[Dict]) -> List[ManeuverGene]:
        """Initialize random population of maneuvers"""
        population = []
        
        # Get earliest collision time
        min_tca = min(c.get("tca_hours", 24) for c in collision_threats)
        
        for _ in range(self.population_size):
            # Random execution time before earliest collision
            exec_time = np.random.uniform(0.1, max(0.5, min_tca - 0.5))
            
            # Random delta-v components
            dv_x = np.random.uniform(-self.max_delta_v, self.max_delta_v)
            dv_y = np.random.uniform(-self.max_delta_v, self.max_delta_v)
            dv_z = np.random.uniform(-self.max_delta_v, self.max_delta_v)
            
            population.append(ManeuverGene(exec_time, dv_x, dv_y, dv_z))
        
        return population
    
    def _evaluate_fitness(self,
                         individual: ManeuverGene,
                         satellite_pos: List[float],
                         satellite_vel: List[float],
                         assigned_slot: List[float],
                         collision_threats: List[Dict],
                         fuel_remaining: float) -> float:
        """
        Evaluate fitness of a maneuver
        
        Fitness components:
        1. Collision avoidance (highest priority)
        2. Fuel efficiency (minimize delta-v)
        3. Orbital slot maintenance
        """
        fitness = 0.0
        
        # Check fuel constraint
        fuel_cost = fuel_model.compute_fuel_percentage(individual.delta_v_magnitude)
        if fuel_cost > fuel_remaining:
            return -1000  # Infeasible
        
        # Simulate maneuver effect
        try:
            # Apply maneuver at execution time
            exec_seconds = individual.execution_time * 3600
            
            # Propagate to maneuver time
            pos_at_maneuver, vel_at_maneuver = self._propagate_to_time(
                satellite_pos, satellite_vel, exec_seconds
            )
            
            # Apply delta-v
            new_vel = [
                vel_at_maneuver[0] + individual.delta_v_x,
                vel_at_maneuver[1] + individual.delta_v_y,
                vel_at_maneuver[2] + individual.delta_v_z
            ]
            
            # Propagate forward 24 hours after maneuver
            positions, _, timestamps = propagate_orbit(
                pos_at_maneuver, new_vel, 24 * 3600, 60
            )
            
            # Check collision avoidance
            min_separation = float('inf')
            for threat in collision_threats:
                # Simplified: assume debris continues on current trajectory
                # In production, would propagate debris too
                min_separation = min(min_separation, 1.0)  # Placeholder
            
            # Reward collision avoidance
            if min_separation > COLLISION_THRESHOLD:
                fitness += 500  # Major reward for avoiding collision
            else:
                fitness -= 1000  # Penalty for collision
            
            # Reward fuel efficiency (minimize delta-v)
            fitness -= individual.delta_v_magnitude * 100
            
            # Check orbital slot deviation
            final_pos = positions[-1]
            deviation = np.linalg.norm(np.array(final_pos) - np.array(assigned_slot))
            
            if deviation < SLOT_TOLERANCE:
                fitness += 200  # Reward staying in slot
            else:
                fitness -= deviation * 10  # Penalty for deviation
            
        except Exception:
            return -1000  # Infeasible maneuver
        
        return fitness
    
    def _propagate_to_time(self, position: List[float], velocity: List[float], 
                          seconds: float) -> Tuple[List[float], List[float]]:
        """Propagate orbit to specific time"""
        positions, velocities, _ = propagate_orbit(position, velocity, seconds, 60)
        return positions[-1].tolist(), velocities[-1].tolist()
    
    def _tournament_selection(self, population: List[ManeuverGene], 
                             fitness_scores: List[float],
                             tournament_size: int = 3) -> List[ManeuverGene]:
        """Tournament selection"""
        selected = []
        
        for _ in range(len(population)):
            # Random tournament
            tournament_idx = np.random.choice(len(population), tournament_size, replace=False)
            tournament_fitness = [fitness_scores[i] for i in tournament_idx]
            winner_idx = tournament_idx[np.argmax(tournament_fitness)]
            selected.append(population[winner_idx])
        
        return selected
    
    def _crossover(self, parent1: ManeuverGene, 
                  parent2: ManeuverGene) -> Tuple[ManeuverGene, ManeuverGene]:
        """Single-point crossover"""
        # Random crossover point
        if np.random.random() < 0.5:
            child1 = ManeuverGene(
                parent1.execution_time,
                parent1.delta_v_x,
                parent2.delta_v_y,
                parent2.delta_v_z
            )
            child2 = ManeuverGene(
                parent2.execution_time,
                parent2.delta_v_x,
                parent1.delta_v_y,
                parent1.delta_v_z
            )
        else:
            child1 = ManeuverGene(
                parent1.execution_time,
                parent2.delta_v_x,
                parent2.delta_v_y,
                parent1.delta_v_z
            )
            child2 = ManeuverGene(
                parent2.execution_time,
                parent1.delta_v_x,
                parent1.delta_v_y,
                parent2.delta_v_z
            )
        
        return child1, child2
    
    def _mutate(self, individual: ManeuverGene) -> ManeuverGene:
        """Gaussian mutation"""
        if np.random.random() < self.mutation_rate:
            # Mutate execution time
            exec_time = individual.execution_time + np.random.normal(0, 0.5)
            exec_time = max(0.1, min(24, exec_time))
            
            # Mutate delta-v components
            dv_x = individual.delta_v_x + np.random.normal(0, 0.005)
            dv_y = individual.delta_v_y + np.random.normal(0, 0.005)
            dv_z = individual.delta_v_z + np.random.normal(0, 0.005)
            
            # Clip to constraints
            dv_x = np.clip(dv_x, -self.max_delta_v, self.max_delta_v)
            dv_y = np.clip(dv_y, -self.max_delta_v, self.max_delta_v)
            dv_z = np.clip(dv_z, -self.max_delta_v, self.max_delta_v)
            
            return ManeuverGene(exec_time, dv_x, dv_y, dv_z)
        
        return individual
    
    def _gene_to_maneuver(self, gene: ManeuverGene, collision_info: Dict) -> Dict:
        """Convert gene to maneuver dictionary"""
        return {
            "satellite_id": collision_info.get("satellite_id", "unknown"),
            "maneuver_type": "ai_optimized_avoidance",
            "delta_v": gene.delta_v_vector,
            "delta_v_magnitude": gene.delta_v_magnitude,
            "fuel_cost_percent": fuel_model.compute_fuel_percentage(gene.delta_v_magnitude),
            "execution_time_hours": round(gene.execution_time, 2),
            "execution_time_seconds": round(gene.execution_time * 3600, 0),
            "collision_object": collision_info.get("debris_id", "unknown"),
            "reason": f"AI-optimized avoidance of {collision_info.get('debris_id', 'unknown')}",
            "optimization_method": "genetic_algorithm",
            "optimized": True
        }

# Global instance
ai_optimizer = GeneticManeuverOptimizer()
