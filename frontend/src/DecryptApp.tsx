import { useState, useRef } from 'react';
import { Chessboard, type PieceDropHandlerArgs } from 'react-chessboard';
import { Chess } from 'chess.js';
import JSZip from 'jszip';
import { decryptStego } from './api';

export default function DecryptApp() {
  const [game, setGame] = useState(new Chess());
  const [pgnHistory, setPgnHistory] = useState<string[]>([]);
  const [file, setFile] = useState<File | null>(null);
  const [privateKey, setKey] = useState('');
  const [inputType, setInputType] = useState<'pgn' | 'password'>('pgn');
  const [password, setPassword] = useState('');
  const [plaintext, setPlaintext] = useState('');
  const [feedback, setFeedback] = useState<{ type: 'error' | 'success', text: string } | null>(null);
  const [loading, setLoading] = useState(false);
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

  const handleDecrypt = async () => {
    setFeedback(null);
    setPlaintext('');
    setLoading(true);
    try {
      if (!file) {
        setFeedback({ type: 'error', text: 'Please upload your stego ZIP or PNG.' });
        return;
      }
      if (!privateKey) {
        setFeedback({ type: 'error', text: 'Please paste your private key.' });
        return;
      }

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

      let imageFile = file;
      if (file.name.endsWith('.zip') || file.type === 'application/zip') {
        try {
          const zip = await JSZip.loadAsync(file);
          const blob = await zip.file('stego.png')!.async('blob');
          imageFile = new File([blob], 'stego.png', { type: 'image/png' });
        } catch (e) {
          setFeedback({ type: 'error', text: 'Could not unzip your package. Make sure it contains stego.png.' });
          return;
        }
      }

      try {
        const { data } = await decryptStego(
          imageFile, 
          privateKey, 
          inputType,
          inputType === 'pgn' ? game.pgn() : undefined,
          inputType === 'password' ? password : undefined
        );
        setPlaintext(data.message);
        setFeedback({ type: 'success', text: 'Decryption successful!' });
        setTimeout(() => messageRef.current?.scrollIntoView({ behavior: 'smooth' }), 100);
      } catch (err: any) {
        const msg = err?.response?.data?.detail || err.message || 'Unknown error';
        setFeedback({ type: 'error', text: 'Decryption failed: ' + msg });
        setTimeout(() => messageRef.current?.scrollIntoView({ behavior: 'smooth' }), 100);
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="decrypt-bg">
      <div className="main-content two-col-layout">
        <div className="left-col board-wrapper">
          <div className="card board-card">
            <h3>1. Choose Input Type & Replay Moves</h3>
            
            {/* Input Type Selection */}
            <div className="input-type-selector" style={{ marginBottom: '20px' }}>
              <label style={{ display: 'block', marginBottom: '10px', fontWeight: 'bold' }}>
                Select Input Type:
              </label>
              <div style={{ display: 'flex', gap: '20px' }}>
                <label style={{ display: 'flex', alignItems: 'center', gap: '5px' }}>
                  <input
                    type="radio"
                    name="decryptInputType"
                    value="pgn"
                    checked={inputType === 'pgn'}
                    onChange={(e) => setInputType(e.target.value as 'pgn' | 'password')}
                  />
                  Chess Moves (PGN)
                </label>
                <label style={{ display: 'flex', alignItems: 'center', gap: '5px' }}>
                  <input
                    type="radio"
                    name="decryptInputType"
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
                <h4>Replay the Encryption Moves</h4>
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
                  This password must match the one used during encryption.
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
          <div className="card decrypt-card">
            <h3>2. Upload & Decrypt</h3>
            <label htmlFor="file-upload" className="button primary input-file-label">
              {file ? file.name : 'Choose ZIP or PNG file'}
            </label>
            <input
              id="file-upload"
              type="file"
              accept="image/png,application/zip"
              onChange={e => setFile(e.target.files?.[0] || null)}
              disabled={loading}
              className="input-file-hidden"
            />
            <textarea
              className="input message"
              placeholder="Paste your private key here…"
              value={privateKey}
              onChange={e => setKey(e.target.value)}
              disabled={loading}
            />
            <button className="button primary" onClick={handleDecrypt} disabled={loading}>
              {loading ? 'Decrypting…' : 'Decrypt Message'}
            </button>
            <div ref={messageRef} />
            {feedback && <div className={`alert alert-${feedback.type}`} style={{ marginTop: 16 }}>{feedback.text}</div>}
            {plaintext && (
              <div className="info mt-4">
                <h4>Decrypted Text</h4>
                <pre className="plaintext-output">{plaintext}</pre>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}