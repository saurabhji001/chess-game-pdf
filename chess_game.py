import chess
import chess.svg
from fpdf import FPDF
from io import BytesIO
import cairosvg
from datetime import datetime

def create_chess_pdf():
    """
    Creates an interactive chess game PDF with board visualization.
    """
    
    # Initialize chess board
    board = chess.Board()
    
    # Create PDF
    pdf = FPDF(orientation='L', unit='mm', format='A4')
    pdf.add_page()
    
    # Add title
    pdf.set_font("Helvetica", "B", 20)
    pdf.cell(0, 15, "Chess Game", ln=True, align="C")
    
    # Add metadata
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 10, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=True, align="C")
    pdf.ln(5)
    
    # Initial position
    save_board_position(pdf, board, "Initial Position")
    
    # Play some sample moves
    moves = ["e2e4", "e7e5", "g1f3", "b8c6"]
    
    for move_uci in moves:
        move = chess.Move.from_uci(move_uci)
        board.push(move)
        save_board_position(pdf, board, f"Move: {move.uci()}")
    
    # Save PDF
    pdf.output("chess_game.pdf")
    print("Chess game PDF created successfully: chess_game.pdf")

def save_board_position(pdf, board, title):
    """
    Adds a chess board position to the PDF.
    """
    
    # Create SVG representation of the board
    svg_str = chess.svg.board(board, size=300)
    
    # Convert SVG to PNG in memory
    png_bytes = BytesIO()
    cairosvg.svg2png(bytestring=svg_str.encode('utf-8'), write_to=png_bytes)
    png_bytes.seek(0)
    
    # Add to PDF
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, title, ln=True)
    
    # Add board image
    png_bytes.seek(0)
    pdf.image(png_bytes, x=20, w=150)
    
    # Add board status
    pdf.set_font("Helvetica", "", 10)
    pdf.ln(5)
    pdf.cell(0, 6, f"FEN: {board.fen()}", ln=True)
    
    if board.is_check():
        pdf.cell(0, 6, "Status: CHECK", ln=True)
    elif board.is_checkmate():
        pdf.cell(0, 6, "Status: CHECKMATE", ln=True)
    elif board.is_stalemate():
        pdf.cell(0, 6, "Status: STALEMATE", ln=True)
    else:
        turn = "White" if board.turn else "Black"
        pdf.cell(0, 6, f"Status: {turn} to move", ln=True)
    
    pdf.ln(10)

if __name__ == "__main__":
    create_chess_pdf()
