// src/DecryptApp.tsx
import React, { useState, useRef } from 'react';
import { Chessboard, type PieceDropHandlerArgs } from 'react-chessboard';
import { Chess } from 'chess.js';
import JSZip from 'jszip';
import { decryptStego } from './api';

export default function DecryptApp() {
  const [game, setGame]             = useState(new Chess());
  const [pgnHistory, setPgnHistory] = useState<string[]>([]);
  const [file, setFile]             = useState<File | null>(null);
  const [privateKey, setKey]        = useState('');
  const [plaintext, setPlaintext]   = useState('');
  const [error, setError]           = useState('');
  const [success, setSuccess]       = useState('');
  const [loading, setLoading]       = useState(false);
  const messageRef = useRef<HTMLDivElement>(null);

  const onPieceDrop = ({ sourceSquare, targetSquare }: PieceDropHandlerArgs) => {
    const copy = new Chess(game.fen());
    const mv   = copy.move({ from: sourceSquare, to: targetSquare, promotion: 'q' });
    if (!mv) return false;
    setGame(copy);
    setPgnHistory(copy.history());
    return true;
  };

  const handleDecrypt = async () => {
    setError('');
    setSuccess('');
    setPlaintext('');
    setLoading(true);
    try {
      if (!file) {
        setError('Please upload your stego ZIP or PNG.');
        setLoading(false);
        return;
      }
      if (!privateKey) {
        setError('Please paste your private key.');
        setLoading(false);
        return;
      }
      // 1) If it's a ZIP, unzip & grab stego.png
      let imageFile = file;
      if (file.name.endsWith('.zip') || file.type === 'application/zip') {
        try {
          const zip = await JSZip.loadAsync(file);
          const blob = await zip.file('stego.png')!.async('blob');
          imageFile = new File([blob], 'stego.png', { type: 'image/png' });
        } catch (e) {
          setError('Could not unzip your package. Make sure it contains stego.png.');
          setLoading(false);
          return;
        }
      }
      // 2) Now send the PNG + key + PGN to backend
      const pgn = game.pgn();
      try {
        const { data } = await decryptStego(imageFile, privateKey, pgn);
        setPlaintext(data.message);
        setSuccess('Decryption successful!');
        setError('');
        setTimeout(() => {
          if (messageRef.current) messageRef.current.scrollIntoView({ behavior: 'smooth' });
        }, 100);
      } catch (err: any) {
        const msg = err?.response?.data?.detail || err.message || 'Unknown error';
        setError('Decryption failed: ' + msg);
        setSuccess('');
        setPlaintext('');
        setTimeout(() => {
          if (messageRef.current) messageRef.current.scrollIntoView({ behavior: 'smooth' });
        }, 100);
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="decrypt-bg">
      <div className="main-content">
        <div className="card decrypt-card">
          <h3>1. Replay the Encryption Moves</h3>
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

        <div className="card decrypt-card">
          <h3>2. Upload & Decrypt</h3>
          <input
            type="file"
            accept="image/png,application/zip"
            onChange={e => setFile(e.target.files?.[0] || null)}
            disabled={loading}
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
          {error && <div className="alert alert-error" style={{marginTop: 16}}>{error}</div>}
          {success && <div className="alert alert-success" style={{marginTop: 16}}>{success}</div>}
          {plaintext && (
            <div className="info mt-4">
              <h4>Decrypted Text</h4>
              <pre className="plaintext-output">{plaintext}</pre>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
