#storing information about current state
#determines vaid moves at current state
#move logs

import re
from shutil import move


class Gamestate():
    def __init__ (self):
        #borad is 8x8 2d list, and each element of list is represented by 2 characters
        #1st character represents the color of the chess piece
        #2nd character represents the piece
        #"--" represents an empty space with no piece
        self.board = [
            ["bR","bN","bB","bQ","bK","bB","bN","bR"] ,
            ["bp","bp","bp","bp","bp","bp","bp","bp"] ,
            ["--","--","--","--","--","--","--","--"] ,
            ["--","--","--","--","--","--","--","--"] ,
            ["--","--","--","--","--","--","--","--"] ,
            ["--","--","--","--","--","--","--","--"] ,
            ["wp","wp","wp","wp","wp","wp","wp","wp"] ,
            ["wR","wN","wB","wQ","wK","wB","wN","wR"] 
        ]
        self.moveFunctions = { 'p':self.getPawnMoves, 'R':self.getRookMoves, 'N':self.getKnightMoves, 'B':self.getBishopMoves, 
                               'Q':self.getQueenMoves, 'K':self.getKingMoves }
        self.whiteToMove = True
        self.moveLog = []
        self.whiteKingLocation = (7,4)
        self.blackKingLocation = (0,4)
        self.checkMate = False
        self.staleMate = False

#takes a move as a parameter and executes it(doesn't work for castling, pawn promotion and en-passant)  
    def makeMove(self,move) :
        self.board[move.startRow][move.startCol] = "--"
        self.board[move.endRow][move.endCol] = move.pieceMoved
        self.moveLog.append(move)                                #undo move and to display history of the game
        self.whiteToMove = not self.whiteToMove                  # swap turns of players
        #update King's Location
        if move.pieceMoved == "wK" :
            self.whiteKingLocation = (move.endRow, move.endCol)
        elif move.pieceMoved == "bK" :
            self.blackKingLocation = (move.endRow, move.endCol)



    def undoMove(self):
        if len(self.moveLog) != 0:  #movelog is not zero
            move = self.moveLog.pop()
            self.board[move.startRow][move.startCol] = move.pieceMoved
            self.board[move.endRow][move.endCol] = move.pieceCaptured
            self.whiteToMove = not self.whiteToMove
            #update King's Position
            if move.pieceMoved == "wK" :
                self.whiteKingLocation = (move.startRow, move.startCol)
            elif move.pieceMoved == "bK" :
                self.blackKingLocation = (move.startRow, move.startCol)


    #All moves considering checks
    def getValidMoves(self):
        #1   Generate All possible moves
        moves = self.getAllPossibleMoves ()
        #2   for each move, make the move
        for i in range(len(moves)-1, -1, -1): #when running from a list go backwards through that list
            self.makeMove(moves[i])
            #3   Generate all opponent's moves      
            #4   for each of opponent's moves, check if they attack your King
            self.whiteToMove = not self.whiteToMove
            if self.inCheck():
                moves.remove(moves[i])             #5   if they attack your king, it is not a valid move
            self.whiteToMove = not self.whiteToMove
            self.undoMove()
        if len(moves)==0 :  #either checkmate or stalemate
            if self.inCheck() : 
                self.checkMate = True
            else : 
                self.staleMate = True
        else : 
            self.checkMate = False
            self.staleMate = False

        return moves 

# Check if the current player is in Check
    def inCheck(self):
        if self.whiteToMove:
            return self.squareUnderAttack(self.whiteKingLocation[0],self.whiteKingLocation[1])
        else:
            return self.squareUnderAttack(self.blackKingLocation[0],self.blackKingLocation[1])


