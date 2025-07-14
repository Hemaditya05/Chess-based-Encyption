import axios from 'axios';

const API_BASE_URL = 'http://127.0.0.1:8000/api';

/**
 * Encrypt: sends PGN & message → returns ZIP blob (stego.png + private_key.txt).
 */
export const sendMoves = (pgn: string, message: string) => {
  const fd = new FormData();
  fd.append('pgn', pgn);
  fd.append('message', message);

  return axios.post(`${API_BASE_URL}/encrypt`, fd, {
    responseType: 'blob',
    headers: { 'Content-Type': 'multipart/form-data' },
  });
};

/**
 * Decrypt: sends stego file + private_key + pgn → returns { message } JSON.
 */
export const decryptStego = (
  file: File,
  privateKey: string,
  pgn: string
) => {
  const fd = new FormData();
  fd.append('file', file);
  fd.append('private_key', privateKey);
  fd.append('pgn', pgn);

  return axios.post(`${API_BASE_URL}/decrypt`, fd, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
};
