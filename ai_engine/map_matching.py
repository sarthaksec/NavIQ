import numpy as np

class MapMatchingHMM:
    """
    Simulates a Hidden Markov Model (HMM) for Map-Matching.
    Given a sequence of noisy GPS or UKF-predicted coordinates, this algorithm 
    snaps the trajectory to the most probable road segments.
    """
    def __init__(self, search_radius=50.0):
        self.search_radius = search_radius
        # Simulated road network (a simple grid for demonstration)
        # In production, this would be an OpenStreetMap (OSM) spatial index
        self.road_nodes = self._generate_dummy_grid()

    def _generate_dummy_grid(self):
        """ Generates a dummy road network grid. """
        nodes = []
        for x in range(-500, 500, 50):
            for y in range(-500, 500, 50):
                nodes.append((x, y))
        return np.array(nodes)

    def emission_probability(self, point, node, sigma=10.0):
        """
        Probability of observing the 'point' given we are actually on 'node'.
        Using a Gaussian distribution based on distance.
        """
        dist = np.linalg.norm(np.array(point) - np.array(node))
        return (1.0 / (np.sqrt(2 * np.pi) * sigma)) * np.exp(-0.5 * (dist / sigma)**2)

    def transition_probability(self, node_a, node_b, dist_traveled):
        """
        Probability of moving from node_a to node_b given the distance traveled.
        Penalizes teleportation across the map.
        """
        network_dist = np.linalg.norm(np.array(node_a) - np.array(node_b))
        beta = 5.0
        dist_diff = abs(network_dist - dist_traveled)
        return (1.0 / beta) * np.exp(-dist_diff / beta)

    def snap_to_road(self, trajectory):
        """
        Viterbi algorithm to find the most likely sequence of road nodes.
        trajectory: List of (x, y) coordinates representing the vehicle path.
        """
        if not trajectory:
            return []

        # List of dicts mapping road node index -> (probability, previous_node_idx)
        viterbi = []
        
        # Step 1: Initialize
        start_point = trajectory[0]
        initial_probs = {}
        for i, node in enumerate(self.road_nodes):
            if np.linalg.norm(start_point - node) <= self.search_radius:
                # Uniform initial transition prob, weighted by emission
                prob = self.emission_probability(start_point, node)
                initial_probs[i] = (prob, None)
        viterbi.append(initial_probs)

        # Step 2: Forward pass
        for t in range(1, len(trajectory)):
            point = trajectory[t]
            prev_point = trajectory[t-1]
            dist_traveled = np.linalg.norm(np.array(point) - np.array(prev_point))
            
            current_probs = {}
            for i, current_node in enumerate(self.road_nodes):
                # Optimization: Only consider nodes near the observation
                if np.linalg.norm(np.array(point) - current_node) > self.search_radius:
                    continue
                    
                max_prob = -1.0
                best_prev = None
                
                # Compare against all valid previous nodes
                for j, (prev_prob, _) in viterbi[t-1].items():
                    prev_node = self.road_nodes[j]
                    
                    trans_p = self.transition_probability(prev_node, current_node, dist_traveled)
                    emiss_p = self.emission_probability(point, current_node)
                    
                    prob = prev_prob * trans_p * emiss_p
                    if prob > max_prob:
                        max_prob = prob
                        best_prev = j
                
                if best_prev is not None:
                    current_probs[i] = (max_prob, best_prev)
            
            viterbi.append(current_probs)

        # Step 3: Backtrack to find the best path
        snapped_path = []
        if not viterbi[-1]:
            print("Map matching failed (trajectory too far from roads).")
            return snapped_path

        # Find the node with the highest probability at the final step
        best_last_node = max(viterbi[-1].items(), key=lambda x: x[1][0])[0]
        
        current_node = best_last_node
        for t in range(len(trajectory) - 1, -1, -1):
            snapped_path.insert(0, self.road_nodes[current_node].tolist())
            current_node = viterbi[t][current_node][1]
            
        return snapped_path

if __name__ == "__main__":
    hmm = MapMatchingHMM()
    # A drifting trajectory passing near the grid nodes (0,0), (0,50), (0,100)
    noisy_trajectory = [
        (2.1, -1.5),
        (5.5, 48.0),
        (-3.0, 102.5)
    ]
    
    print("Noisy Trajectory:")
    for pt in noisy_trajectory: print(f"  {pt}")
        
    snapped = hmm.snap_to_road(noisy_trajectory)
    
    print("\nSnapped Trajectory (Map-Matched):")
    for pt in snapped: print(f"  {pt}")