#  Determine in enemy can attack square r,c
    def squareUnderAttack(self,r,c):
        self.whiteToMove = not self.whiteToMove
        oppMoves = self.getAllPossibleMoves()
        self.whiteToMove = not self.whiteToMove
        for move in oppMoves :
            if move.endRow == r and move.endCol == c :
                return True
        return False


    # All moves without considering checks
    def getAllPossibleMoves(self):
        moves = []
        for r in range (len(self.board)):
            for c in range (len(self.board[r])):
                turn = self.board[r][c][0]
                if (turn=='w'and self.whiteToMove) or (turn=='b' and not self.whiteToMove):
                    piece = self.board[r][c][1]
                    self.moveFunctions[piece](r,c,moves)
        return moves


    def getPawnMoves(self,r,c,moves):
        if self.whiteToMove:                                                            #white pawn moves
            if self.board[r-1][c] == "--" :
                moves.append(Move((r,c),(r-1,c), self.board))
                if r==6 and self.board[r-2][c] == "--":
                    moves.append(Move((r,c),(r-2,c),self.board))
            if c-1 >= 0:
                if self.board[r-1][c-1][0] == "b":
                    moves.append(Move((r,c),(r-1,c-1),self.board))
            if c+1 <= 7:
                if self.board[r-1][c+1][0] == "b":
                    moves.append(Move((r,c),(r-1,c+1),self.board))
        else:                                                                              #black pawn moves
            if self.board[r+1][c] == "--":
                moves.append(Move((r,c),(r+1,c), self.board))
                if r==1 and self.board[r+2][c] == "--":
                    moves.append(Move((r,c),(r+2,c),self.board))
            if c-1 >= 0:
                if self.board[r+1][c-1][0] == "w":
                    moves.append(Move((r,c),(r+1,c-1),self.board))
            if c+1 <= 7:
                if self.board[r+1][c+1][0] == "w":
                    moves.append(Move((r,c),(r+1,c+1),self.board))
            

    def getRookMoves(self,r,c,moves):
        directions = ((-1,0), (0,-1), (1,0), (0,1))         #up,left,down,right
        enemycolor = "b" if self.whiteToMove  else "w"
        for d in directions:
            for i in range(1,8):
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                if 0<= endRow <8 and 0<= endCol <8:
                    endPiece = self.board[endRow][endCol]
                    if endPiece == "--":
                        moves.append(Move((r,c),(endRow,endCol),self.board))
                    elif endPiece[0] == enemycolor: 
                        moves.append(Move((r,c),(endRow,endCol),self.board))
                        break
                    else:                                 #friendly piece invalid
                        break
                else:                                     #off board
                    break


    def getKnightMoves(self,r,c,moves):
        knightMoves = ((-2,-1),(2,-1),(-2,1),(2,1),(-1,-2),(-1,2),(1,-2),(1,2))
        allycolor= "w" if self.whiteToMove else "b"
        for n in knightMoves:
            endRow = r + n[0]
            endCol = c + n[1]
            if 0<= endRow < 8 and 0<=endCol < 8:
                endPiece = self.board[endRow][endCol]
                if endPiece [0] != allycolor :
                    moves.append(Move((r,c),(endRow,endCol),self.board))


    def getBishopMoves(self,r,c,moves):
        directions = ((-1,-1),(-1,1),(1,-1),(1,1))
        enemycolor = "b" if self.whiteToMove  else "w"
        for d in directions:
            for i in range (1,8):
                endRow = r + d[0] *i
                endCol = c + d[1] *i
                if 0<= endRow <8 and 0<= endCol <8:
                    endPiece = self.board[endRow][endCol]
                    if endPiece == "--":
                        moves.append(Move((r,c),(endRow,endCol),self.board)) 
                    elif endPiece[0] == enemycolor: 
                        moves.append(Move((r,c),(endRow,endCol),self.board))
                        break
                    else:                                 #friendly piece invalid
                        break
                else:                                     #off board
                    break


    def getQueenMoves(self,r,c,moves):
        self.getRookMoves(r,c,moves)
        self.getBishopMoves(r,c,moves)
        

    def getKingMoves(self,r,c,moves):
        kingMoves = ((-1,-1),(-1,0),(-1,1),(1,-1),(1,0),(1,1),(0,-1),(0,1) )
        allycolor= "w" if self.whiteToMove else "b"
        for i in range(8):
            endRow = r + kingMoves[i][0]
            endCol = c + kingMoves[i][1]
            if 0<= endRow < 8 and 0<=endCol < 8:
                endPiece = self.board[endRow][endCol]
                if endPiece [0] != allycolor :
                     moves.append(Move((r,c),(endRow,endCol),self.board))



class Move():
    #maps keys to values
    #key : value
    rankstoRows = {"1":7, "2":6, "3":5,"4":4,
                   "5":3, "6":2, "7":1, "8":0 }
    rowstoRanks = { v: k for k, v in rankstoRows.items()}
    filestoCols = {"a":0, "b":1, "c":2,"d":3,
                   "e":4, "f":5, "g":6, "h":7 } 
    colstoFiles = { v: k for k, v in filestoCols.items()}

    def __init__(self, startSq, endSq, board) :
        self.startRow = startSq[0]
        self.startCol = startSq [1]
        self.endRow = endSq [0]
        self.endCol = endSq[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]
        self.moveID = self.startRow*1000 + self.startCol*100 + self.endRow*10 + self.endCol

    #overriding the equals
    def __eq__(self, other):
        if isinstance(other, Move):
            return self.moveID == other.moveID
        return False

        
    
    def getChessNotation(self):
        #you can add to make these like real chess notations
        return self.getRanksFiles(self.startRow, self.startCol) + self.getRanksFiles(self.endRow,self.endCol)
    

    def getRanksFiles(self,r,c):
        return self.colstoFiles[c] + self.rowstoRanks[r]
