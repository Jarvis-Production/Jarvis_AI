import React from 'react';

interface CommandHistoryItem {
  id: string;
  user: string;
  assistant: string;
  timestamp: Date;
}

interface CommandHistoryProps {
  history: CommandHistoryItem[];
  onClear: () => void;
}

export const CommandHistory: React.FC<CommandHistoryProps> = ({ history, onClear }) => {
  return (
    <div className="command-history">
      <div className="history-header">
        <h3>История команд</h3>
        {history.length > 0 && (
          <button onClick={onClear} className="clear-button">
            Очистить
          </button>
        )}
      </div>
      
      <div className="history-list">
        {history.length === 0 ? (
          <div className="history-empty">
            <p>История команд пуста</p>
          </div>
        ) : (
          history.map((item) => (
            <div key={item.id} className="history-item">
              <div className="history-user">
                <span className="label">Вы:</span>
                <span className="text">{item.user}</span>
              </div>
              <div className="history-assistant">
                <span className="label">Джарвис:</span>
                <span className="text">{item.assistant}</span>
              </div>
              <div className="history-timestamp">
                {item.timestamp.toLocaleTimeString()}
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};
