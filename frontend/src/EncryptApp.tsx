import React, { useState, useRef } from 'react';
import { Chessboard, type PieceDropHandlerArgs } from 'react-chessboard';
import { Chess } from 'chess.js';
import { sendMoves } from './api';

export default function EncryptApp() {
  const [game, setGame] = useState(new Chess());
  const [pgnHistory, setPgnHistory] = useState<string[]>([]);
  const [message, setMessage] = useState('');
  const [feedback, setFeedback] = useState<{ type: 'error' | 'success', text: string } | null>(null);
  const [loading, setLoading] = useState(false);
  const [downloadUrl, setDownloadUrl] = useState<string | null>(null);
  const messageRef = useRef<HTMLDivElement>(null);

  const onPieceDrop = ({ sourceSquare, targetSquare }: PieceDropHandlerArgs) => {
    const copy = new Chess();
    copy.loadPgn(game.pgn()); // clone the full game history
    const mv = copy.move({ from: sourceSquare, to: targetSquare, promotion: 'q' });
    if (!mv) return false;
    setGame(copy);
    setPgnHistory(copy.history());
    return true;
  };

  const handleEncrypt = async () => {
    setFeedback(null);
    setDownloadUrl(null);
    setLoading(true);
    try {
      const pgn = game.pgn();
      if (!pgn || pgn.trim() === '') {
        setFeedback({ type: 'error', text: 'Please play some moves to generate a PGN.' });
        return;
      }
      if (!message) {
        setFeedback({ type: 'error', text: 'Please enter a message to encrypt.' });
        return;
      }
      try {
        const response = await sendMoves(pgn, message);
        const url = window.URL.createObjectURL(new Blob([response.data]));
        setDownloadUrl(url);
        setFeedback({ type: 'success', text: 'Encryption successful! Download your package below.' });
        setTimeout(() => messageRef.current?.scrollIntoView({ behavior: 'smooth' }), 100);
      } catch (err: any) {
        const msg = err?.response?.data?.detail || err.message || 'Unknown error';
        setFeedback({ type: 'error', text: 'Encryption failed: ' + msg });
        setTimeout(() => messageRef.current?.scrollIntoView({ behavior: 'smooth' }), 100);
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="encrypt-bg">
      <div className="main-content two-col-layout"> {/* Added two-col-layout back here */}
        <div className="left-col board-wrapper"> {/* Renamed left-col and added board-wrapper */}
          <div className="card board-card">
            <h3>1. Play Your Moves</h3>
            <Chessboard
              options={{
                position: game.fen(),
                onPieceDrop,
                boardWidth: 600, // Increased board size for a "complete big board" feel
                arePiecesDraggable: true
              }}
            />
          </div>
        </div>
        <div className="right-col message-history-wrapper"> {/* Renamed right-col */}
          <div className="card move-history-card">
            <h3>Move History</h3>
            <ol className="pgn-list">
              {pgnHistory.map((mv, i) => (
                <li key={i}>
                  {i % 2 === 0 ? `${Math.floor(i / 2) + 1}. ` : ''}{mv}
                </li>
              ))}
            </ol>
          </div>
          <div className="card encrypt-card scroll-section">
            <h3>2. Enter Message & Encrypt</h3>
            <textarea
              className="input message"
              placeholder="Type your secret message here…"
              value={message}
              onChange={e => setMessage(e.target.value)}
              disabled={loading}
            />
            <button className="button primary" onClick={handleEncrypt} disabled={loading}>
              {loading ? 'Encrypting…' : 'Encrypt Message'}
            </button>
            <div ref={messageRef} />
            {feedback && <div className={`alert alert-${feedback.type}`} style={{ marginTop: 16 }}>{feedback.text}</div>}
            {downloadUrl && (
              <div className="info mt-4">
                <h4>Download Your Encrypted Package</h4>
                <a href={downloadUrl} download="chessperm_package.zip" className="button secondary">
                  Download ZIP
                </a>
                <div style={{ marginTop: 8, fontSize: 12, color: '#888' }}>
                  (Contains stego.png and private_key.txt)
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}