import itertools
import random


class Minesweeper():
    """
    Minesweeper game representation
    """

    def __init__(self, height=8, width=8, mines=8):

        # Set initial width, height, and number of mines
        self.height = height
        self.width = width
        self.mines = set()

        # Initialize an empty field with no mines
        self.board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(False)
            self.board.append(row)

        # Add mines randomly
        while len(self.mines) != mines:
            i = random.randrange(height)
            j = random.randrange(width)
            if not self.board[i][j]:
                self.mines.add((i, j))
                self.board[i][j] = True

        # At first, player has found no mines
        self.mines_found = set()

    def print(self):
        """
        Prints a text-based representation
        of where mines are located.
        """
        for i in range(self.height):
            print("--" * self.width + "-")
            for j in range(self.width):
                if self.board[i][j]:
                    print("|X", end="")
                else:
                    print("| ", end="")
            print("|")
        print("--" * self.width + "-")

    def is_mine(self, cell):
        i, j = cell
        return self.board[i][j]

    def nearby_mines(self, cell):
        """
        Returns the number of mines that are
        within one row and column of a given cell,
        not including the cell itself.
        """

        # Keep count of nearby mines
        count = 0

        # Loop over all cells within one row and column
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # Ignore the cell itself
                if (i, j) == cell:
                    continue

                # Update count if cell in bounds and is mine
                if 0 <= i < self.height and 0 <= j < self.width:
                    if self.board[i][j]:
                        count += 1

        return count

    def won(self):
        """
        Checks if all mines have been flagged.
        """
        return self.mines_found == self.mines


class Sentence():
    """
    Logical statement about a Minesweeper game
    A sentence consists of a set of board cells,
    and a count of the number of those cells which are mines.
    """

    def __init__(self, cells, count):
        self.cells = set(cells)
        self.count = count

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def number_cells(self, sentence):
        x = 0
        for cell in sentence:
            x += 1

        return x

    def known_mines(self):
        """
        Returns the set of all cells in self.cells known to be mines.
        """
        result = set()
        for cell in self.cells:
            if cell in MinesweeperAI.mines:
                result.add(cell)

        for sentence in MinesweeperAI.knowledge:
            if self.number_cells(sentence.cells) == sentence.count:
                for cell in sentence:
                    result.add(cell)

        return result

    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """
        result = set()
        for cell in self.cells:
            if cell in MinesweeperAI.safes:
                result.add(cell)

        for sentence in MinesweeperAI.knowledge:
            if sentence.count == 0:
                for cell in sentence:
                    result.add(cell)
        return result

    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """

        # knowledge is a list of sentence object

        if cell in self.cells:
            self.cells -= {cell}
            self.count -= 1

    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """
        if cell in self.cells:
            self.cells -= {cell}


class MinesweeperAI():
    """
    Minesweeper game player
    """

    def __init__(self, height=8, width=8):

        # Set initial height and width
        self.height = height
        self.width = width

        # Keep track of which cells have been clicked on
        self.moves_made = set()

        # Keep track of cells known to be safe or mines
        self.mines = set()
        self.safes = set()

        # List of sentences about the game known to be true
        self.knowledge = []

    def mark_mine(self, cell):
        """
        Marks a cell as a mine, and updates all knowledge
        to mark that cell as a mine as well.
        """
        self.mines.add(cell)
        for sentence in self.knowledge:
            sentence.mark_mine(cell)

    def mark_safe(self, cell):
        """
        Marks a cell as safe, and updates all knowledge
        to mark that cell as safe as well.
        """
        self.safes.add(cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)

    def get_neighbor_cells(self, cell):
        # cell -> (i, j)  i -> 0~h-1 ,, j -> 0~w-1
        neighbors = set()
        neighbors.add((cell[0] - 1, cell[1]))  # upper cell
        neighbors.add((cell[0] + 1, cell[1]))  # lower cell
        neighbors.add((cell[0], cell[1] - 1))  # left
        neighbors.add((cell[0], cell[1] + 1))  # right
        neighbors.add((cell[0] - 1, cell[1] - 1))  # upper left
        neighbors.add((cell[0] - 1, cell[1] + 1))  # upper right
        neighbors.add((cell[0] + 1, cell[1] - 1))  # lower left
        neighbors.add((cell[0] + 1, cell[1] + 1))  # lower right

        res = set()
        for cell in neighbors:
            if cell[0] >= 0 and cell[1] >= 0 and cell[0] != 8 and cell[1] != 8:
                if cell not in self.safes and cell not in self.moves_made:
                    res.add(cell)
        
        return res
    
    # this function adjust the knowledge by removing the known cells 
    def knowledge_check(self, knowledge):
        
        print('inside knowledge check')
        for sentence in knowledge:
            if len(sentence.cells) == 0:
                knowledge.remove(sentence)
                
        for sentence in knowledge:
            if sentence.count == 0:
                for cell in sentence.cells:
                    self.safes.add(cell)          
                    
            elif sentence.count == len(sentence.cells):
                for cell in sentence.cells:
                    self.mines.add(cell)                  

        for cell in self.safes:
            self.mark_safe(cell)
            
        for cell in self.mines:
            self.mark_mine(cell)

    def add_knowledge(self, cell, count):
        """
        Called when the Minesweeper board tells us, for a given
        safe cell, how many neighboring cells have mines in them.
        This function should:
            1) mark the cell as a move that has been made
            2) mark the cell as safe
            3) add a new sentence to the AI's knowledge base
               based on the value of `cell` and `count`
            4) mark any additional cells as safe or as mines
               if it can be concluded based on the AI's knowledge base
            5) add any new sentences to the AI's knowledge base
               if they can be inferred from existing knowledge
        """
        self.moves_made.add(cell)
        self.mark_safe(cell)
        
        sentence = Sentence(self.get_neighbor_cells(cell), count)
        
        for obj in self.knowledge:
            if obj.cells & sentence.cells == sentence.cells:
                self.knowledge.append(Sentence(obj.cells - sentence.cells, obj.count - sentence.count))
                break
                
        self.knowledge.append(sentence)
        self.knowledge_check(self.knowledge)
        
    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.
        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """
        for cell in self.safes:
            if cell not in self.moves_made:
                return cell

        return None
    # if there isn't a safe mode(like when the game is starting)

    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """

        for i in range(8):
            for j in range(8):
                if (i, j) not in self.moves_made and (i, j) not in self.mines:
                    return i, j

        return None
