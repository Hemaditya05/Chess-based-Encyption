import axios from 'axios';

const API_BASE_URL = 'http://127.0.0.1:8000/api';

/**
 * Encrypt: sends FormData with input_type, pgn/password, and message → returns ZIP blob (stego.png + private_key.txt).
 */
export const sendMoves = (formData: FormData) => {
  return axios.post(`${API_BASE_URL}/encrypt`, formData, {
    responseType: 'blob',
    headers: { 'Content-Type': 'multipart/form-data' },
  });
};

/**
 * Decrypt: sends stego file + private_key + input_type + pgn/password → returns { message } JSON.
 */
export const decryptStego = (
  file: File,
  privateKey: string,
  inputType: 'pgn' | 'password',
  pgn?: string,
  password?: string
) => {
  const fd = new FormData();
  fd.append('file', file);
  fd.append('private_key', privateKey);
  fd.append('input_type', inputType);
  if (inputType === 'pgn' && pgn) {
    fd.append('pgn', pgn);
  } else if (inputType === 'password' && password) {
    fd.append('password', password);
  }

  return axios.post(`${API_BASE_URL}/decrypt`, fd, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
};
