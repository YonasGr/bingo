"""
Bingo Card Generation Service
"""
import random
from typing import List, Dict, Any, Optional
from secrets import SystemRandom

# Use cryptographically secure random
secure_random = SystemRandom()


class CardGenerator:
    """Generate bingo cards for different variants"""
    
    @staticmethod
    def generate_75_ball_card() -> List[List[Dict[str, Any]]]:
        """
        Generate a 75-ball bingo card (5x5 grid)
        Columns: B(1-15), I(16-30), N(31-45), G(46-60), O(61-75)
        Center is FREE
        """
        card = []
        column_ranges = [
            (1, 15),   # B
            (16, 30),  # I
            (31, 45),  # N
            (46, 60),  # G
            (61, 75)   # O
        ]
        
        for row in range(5):
            card_row = []
            for col in range(5):
                # Center cell is FREE
                if row == 2 and col == 2:
                    card_row.append({
                        "value": None,
                        "marked": True,
                        "free": True
                    })
                else:
                    # Get available numbers for this column
                    min_val, max_val = column_ranges[col]
                    # Generate unique numbers for this column
                    value = secure_random.randint(min_val, max_val)
                    card_row.append({
                        "value": value,
                        "marked": False,
                        "free": False
                    })
            card.append(card_row)
        
        # Ensure no duplicate numbers in the card
        used_numbers = set()
        for row in range(5):
            for col in range(5):
                if card[row][col]["value"] is not None:
                    while card[row][col]["value"] in used_numbers:
                        min_val, max_val = column_ranges[col]
                        card[row][col]["value"] = secure_random.randint(min_val, max_val)
                    used_numbers.add(card[row][col]["value"])
        
        return card
    
    @staticmethod
    def generate_90_ball_card() -> List[List[Dict[str, Any]]]:
        """
        Generate a 90-ball bingo card (3 rows x 9 columns)
        Each row has 5 numbers and 4 blanks
        Numbers 1-90 distributed across columns
        """
        card = []
        
        # Column ranges for 90-ball: col0(1-9), col1(10-19), ..., col8(80-90)
        column_ranges = [
            (1, 9),
            (10, 19),
            (20, 29),
            (30, 39),
            (40, 49),
            (50, 59),
            (60, 69),
            (70, 79),
            (80, 90)
        ]
        
        # Generate 3 rows
        used_numbers = set()
        for row in range(3):
            # Randomly select 5 columns to have numbers
            columns_with_numbers = secure_random.sample(range(9), 5)
            columns_with_numbers.sort()
            
            card_row = []
            for col in range(9):
                if col in columns_with_numbers:
                    min_val, max_val = column_ranges[col]
                    value = secure_random.randint(min_val, max_val)
                    # Ensure uniqueness
                    while value in used_numbers:
                        value = secure_random.randint(min_val, max_val)
                    used_numbers.add(value)
                    
                    card_row.append({
                        "value": value,
                        "marked": False,
                        "free": False
                    })
                else:
                    card_row.append({
                        "value": None,
                        "marked": False,
                        "free": False
                    })
            card.append(card_row)
        
        return card
    
    @staticmethod
    def generate_card(variant: str = "75") -> List[List[Dict[str, Any]]]:
        """Generate card based on variant"""
        if variant == "90":
            return CardGenerator.generate_90_ball_card()
        else:
            return CardGenerator.generate_75_ball_card()


class DrawEngine:
    """Handle number drawing with RNG and audit trail"""
    
    @staticmethod
    def initialize_draw_pool(min_num: int, max_num: int, seed: Optional[str] = None) -> tuple[List[int], str]:
        """
        Initialize and shuffle draw pool
        Returns: (shuffled_pool, seed_used)
        """
        # Generate seed if not provided
        if seed is None:
            seed = str(secure_random.randint(10**15, 10**16 - 1))
        
        # Create pool of numbers
        pool = list(range(min_num, max_num + 1))
        
        # Shuffle using seed for reproducibility
        rng = random.Random(seed)
        rng.shuffle(pool)
        
        return pool, seed
    
    @staticmethod
    def draw_number(pool: List[int]) -> Optional[int]:
        """Draw next number from pool"""
        if pool:
            return pool.pop(0)
        return None


