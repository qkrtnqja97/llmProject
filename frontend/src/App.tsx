import "./App.css";

function App() {
  return (
    <div className="page">
      <h1>💬 AI 챗봇</h1>
      <p>LLM 프로젝트 시작 🚀</p>

      <div className="chatBox">
        <div className="bubble bot">안녕! 나는 너의 업무 도우미야 😎</div>
        <div className="bubble user">재고 확인해줘</div>
        <div className="bubble bot">오케이. 어떤 품목이야?</div>
      </div>

      <div className="inputRow">
        <input className="input" placeholder="메시지 입력..." />
        <button className="sendBtn">보내기</button>
      </div>
    </div>
  );
}

export default App;
