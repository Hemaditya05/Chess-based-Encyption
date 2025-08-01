import { useState, useRef } from 'react';
import { Chessboard, type PieceDropHandlerArgs } from 'react-chessboard';
import { Chess } from 'chess.js';
import { sendMoves } from './api';

export default function EncryptApp() {
  const [game, setGame] = useState(new Chess());
  const [pgnHistory, setPgnHistory] = useState<string[]>([]);
  const [message, setMessage] = useState('');
  const [inputType, setInputType] = useState<'pgn' | 'password'>('pgn');
  const [password, setPassword] = useState('');
  const [feedback, setFeedback] = useState<{ type: 'error' | 'success', text: string } | null>(null);
  const [loading, setLoading] = useState(false);
  const [downloadUrl, setDownloadUrl] = useState<string | null>(null);
  const messageRef = useRef<HTMLDivElement>(null);

  const onPieceDrop = ({ sourceSquare, targetSquare }: PieceDropHandlerArgs) => {
    if (!targetSquare) return false;
    const copy = new Chess();
    copy.loadPgn(game.pgn()); // clone the full game history
    const mv = copy.move({ from: sourceSquare, to: targetSquare, promotion: 'q' as const });
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
      // Validate inputs based on input type
      if (inputType === 'pgn') {
        const pgn = game.pgn();
        if (!pgn || pgn.trim() === '') {
          setFeedback({ type: 'error', text: 'Please play some moves to generate a PGN.' });
          return;
        }
      } else {
        if (!password || password.trim() === '') {
          setFeedback({ type: 'error', text: 'Please enter a password.' });
          return;
        }
      }
      
      if (!message) {
        setFeedback({ type: 'error', text: 'Please enter a message to encrypt.' });
        return;
      }

      // Build FormData
      const form = new FormData();
      form.append('input_type', inputType);
      if (inputType === 'pgn') {
        form.append('pgn', game.pgn());
      } else {
        form.append('password', password);
      }
      form.append('message', message);

      try {
        const response = await sendMoves(form);
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
      <div className="main-content two-col-layout">
        <div className="left-col board-wrapper">
          <div className="card board-card">
            <h3>1. Choose Input Type & Generate Key</h3>
            
            {/* Input Type Selection */}
            <div className="input-type-selector" style={{ marginBottom: '20px' }}>
              <label style={{ display: 'block', marginBottom: '10px', fontWeight: 'bold' }}>
                Select Input Type:
              </label>
              <div style={{ display: 'flex', gap: '20px' }}>
                <label style={{ display: 'flex', alignItems: 'center', gap: '5px' }}>
                  <input
                    type="radio"
                    name="inputType"
                    value="pgn"
                    checked={inputType === 'pgn'}
                    onChange={(e) => setInputType(e.target.value as 'pgn' | 'password')}
                  />
                  Chess Moves (PGN)
                </label>
                <label style={{ display: 'flex', alignItems: 'center', gap: '5px' }}>
                  <input
                    type="radio"
                    name="inputType"
                    value="password"
                    checked={inputType === 'password'}
                    onChange={(e) => setInputType(e.target.value as 'pgn' | 'password')}
                  />
                  Password
                </label>
              </div>
            </div>

            {/* Conditional Rendering */}
            {inputType === 'pgn' ? (
              <div>
                <h4>Play Your Moves</h4>
                <Chessboard
                  options={{
                    position: game.fen(),
                    onPieceDrop,
                    allowDragging: true
                  }}
                />
              </div>
            ) : (
              <div>
                <h4>Enter Your Password</h4>
                <input
                  type="password"
                  className="input"
                  placeholder="Enter your password..."
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  style={{ width: '100%', padding: '10px', marginBottom: '10px' }}
                />
                <p style={{ fontSize: '12px', color: '#666', marginTop: '5px' }}>
                  This password will be used to derive the master key for encryption.
                </p>
              </div>
            )}
          </div>
        </div>
        <div className="right-col message-history-wrapper">
          {inputType === 'pgn' && (
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
          )}
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
                <div style={{ marginTop: 8, fontSize: '12px', color: '#888' }}>
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