import './App.css';
import { useEffect, useMemo, useRef, useState } from 'react';

function App() {
  const [status, setStatus] = useState('disconnected');
  const [lastMessageAt, setLastMessageAt] = useState(null);
  const [latestState, setLatestState] = useState(null);
  const [history, setHistory] = useState([]);
  const [handlers, setHandlers] = useState([]);
  const [handlersError, setHandlersError] = useState(null);
  const wsRef = useRef(null);

  const wsUrl = useMemo(() => {
    return "ws://127.0.0.1:8000/stream-store/ws";
    const env = process.env.REACT_APP_BACKEND_WS;
    if (env && env.trim()) return env.trim();

    const proto = window.location.protocol === 'https:' ? 'wss' : 'ws';

    return `${proto}://${window.location.host}/stream-store/ws`;
    // return `${proto}://localhost:3000/stream-store/ws`;
  }, []);

  const loadHandlers = async () => {
    try {
      setHandlersError(null);
      const res = await fetch('/supervisor/handlers');
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      setHandlers(Array.isArray(data?.handlers) ? data.handlers : []);
    } catch (e) {
      setHandlersError(String(e?.message || e));
    }
  };

  const reconcileHandlers = async () => {
    try {
      setHandlersError(null);
      const res = await fetch('/supervisor/reconcile', { method: 'POST' });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      await loadHandlers();
    } catch (e) {
      setHandlersError(String(e?.message || e));
    }
  };

  useEffect(() => {
    let ws;
    let closed = false;

    const connect = () => {
      setStatus('connecting');
      ws = new WebSocket(wsUrl);
      wsRef.current = ws;

      ws.onopen = () => {
        setStatus('connected');
      };

      ws.onmessage = (evt) => {
        const now = new Date();
        setLastMessageAt(now);
        try {
          console.log(evt)
          const data = JSON.parse(evt.data);
          setLatestState(data);
          setHistory((prev) => {
            const next = [{ at: now.toISOString(), state: data }, ...prev];
            return next.slice(0, 200);
          });
        } catch (e) {
          setHistory((prev) => {
            const next = [{ at: now.toISOString(), state: { _raw: String(evt.data) } }, ...prev];
            return next.slice(0, 200);
          });
        }
      };

      ws.onerror = (e) => {
        console.log('error', e)
        setStatus('error');
      };

      ws.onclose = () => {
        wsRef.current = null;
        if (closed) return;
        setStatus('disconnected');
        // simple backoff reconnect
        setTimeout(connect, 750);
      };
    };

    connect();

    return () => {
      closed = true;
      try {
        ws?.close();
      } catch (_) {}
    };
  }, [wsUrl]);

  useEffect(() => {
    let alive = true;
    loadHandlers();
    const id = setInterval(() => {
      if (!alive) return;
      loadHandlers();
    }, 2000);
    return () => {
      alive = false;
      clearInterval(id);
    };
  }, []);

  const clearHistory = () => setHistory([]);

  return (
    <div className="App">
      <div className="Shell">
        <div className="Topbar">
          <div>
            <div className="Title">Stream Processor Engine</div>
            <div className="Sub">
              WebSocket: <code className="Mono">{wsUrl}</code>
            </div>
          </div>

          <div className="Right">
            <div className={`Pill Pill--${status}`}>
              <span className="Dot" /> {status}
            </div>
            <button className="Btn" onClick={clearHistory}>
              Clear
            </button>
          </div>
        </div>

        <div className="Grid">
          <div className="Card">
            <div className="CardTitle">Latest state</div>
            <div className="Meta">
              Last update:{' '}
              <span className="Mono">
                {lastMessageAt ? lastMessageAt.toLocaleTimeString() : '—'}
              </span>
            </div>
            <pre className="Pre">
              {latestState ? JSON.stringify(latestState, null, 2) : 'Waiting for first state...'}
            </pre>
          </div>

          <div className="Card">
            <div className="CardTitle Row">
              <span>Handler containers</span>
              <button className="Btn Btn--small" onClick={reconcileHandlers}>
                Reconcile
              </button>
            </div>
            <div className="Meta">
              {handlersError ? (
                <span className="Error">Error: {handlersError}</span>
              ) : (
                <span>Showing <span className="Mono">{handlers.length}</span> handlers</span>
              )}
            </div>
            <div className="TableWrap">
              <table className="Table">
                <thead>
                  <tr>
                    <th>key</th>
                    <th>container</th>
                    <th>status</th>
                  </tr>
                </thead>
                <tbody>
                  {handlers.length === 0 ? (
                    <tr>
                      <td colSpan={3} className="EmptyCell">No handler info yet.</td>
                    </tr>
                  ) : (
                    handlers.map((h) => (
                      <tr key={h.key}>
                        <td className="Mono">{h.key}</td>
                        <td className="Mono">{h.container_name}</td>
                        <td>
                          <span className={`Tag Tag--${h.status}`}>{h.status}</span>
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          </div>

          <div className="Card">
            <div className="CardTitle">State stream (newest first)</div>
            <div className="Meta">
              Showing <span className="Mono">{history.length}</span> messages (max 200)
            </div>
            <div className="Stream">
              {history.length === 0 ? (
                <div className="Empty">No messages yet.</div>
              ) : (
                history.map((item, idx) => (
                  <details className="Item" key={`${item.at}-${idx}`} open={idx < 1}>
                    <summary className="Summary">
                      <span className="Mono">{item.at}</span>
                      <span className="Hint">click to expand</span>
                    </summary>
                    <pre className="Pre Pre--small">{JSON.stringify(item.state, null, 2)}</pre>
                  </details>
                ))
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