class PatternVerifier:
    """Verify bingo patterns"""
    
    # Common patterns for 75-ball
    PATTERNS_75 = {
        "horizontal_line": [
            [[1, 1, 1, 1, 1], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0]],  # Top
            [[0, 0, 0, 0, 0], [1, 1, 1, 1, 1], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0]],  # Second
            [[0, 0, 0, 0, 0], [0, 0, 0, 0, 0], [1, 1, 1, 1, 1], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0]],  # Middle
            [[0, 0, 0, 0, 0], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0], [1, 1, 1, 1, 1], [0, 0, 0, 0, 0]],  # Fourth
            [[0, 0, 0, 0, 0], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0], [1, 1, 1, 1, 1]],  # Bottom
        ],
        "vertical_line": [
            [[1, 0, 0, 0, 0], [1, 0, 0, 0, 0], [1, 0, 0, 0, 0], [1, 0, 0, 0, 0], [1, 0, 0, 0, 0]],  # Left
            [[0, 1, 0, 0, 0], [0, 1, 0, 0, 0], [0, 1, 0, 0, 0], [0, 1, 0, 0, 0], [0, 1, 0, 0, 0]],  # Second
            [[0, 0, 1, 0, 0], [0, 0, 1, 0, 0], [0, 0, 1, 0, 0], [0, 0, 1, 0, 0], [0, 0, 1, 0, 0]],  # Middle
            [[0, 0, 0, 1, 0], [0, 0, 0, 1, 0], [0, 0, 0, 1, 0], [0, 0, 0, 1, 0], [0, 0, 0, 1, 0]],  # Fourth
            [[0, 0, 0, 0, 1], [0, 0, 0, 0, 1], [0, 0, 0, 0, 1], [0, 0, 0, 0, 1], [0, 0, 0, 0, 1]],  # Right
        ],
        "diagonal": [
            [[1, 0, 0, 0, 0], [0, 1, 0, 0, 0], [0, 0, 1, 0, 0], [0, 0, 0, 1, 0], [0, 0, 0, 0, 1]],  # TL to BR
            [[0, 0, 0, 0, 1], [0, 0, 0, 1, 0], [0, 0, 1, 0, 0], [0, 1, 0, 0, 0], [1, 0, 0, 0, 0]],  # TR to BL
        ],
        "four_corners": [
            [[1, 0, 0, 0, 1], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0], [1, 0, 0, 0, 1]]
        ],
        "full_house": [
            [[1, 1, 1, 1, 1], [1, 1, 1, 1, 1], [1, 1, 1, 1, 1], [1, 1, 1, 1, 1], [1, 1, 1, 1, 1]]
        ]
    }
    
    # Patterns for 90-ball
    PATTERNS_90 = {
        "one_line": "any_row",  # Any complete row
        "two_lines": "any_two_rows",  # Any two complete rows
        "full_house": "all_numbers"  # All numbers
    }
    
    @staticmethod
    def verify_pattern(card: List[List[Dict[str, Any]]], pattern_name: str, variant: str = "75") -> bool:
        """Verify if card matches the pattern"""
        if variant == "75":
            return PatternVerifier._verify_75_ball_pattern(card, pattern_name)
        else:
            return PatternVerifier._verify_90_ball_pattern(card, pattern_name)
    
    @staticmethod
    def _verify_75_ball_pattern(card: List[List[Dict[str, Any]]], pattern_name: str) -> bool:
        """Verify 75-ball pattern"""
        if pattern_name not in PatternVerifier.PATTERNS_75:
            return False
        
        patterns = PatternVerifier.PATTERNS_75[pattern_name]
        
        # Create marked mask from card
        marked_mask = [[1 if cell["marked"] else 0 for cell in row] for row in card]
        
        # Check if any pattern matches
        for pattern in patterns:
            match = True
            for row in range(5):
                for col in range(5):
                    if pattern[row][col] == 1 and marked_mask[row][col] != 1:
                        match = False
                        break
                if not match:
                    break
            if match:
                return True
        
        return False
    
    @staticmethod
    def _verify_90_ball_pattern(card: List[List[Dict[str, Any]]], pattern_name: str) -> bool:
        """Verify 90-ball pattern"""
        if pattern_name == "one_line":
            # Check if any row is complete
            for row in card:
                if all(cell["marked"] for cell in row if cell["value"] is not None):
                    return True
            return False
        
        elif pattern_name == "two_lines":
            # Check if any two rows are complete
            complete_rows = 0
            for row in card:
                if all(cell["marked"] for cell in row if cell["value"] is not None):
                    complete_rows += 1
            return complete_rows >= 2
        
        elif pattern_name == "full_house":
            # Check if all numbers are marked
            for row in card:
                for cell in row:
                    if cell["value"] is not None and not cell["marked"]:
                        return False
            return True
        
        return False
    
    @staticmethod
    def verify_claim(card: List[List[Dict[str, Any]]], called_numbers: List[int], pattern_name: str, variant: str = "75") -> tuple[bool, str]:
        """
        Verify a bingo claim
        Returns: (is_valid, message)
        """
        # First check all marked numbers were actually called
        for row in card:
            for cell in row:
                if cell["marked"] and not cell.get("free", False):
                    if cell["value"] not in called_numbers:
                        return False, f"Number {cell['value']} was marked but not called"
        
        # Then check if pattern is satisfied
        if PatternVerifier.verify_pattern(card, pattern_name, variant):
            return True, "Valid bingo!"
        else:
            return False, f"Pattern '{pattern_name}' not satisfied"
