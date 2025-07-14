import React, { useState, useRef } from 'react';
import { Chessboard, type PieceDropHandlerArgs } from 'react-chessboard';
import { Chess } from 'chess.js';
import { sendMoves } from './api';

export default function EncryptApp() {
  const [game, setGame]             = useState(new Chess());
  const [pgnHistory, setPgnHistory] = useState<string[]>([]);
  const [message, setMessage]       = useState('');
  const [error, setError]           = useState('');
  const [success, setSuccess]       = useState('');
  const [loading, setLoading]       = useState(false);
  const [downloadUrl, setDownloadUrl] = useState<string | null>(null);
  const messageRef = useRef<HTMLDivElement>(null);

  const onPieceDrop = ({ sourceSquare, targetSquare }: PieceDropHandlerArgs) => {
    const copy = new Chess(game.fen());
    const mv   = copy.move({ from: sourceSquare, to: targetSquare, promotion: 'q' });
    if (!mv) return false;
    setGame(copy);
    setPgnHistory(copy.history());
    return true;
  };

  const handleEncrypt = async () => {
    setError('');
    setSuccess('');
    setDownloadUrl(null);
    setLoading(true);
    try {
      const pgn = game.pgn();
      if (!pgn || pgn.trim() === '') {
        setError('Please play some moves to generate a PGN.');
        setLoading(false);
        return;
      }
      if (!message) {
        setError('Please enter a message to encrypt.');
        setLoading(false);
        return;
      }
      try {
        const response = await sendMoves(pgn, message);
        // Create a download link for the returned ZIP
        const url = window.URL.createObjectURL(new Blob([response.data]));
        setDownloadUrl(url);
        setSuccess('Encryption successful! Download your package below.');
        setTimeout(() => {
          if (messageRef.current) messageRef.current.scrollIntoView({ behavior: 'smooth' });
        }, 100);
      } catch (err: any) {
        const msg = err?.response?.data?.detail || err.message || 'Unknown error';
        setError('Encryption failed: ' + msg);
        setSuccess('');
        setDownloadUrl(null);
        setTimeout(() => {
          if (messageRef.current) messageRef.current.scrollIntoView({ behavior: 'smooth' });
        }, 100);
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="encrypt-bg">
      <div className="main-content">
        <div className="card encrypt-card">
          <h3>1. Play Your Moves</h3>
          <Chessboard
            options={{
              position: game.fen(),
              onPieceDrop,
              boardWidth: 400,
              arePiecesDraggable: true
            }}
          />
          <ol className="pgn-list">
            {pgnHistory.map((mv, i) => (
              <li key={i}>
                {i%2===0?`${Math.floor(i/2)+1}. `:''}{mv}
              </li>
            ))}
          </ol>
        </div>

        <div className="card encrypt-card">
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
          {error && <div className="alert alert-error" style={{marginTop: 16}}>{error}</div>}
          {success && <div className="alert alert-success" style={{marginTop: 16}}>{success}</div>}
          {downloadUrl && (
            <div className="info mt-4">
              <h4>Download Your Encrypted Package</h4>
              <a href={downloadUrl} download="chessperm_package.zip" className="button secondary">
                Download ZIP
              </a>
              <div style={{marginTop: 8, fontSize: 12, color: '#888'}}>
                (Contains stego.png and private_key.txt)
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
