#Driver File
#control user input
#Display current game state object

from calendar import c
from re import S
from shutil import move
from turtle import Screen
import pygame as p
p.font.init()
font = p.font.SysFont(None, 48)

import chessengine 

WIDTH = HEIGHT = 512
DIMENSION = 8
SQ_SIZE = WIDTH // DIMENSION
MAX_FPS= 15 
IMAGES = {}

#global dictionary for images so we don't have to call them again and again
def loadImages():
    pieces = ['wp','bp','wR','bR','wN','bN','wB','bB','wQ','bQ','wK','bK']
    for piece in pieces :
        IMAGES[piece]= p.transform.scale(p.image.load("images/" + piece + ".png"), (SQ_SIZE,SQ_SIZE))

#Main Driver
#Handles user input and updates graphics
def main():
    p.init
    screen = p.display.set_mode((WIDTH,HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    gs = chessengine.Gamestate()
    validMoves = gs.getValidMoves()
    movemade = False           #flag variable when a move is made
    animate = False            #flag variable for when should we animate our move
    loadImages()               #only done once before the while loop
    running = True
    sqSelected = ()            #tuple keeping track of last click of user
    playerClicks = []          #keep track of player clicks
    gameOver = False
    while running :
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            #Mouse Handler
            elif e.type == p.MOUSEBUTTONDOWN:
                if not gameOver :
                    location = p.mouse.get_pos()
                    col = location[0]//SQ_SIZE
                    row = location[1]//SQ_SIZE
                    if sqSelected == (row,col) :
                        sqSelected = ()
                        playerClicks = []
                    else:
                        sqSelected = (row,col)
                        playerClicks.append(sqSelected)
                    if len(playerClicks) == 2 :
                        move=chessengine.Move(playerClicks[0], playerClicks[1], gs.board)
                        print (move.getChessNotation())
                        if move in validMoves:
                            gs.makeMove(move)
                            movemade = True
                            animate = True
                            sqSelected = ()
                            playerClicks = []
                        else:
                            playerClicks = [sqSelected]
            #key handler
            elif e.type == p.KEYDOWN:
                if e.key == p.K_z :
                    gs.undoMove()
                    movemade = True
                    animate = False
                if e.key == p.K_r :
                    gs = chessengine.Gamestate()
                    validMoves = gs.getValidMoves()
                    sqSelected = ()
                    playerClicks = []
                    movemade = False
                    animate = False
            
        if movemade :
            if animate :
                animateMove(gs.moveLog[-1] , screen , gs.board, clock)
            validMoves = gs.getValidMoves()
            movemade = False
            animate = False

        
        drawGameState( screen, gs, validMoves, sqSelected)
        
        if gs.checkMate :
            gameOver = True
            if gs.whiteToMove :
                drawText (screen, 'Black Wins by Checkmate')
            else:
                drawText (screen, 'White Wins by Checkmate')
        elif gs.staleMate :
            gameOver = True
            drawText (screen, 'Stalemate')
            
        
        clock.tick(MAX_FPS) 
        p.display.flip()

 #Highlight square selected and moves for piece selected
def highlightSquares(screen, gs, validMoves, sqSelected)   :
    if sqSelected != ():
        r,c = sqSelected
        if gs.board[r][c][0] == ('w' if gs.whiteToMove else 'b') :    #sqSelected is a piece that can be moved
            #highlight selected square
            s = p.Surface((SQ_SIZE,SQ_SIZE))
            s.set_alpha(100) #transparency value 0- transparent; 255 opaque
            s.fill(p.Color('gold'))
            screen.blit (s, (c*SQ_SIZE, r*SQ_SIZE))
            #highlight moves from that square
            s.fill(p.Color('green'))
            for move in validMoves :
                if move.startRow == r and move.startCol == c:
                    screen.blit(s, (move.endCol*SQ_SIZE , move.endRow*SQ_SIZE ))
             


#Responsible for all the graphics in current game state
def drawGameState(screen,gs, validMoves, sqSelected) :
    drawBoard(screen)
    highlightSquares(screen, gs , validMoves, sqSelected )#can be used to add other such things like piece highlighting or move suggestions
    drawPieces(screen, gs.board)

#Draw squares on the board
def drawBoard (screen) :
    global colors
    colors = [p.Color(128,160,180) , p.Color(201,217,225)]
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[( (r+c)%2 )]
            p.draw.rect(screen, color, p.Rect (c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))
            

#Draw pieces on the boarrd using current game state
def drawPieces (screen, board) :
    for r in range (DIMENSION):
        for c in range (DIMENSION):
            piece = board[r][c]
            if piece != "--":
                screen.blit(IMAGES[piece], p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))

# Animating a move
def animateMove(move,screen,board,clock):
    global colors
    dR = move.endRow - move.startRow
    dC = move.endCol - move.startCol
    framesPerSquare = 10          #frames to move one square piece
    frameCount = (abs(dR) + abs(dC)) * framesPerSquare
    for frame in range(frameCount+1) :
        r,c = (move.startRow+ dR*frame/frameCount , move.startCol + dC*frame/frameCount)
        drawBoard(screen)
        drawPieces(screen, board)
        #erase the piece moved from it's ending square
        color = colors[ (move.endRow + move.endCol) % 2 ]
        endSquare = p.Rect (move.endCol*SQ_SIZE , move.endRow*SQ_SIZE , SQ_SIZE, SQ_SIZE)
        p.draw.rect(screen,color,endSquare)
        #draw captured piece onto rectangle
        if move.pieceCaptured != '--':
            screen.blit(IMAGES[move.pieceCaptured], endSquare)
        #draw moving piece
        screen.blit(IMAGES[move.pieceMoved], p.Rect(c*SQ_SIZE,r*SQ_SIZE, SQ_SIZE, SQ_SIZE))
        p.display.flip()
        clock.tick(60)

def drawText(screen, text) :
    font = p.font.SysFont("Arial", 32 , True, False)
    textObject = font.render(text, 0, p.Color('grey'))
    textLocation = p.Rect(0,0,WIDTH,HEIGHT).move(WIDTH/2 - textObject.get_width()/2, HEIGHT/2 - textObject.get_height()/2)
    screen.blit(textObject,textLocation)
    textObject = font.render(text, 0, p.Color('grey7'))
    screen.blit(textObject , textLocation.move(2,2))
               

if __name__ == "__main__":
    main()