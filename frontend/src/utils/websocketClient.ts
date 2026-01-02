export interface WebSocketMessage {
  type: 'audio' | 'text' | 'control' | 'transcription' | 'response' | 'status' | 'volume' | 'error' | 'reminders';
  data: any;
}

export interface WebSocketCallbacks {
  onTranscription?: (text: string) => void;
  onResponse?: (text: string, audio: string | null, commandType: string) => void;
  onStatus?: (status: string, message: string) => void;
  onVolume?: (volume: number) => void;
  onError?: (error: string) => void;
  onConnect?: () => void;
  onDisconnect?: () => void;
  onReminders?: (reminders: any[]) => void;
}

export class WebSocketClient {
  private ws: WebSocket | null = null;
  private clientId: string;
  private callbacks: WebSocketCallbacks = {};
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectTimeout = 3000;
  private url: string;

  constructor(url: string, clientId: string) {
    this.url = url;
    this.clientId = clientId;
  }

  connect(callbacks: WebSocketCallbacks): Promise<void> {
    return new Promise((resolve, reject) => {
      try {
        this.callbacks = callbacks;
        const wsUrl = `${this.url}/ws/${this.clientId}`;
        
        console.log(`Connecting to WebSocket: ${wsUrl}`);
        this.ws = new WebSocket(wsUrl);

        this.ws.onopen = () => {
          console.log('WebSocket connected');
          this.reconnectAttempts = 0;
          if (this.callbacks.onConnect) {
            this.callbacks.onConnect();
          }
          resolve();
        };

        this.ws.onmessage = (event) => {
          try {
            const message: WebSocketMessage = JSON.parse(event.data);
            this.handleMessage(message);
          } catch (error) {
            console.error('Error parsing WebSocket message:', error);
          }
        };

        this.ws.onerror = (error) => {
          console.error('WebSocket error:', error);
          reject(error);
        };

        this.ws.onclose = () => {
          console.log('WebSocket disconnected');
          if (this.callbacks.onDisconnect) {
            this.callbacks.onDisconnect();
          }
          this.attemptReconnect();
        };
      } catch (error) {
        reject(error);
      }
    });
  }

  private handleMessage(message: WebSocketMessage): void {
    console.log('Received message:', message);

    switch (message.type) {
      case 'transcription':
        if (this.callbacks.onTranscription) {
          this.callbacks.onTranscription(message.data.text);
        }
        break;

      case 'response':
        if (this.callbacks.onResponse) {
          this.callbacks.onResponse(
            message.data.text,
            message.data.audio,
            message.data.command_type
          );
        }
        break;

      case 'status':
        if (this.callbacks.onStatus) {
          this.callbacks.onStatus(message.data.status, message.data.message);
        }
        break;

      case 'volume':
        if (this.callbacks.onVolume) {
          this.callbacks.onVolume(message.data.volume);
        }
        break;

      case 'error':
        if (this.callbacks.onError) {
          this.callbacks.onError(message.data.error);
        }
        break;

      case 'reminders':
        if (this.callbacks.onReminders) {
          this.callbacks.onReminders(message.data.reminders);
        }
        break;
    }
  }

  sendText(text: string): void {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      const message: WebSocketMessage = {
        type: 'text',
        data: { text }
      };
      this.ws.send(JSON.stringify(message));
    }
  }

  sendAudio(audioData: ArrayBuffer): void {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(audioData);
    }
  }

  sendControl(action: string, data?: any): void {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      const message: WebSocketMessage = {
        type: 'control',
        data: { action, ...data }
      };
      this.ws.send(JSON.stringify(message));
    }
  }

  private attemptReconnect(): void {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++;
      console.log(`Reconnecting... Attempt ${this.reconnectAttempts}`);
      
      setTimeout(() => {
        this.connect(this.callbacks).catch(error => {
          console.error('Reconnection failed:', error);
        });
      }, this.reconnectTimeout);
    }
  }

  disconnect(): void {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }

  isConnected(): boolean {
    return this.ws !== null && this.ws.readyState === WebSocket.OPEN;
  }
}
