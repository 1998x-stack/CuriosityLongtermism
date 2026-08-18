"""
Industrial-Strength Grid Manager for Tent Placement Game
Implements advanced backtracking with constraint propagation and defensive programming
"""

import random
from collections import deque
from typing import List, Set, Tuple, Dict
from loguru import logger
from config import GRID_SIZE, TREE_COUNT

class DynamicGridGenerator:
    """Advanced grid generation system with:
    - Iterative backtracking
    - Dynamic requirement calculation
    - Defensive programming
    - Comprehensive validation
    """

    def __init__(self):
        """Initialize a new puzzle grid"""
        self.trees: List[Tuple[int, int]] = []
        self.tents: Set[Tuple[int, int]] = set()
        self.row_requirements: List[int] = []
        self.col_requirements: List[int] = []
        
        self._generate_valid_layout()
        logger.success(f"Generated new grid with {len(self.trees)} trees")

    def _generate_valid_layout(self) -> None:
        """Orchestrate the complete generation process"""
        max_attempts = 3
        for attempt in range(max_attempts):
            try:
                self.trees = []
                self.tents = set()
                self._place_trees()
                self._calculate_requirements()
                self._place_tents()
                
                if self.validated:
                    return
                
                logger.warning(f"Attempt {attempt + 1}: Generated invalid layout")
            except Exception as e:
                logger.error(f"Generation error: {str(e)}")
        
        raise RuntimeError("Failed to generate valid grid after multiple attempts")

    def _place_trees(self) -> None:
        """Generate non-adjacent tree positions"""
        candidates = [(i, j) for i in range(GRID_SIZE) for j in range(GRID_SIZE)]
        random.shuffle(candidates)
        
        for coord in candidates:
            if self._is_valid_tree_position(coord):
                self.trees.append(coord)
                if len(self.trees) == TREE_COUNT:
                    break

    def _is_valid_tree_position(self, coord: Tuple[int, int]) -> bool:
        """Check 8-directional adjacency"""
        x, y = coord
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if 0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE:
                    if (nx, ny) in self.trees:
                        return False
        return True

    def _calculate_requirements(self) -> None:
        """Dynamically calculate row/column requirements"""
        # Initialize with minimum requirements
        self.row_requirements = [1] * GRID_SIZE
        self.col_requirements = [1] * GRID_SIZE
        
        # Adjust to match tree count
        total = GRID_SIZE
        while total != len(self.trees):
            if total < len(self.trees):
                # Increase requirements
                row = random.randint(0, GRID_SIZE - 1)
                self.row_requirements[row] += 1
                total += 1
            else:
                # Decrease requirements
                row = random.randint(0, GRID_SIZE - 1)
                if self.row_requirements[row] > 1:
                    self.row_requirements[row] -= 1
                    total -= 1

    def _place_tents(self) -> None:
        """Iterative backtracking tent placement"""
        candidates = self._generate_candidates()
        solution_stack = deque()
        current_pos = 0
        backtracking = False

        while current_pos < len(candidates):
            if backtracking:
                if not solution_stack:
                    logger.warning("No valid solution found")
                    return
                
                last_pos, last_coord = solution_stack.pop()
                self.tents.remove(last_coord)
                current_pos = last_pos + 1
                backtracking = False
                continue

            current_coord = candidates[current_pos]
            
            if self._is_valid_tent_position(current_coord):
                self.tents.add(current_coord)
                solution_stack.append((current_pos, current_coord))
                current_pos += 1

                # Early pruning
                if self._violates_constraints():
                    self.tents.remove(current_coord)
                    solution_stack.pop()
                    backtracking = True
            else:
                current_pos += 1

    def _generate_candidates(self) -> List[Tuple[int, int]]:
        """Generate and prioritize candidate positions"""
        # Group by column
        col_groups: Dict[int, List[Tuple[int, int]]] = {
            col: [] for col in range(GRID_SIZE)
        }
        
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                coord = (row, col)
                if coord not in self.trees and self._has_adjacent_tree(coord):
                    col_groups[col].append(coord)
        
        # Sort within columns by row requirements
        for col in col_groups:
            col_groups[col].sort(
                key=lambda c: (
                    self.row_requirements[c[0]] - self._count_tents_in_row(c[0]),
                    random.random()
                )
            )
        
        # Sort columns by remaining requirements
        sorted_cols = sorted(
            range(GRID_SIZE),
            key=lambda c: self.col_requirements[c] - self._count_tents_in_col(c),
            reverse=True
        )
        
        # Flatten into final candidate list
        return [
            coord
            for col in sorted_cols
            for coord in col_groups[col]
        ]

    def _is_valid_tent_position(self, coord: Tuple[int, int]) -> bool:
        """Check tent placement validity"""
        # Adjacency check (8-directional)
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = coord[0] + dx, coord[1] + dy
                if (nx, ny) in self.tents:
                    return False
        return self._has_adjacent_tree(coord)

    def _has_adjacent_tree(self, coord: Tuple[int, int]) -> bool:
        """Check 4-directional tree adjacency"""
        x, y = coord
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        return any(
            (x + dx, y + dy) in self.trees
            for dx, dy in directions
            if 0 <= x + dx < GRID_SIZE and 0 <= y + dy < GRID_SIZE
        )

    def _count_tents_in_row(self, row: int) -> int:
        """Count placed tents in a row"""
        return sum(1 for r, _ in self.tents if r == row)

    def _count_tents_in_col(self, col: int) -> int:
        """Count placed tents in a column"""
        return sum(1 for _, c in self.tents if c == col)

    def _violates_constraints(self) -> bool:
        """Check for constraint violations"""
        # Check row constraints
        for row in range(GRID_SIZE):
            if self._count_tents_in_row(row) > self.row_requirements[row]:
                return True
        
        # Check column constraints
        for col in range(GRID_SIZE):
            if self._count_tents_in_col(col) > self.col_requirements[col]:
                return True
        
        return False

    @property
    def validated(self) -> bool:
        """Comprehensive solution validation"""
        try:
            # Verify counts
            assert len(self.trees) == TREE_COUNT, "Incorrect tree count"
            assert len(self.tents) == sum(self.row_requirements), "Tent count mismatch"
            
            # Verify requirements
            for row in range(GRID_SIZE):
                assert self._count_tents_in_row(row) == self.row_requirements[row], \
                    f"Row {row} requirement not met"
            
            for col in range(GRID_SIZE):
                assert self._count_tents_in_col(col) == self.col_requirements[col], \
                    f"Column {col} requirement not met"
            
            # Verify adjacency rules
            for tent in self.tents:
                assert self._has_adjacent_tree(tent), f"Tent {tent} not near tree"
                for dx in (-1, 0, 1):
                    for dy in (-1, 0, 1):
                        if dx == 0 and dy == 0:
                            continue
                        nx, ny = tent[0] + dx, tent[1] + dy
                        assert (nx, ny) not in self.tents, f"Adjacent tents at {tent}"
            
            return True
        except AssertionError as e:
            logger.error(f"Validation failed: {str(e)}")
            return False

# Test harness
if __name__ == "__main__":
    logger.add("grid_generator.log", rotation="1 MB")
    
    try:
        for i in range(10):
            grid = DynamicGridGenerator()
            assert grid.validated, f"Test {i} failed validation"
            logger.success(f"Test {i} passed")
    except Exception as e:
        logger.critical(f"Test failed: {str(e)}")
        raise