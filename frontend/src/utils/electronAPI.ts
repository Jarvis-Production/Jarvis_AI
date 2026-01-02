// Модуль для взаимодействия с Electron API
import { ipcRenderer } from 'electron';

export interface ElectronAPI {
  // Управление backend
  startBackend: () => Promise<{ success: boolean }>;
  stopBackend: () => Promise<{ success: boolean }>;
  getBackendStatus: () => Promise<{ running: boolean }>;
  
  // Диалоги
  selectFile: (options: any) => Promise<any>;
  showMessageBox: (options: any) => Promise<any>;
}

declare global {
  interface Window {
    electronAPI?: ElectronAPI;
  }
}

// Проверка доступности Electron API
const isElectron = () => {
  return window.electronAPI !== undefined;
};

// Electron API функции
export const electronAPI: ElectronAPI = {
  startBackend: async () => {
    if (isElectron()) {
      return await ipcRenderer.invoke('start-backend');
    }
    return { success: false };
  },
  
  stopBackend: async () => {
    if (isElectron()) {
      return await ipcRenderer.invoke('stop-backend');
    }
    return { success: false };
  },
  
  getBackendStatus: async () => {
    if (isElectron()) {
      return await ipcRenderer.invoke('get-backend-status');
    }
    return { running: false };
  },
  
  selectFile: async (options: any) => {
    if (isElectron()) {
      return await ipcRenderer.invoke('select-file', options);
    }
    return { canceled: true };
  },
  
  showMessageBox: async (options: any) => {
    if (isElectron()) {
      return await ipcRenderer.invoke('show-message-box', options);
    }
    return { response: 0 };
  }
};

// Функция для определения платформы
export const isDesktopApp = () => {
  return isElectron();
};

// Функция для работы с аудио (улучшенная для десктопа)
export class DesktopAudioProcessor {
  private audioContext: AudioContext | null = null;
  private mediaRecorder: MediaRecorder | null = null;
  private audioChunks: Blob[] = [];
  
  async initialize() {
    try {
      // Для десктопного приложения можем использовать более продвинутые настройки
      const constraints = {
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true,
          sampleRate: 16000,
          channelCount: 1
        }
      };
      
      const stream = await navigator.mediaDevices.getUserMedia(constraints);
      
      // Создаем AudioContext с оптимальными настройками для распознавания речи
      this.audioContext = new AudioContext({
        sampleRate: 16000,
        channelCount: 1
      });
      
      const source = this.audioContext.createMediaStreamSource(stream);
      
      // Подключаем анализатор для визуализации
      const analyser = this.audioContext.createAnalyser();
      analyser.fftSize = 256;
      source.connect(analyser);
      
      return { stream, audioContext: this.audioContext, analyser };
    } catch (error) {
      console.error('Failed to initialize desktop audio:', error);
      throw error;
    }
  }
  
  async startRecording(): Promise<void> {
    if (!this.audioContext) {
      await this.initialize();
    }
    
    // Используем MediaRecorder для записи с оптимальными настройками
    const stream = await this.initialize();
    
    this.mediaRecorder = new MediaRecorder(stream.stream, {
      mimeType: 'audio/webm;codecs=opus',
      audioBitsPerSecond: 16000
    });
    
    this.audioChunks = [];
    
    this.mediaRecorder.ondataavailable = (event) => {
      if (event.data.size > 0) {
        this.audioChunks.push(event.data);
      }
    };
    
    this.mediaRecorder.start(100); // Записываем каждые 100ms
  }
  
  async stopRecording(): Promise<Blob> {
    return new Promise((resolve) => {
      if (!this.mediaRecorder) {
        resolve(new Blob());
        return;
      }
      
      this.mediaRecorder.onstop = () => {
        const audioBlob = new Blob(this.audioChunks, { type: 'audio/webm' });
        resolve(audioBlob);
      };
      
      this.mediaRecorder.stop();
    });
  }
  
  async cleanup() {
    if (this.audioContext) {
      await this.audioContext.close();
      this.audioContext = null;
    }
    
    if (this.mediaRecorder) {
      this.mediaRecorder = null;
    }
    
    this.audioChunks = [];
  }
}

// Экспорт по умолчанию
export default electronAPI;