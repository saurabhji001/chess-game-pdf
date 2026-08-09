import chess
import chess.svg
from fpdf import FPDF
from io import BytesIO
import cairosvg
from datetime import datetime
import tempfile
import os


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
        try:
            move = chess.Move.from_uci(move_uci)
        except ValueError:
            print(f"Skipping invalid move: {move_uci}")
            continue
        if move not in board.legal_moves:
            # If the move isn't legal in the current position, skip it
            print(f"Skipping illegal move in current position: {move_uci}")
            continue
        board.push(move)
        save_board_position(pdf, board, f"Move: {move.uci()}")
    
    # Save PDF
    output_path = "chess_game.pdf"
    try:
        pdf.output(output_path)
        print(f"Chess game PDF created successfully: {output_path}")
    except Exception as e:
        print(f"Failed to write PDF to {output_path}: {e}")


def save_board_position(pdf, board, title):
    """
    Adds a chess board position to the PDF. Each position will be placed on its own page.
    """
    # Start a new page for each position so layout is predictable
    pdf.add_page()

    # Create SVG representation of the board
    svg_str = chess.svg.board(board, size=300)
    
    # Convert SVG to PNG in memory
    png_bytes = BytesIO()
    try:
        cairosvg.svg2png(bytestring=svg_str.encode('utf-8'), write_to=png_bytes)
    except Exception as e:
        # If conversion fails, add a note to the PDF and return
        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(0, 8, title, ln=True)
        pdf.set_font("Helvetica", "", 10)
        pdf.cell(0, 6, f"Failed to render board image: {e}", ln=True)
        return

    png_bytes.seek(0)
    
    # Write PNG bytes to a temporary file because FPDF.image expects a filename
    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
        tmp.write(png_bytes.getvalue())
        tmp_path = tmp.name

    try:
        # Add title
        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(0, 8, title, ln=True)
        pdf.ln(2)
        
        # Add board image from temp file
        try:
            pdf.image(tmp_path, x=20, w=150)
        except Exception as e:
            pdf.set_font("Helvetica", "", 10)
            pdf.cell(0, 6, f"Failed to insert board image: {e}", ln=True)
        
        # Add board status
        pdf.set_font("Helvetica", "", 10)
        pdf.ln(5)
        pdf.cell(0, 6, f"FEN: {board.fen()}", ln=True)
        
        # Check game-ending conditions first
        if board.is_checkmate():
            pdf.cell(0, 6, "Status: CHECKMATE", ln=True)
        elif board.is_stalemate():
            pdf.cell(0, 6, "Status: STALEMATE", ln=True)
        elif board.is_check():
            pdf.cell(0, 6, "Status: CHECK", ln=True)
        else:
            turn = "White" if board.turn else "Black"
            pdf.cell(0, 6, f"Status: {turn} to move", ln=True)
        
        pdf.ln(10)
    finally:
        # Clean up temporary file
        try:
            os.remove(tmp_path)
        except OSError:
            pass


if __name__ == "__main__":
    create_chess_pdf()
