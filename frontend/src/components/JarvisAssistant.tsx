import React, { useState, useEffect, useRef } from 'react';
import { WebSocketClient } from '../utils/websocketClient';
import { AudioProcessorUtil, playAudioFromBase64 } from '../utils/audioProcessor';
import { WaveAnimation } from './WaveAnimation';
import { CommandHistory } from './CommandHistory';

interface CommandHistoryItem {
  id: string;
  user: string;
  assistant: string;
  timestamp: Date;
}

const WS_URL = import.meta.env.VITE_WS_URL || 'ws://localhost:8000';

export const JarvisAssistant: React.FC = () => {
  const [isConnected, setIsConnected] = useState(false);
  const [isListening, setIsListening] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [volume, setVolume] = useState(0);
  const [transcription, setTranscription] = useState('');
  const [response, setResponse] = useState('');
  const [status, setStatus] = useState('');
  const [history, setHistory] = useState<CommandHistoryItem[]>([]);
  const [error, setError] = useState('');

  const wsClientRef = useRef<WebSocketClient | null>(null);
  const audioProcessorRef = useRef<AudioProcessorUtil | null>(null);
  const volumeIntervalRef = useRef<number>();
  const recordingTimeoutRef = useRef<number>();

  useEffect(() => {
    initializeWebSocket();
    
    return () => {
      cleanup();
    };
  }, []);

  const initializeWebSocket = async () => {
    try {
      const clientId = `client_${Date.now()}`;
      wsClientRef.current = new WebSocketClient(WS_URL, clientId);

      await wsClientRef.current.connect({
        onConnect: () => {
          setIsConnected(true);
          setStatus('Подключено');
          console.log('Connected to Jarvis');
        },
        onDisconnect: () => {
          setIsConnected(false);
          setStatus('Отключено');
        },
        onTranscription: (text) => {
          setTranscription(text);
          setStatus('Обработка команды...');
        },
        onResponse: (text, audio, commandType) => {
          setResponse(text);
          setIsProcessing(false);
          setStatus('');

          if (transcription) {
            setHistory(prev => [{
              id: Date.now().toString(),
              user: transcription,
              assistant: text,
              timestamp: new Date()
            }, ...prev]);
          }

          if (audio) {
            playAudioFromBase64(audio).catch(err => {
              console.error('Error playing audio:', err);
            });
          }
        },
        onStatus: (status, message) => {
          setStatus(message);
          if (status === 'processing') {
            setIsProcessing(true);
          }
        },
        onVolume: (vol) => {
          setVolume(vol);
        },
        onError: (err) => {
          setError(err);
          setIsProcessing(false);
          setStatus('');
        }
      });
    } catch (error) {
      console.error('Failed to connect:', error);
      setError('Не удалось подключиться к серверу');
    }
  };

  const startListening = async () => {
    try {
      setError('');
      
      if (!audioProcessorRef.current) {
        audioProcessorRef.current = new AudioProcessorUtil();
        await audioProcessorRef.current.initialize();
      }

      setIsListening(true);
      setTranscription('');
      setResponse('');
      setStatus('Слушаю...');

      volumeIntervalRef.current = window.setInterval(() => {
        if (audioProcessorRef.current) {
          const vol = audioProcessorRef.current.getVolume();
          setVolume(vol);
        }
      }, 50);

      audioProcessorRef.current.startRecording();

      recordingTimeoutRef.current = window.setTimeout(async () => {
        await stopListening();
      }, 5000);

    } catch (error) {
      console.error('Error starting listening:', error);
      setError('Ошибка доступа к микрофону');
      setIsListening(false);
    }
  };

  const stopListening = async () => {
    try {
      if (volumeIntervalRef.current) {
        clearInterval(volumeIntervalRef.current);
      }

      if (recordingTimeoutRef.current) {
        clearTimeout(recordingTimeoutRef.current);
      }

      setIsListening(false);
      setVolume(0);
      setStatus('Обработка...');
      setIsProcessing(true);

      if (audioProcessorRef.current && audioProcessorRef.current.isRecording()) {
        const audioBlob = await audioProcessorRef.current.stopRecording();
        
        const arrayBuffer = await audioBlob.arrayBuffer();
        
        if (wsClientRef.current && wsClientRef.current.isConnected()) {
          wsClientRef.current.sendAudio(arrayBuffer);
        }
      }
    } catch (error) {
      console.error('Error stopping listening:', error);
      setIsProcessing(false);
    }
  };

  const cleanup = async () => {
    if (volumeIntervalRef.current) {
      clearInterval(volumeIntervalRef.current);
    }

    if (recordingTimeoutRef.current) {
      clearTimeout(recordingTimeoutRef.current);
    }

    if (audioProcessorRef.current) {
      await audioProcessorRef.current.cleanup();
    }

    if (wsClientRef.current) {
      wsClientRef.current.disconnect();
    }
  };

  const clearHistory = () => {
    setHistory([]);
    if (wsClientRef.current && wsClientRef.current.isConnected()) {
      wsClientRef.current.sendControl('clear_history');
    }
  };

  const getIconSize = () => {
    const baseSize = 150;
    const maxSize = 300;
    const scale = 1 + (volume / 100);
    return Math.min(maxSize, baseSize * scale);
  };

  const getIconColor = () => {
    if (isProcessing) return '#FFD700';
    if (isListening) return '#00FF00';
    return '#0096FF';
  };

  return (
    <div className="jarvis-container">
      <div className="status-bar">
        <div className={`connection-status ${isConnected ? 'connected' : 'disconnected'}`}>
          {isConnected ? '● Подключено' : '○ Отключено'}
        </div>
        {status && <div className="status-message">{status}</div>}
      </div>

      <div className="main-area">
        <WaveAnimation isActive={isListening || isProcessing} volume={volume} />

        <div className="jarvis-icon-container">
          <div
            className={`jarvis-icon ${isListening ? 'listening' : ''} ${isProcessing ? 'processing' : ''}`}
            style={{
              width: `${getIconSize()}px`,
              height: `${getIconSize()}px`,
              borderColor: getIconColor(),
              boxShadow: `0 0 ${volume}px ${getIconColor()}`,
            }}
          >
            <div className="icon-inner" style={{ borderColor: getIconColor() }}>
              <div className="icon-core" style={{ backgroundColor: getIconColor() }}></div>
            </div>
          </div>
        </div>

        <div className="text-area">
          {response && (
            <div className="response-text">
              <span className="label">Джарвис:</span>
              <span className="text">{response}</span>
            </div>
          )}

          {transcription && (
            <div className="transcription-text">
              <span className="label">Вы:</span>
              <span className="text">{transcription}</span>
            </div>
          )}
        </div>

        {error && (
          <div className="error-message">
            {error}
          </div>
        )}

        <div className="controls">
          {!isListening && !isProcessing && (
            <button
              onClick={startListening}
              className="mic-button"
              disabled={!isConnected}
            >
              <svg width="40" height="40" viewBox="0 0 24 24" fill="white">
                <path d="M12 14c1.66 0 3-1.34 3-3V5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3z"/>
                <path d="M17 11c0 2.76-2.24 5-5 5s-5-2.24-5-5H5c0 3.53 2.61 6.43 6 6.92V21h2v-3.08c3.39-.49 6-3.39 6-6.92h-2z"/>
              </svg>
              <span>Нажмите чтобы говорить</span>
            </button>
          )}

          {isListening && (
            <button
              onClick={stopListening}
              className="mic-button stop"
            >
              <svg width="40" height="40" viewBox="0 0 24 24" fill="white">
                <rect x="6" y="6" width="12" height="12" rx="2"/>
              </svg>
              <span>Остановить</span>
            </button>
          )}

          {isProcessing && (
            <div className="processing-indicator">
              <div className="spinner"></div>
              <span>Обработка...</span>
            </div>
          )}
        </div>
      </div>

      <CommandHistory history={history} onClear={clearHistory} />
    </div>
  );
};
