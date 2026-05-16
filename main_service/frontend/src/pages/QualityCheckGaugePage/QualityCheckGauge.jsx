// QualityCheckGauge.jsx
import { useState, useEffect } from 'react';
import { HiOutlineQrCode, HiOutlineCheckCircle, HiOutlineXMark, HiPlay, HiPause } from "react-icons/hi2";

function QualityCheckGauge() {
  // สถานะหน้าจอ: false = หน้าสแกน, true = หน้าเริ่มวัดงานแล้ว
  const [isStarted, setIsStarted] = useState(true); 
  const [serial, setSerial] = useState("");

  // ================= [ ระบบ Timer - Hardcode ] =================
  const [seconds, setSeconds] = useState(0);
  const [isTimerRunning, setIsTimerRunning] = useState(false);

  useEffect(() => {
    let interval = null;
    if (isTimerRunning) {
      interval = setInterval(() => {
        setSeconds((prev) => prev + 1);
      }, 1000);
    } else {
      clearInterval(interval);
    }
    return () => clearInterval(interval);
  }, [isTimerRunning]);

  // ฟังก์ชันแปลงวินาทีเป็น MM:SS
  const formatTime = (totalSeconds) => {
    const mins = Math.floor(totalSeconds / 60).toString().padStart(2, '0');
    const secs = (totalSeconds % 60).toString().padStart(2, '0');
    return `${mins}:${secs}`;
  };

  const handleStartTimer = () => setIsTimerRunning(true);
  const handleStopTimer = () => setIsTimerRunning(false);
  const handleResetTimer = () => {
    setIsTimerRunning(false);
    setSeconds(0);
  };
  // ============================================================

  // ข้อมูลจำลอง (Mock Data) สำหรับจุดวัดแกน XY
  const mockPoints = [
    { name: "AIRPOINT 1", xValue: 50.012, xPass: true, yValue: 49.998, yPass: true, finalPass: true },
    { name: "AIRPOINT 2", xValue: 50.054, xPass: false, yValue: 50.002, yPass: true, finalPass: false },
    { name: "AIRPOINT 3", xValue: 49.991, xPass: true, yValue: 49.985, yPass: false, finalPass: false },
    { name: "AIRPOINT 4", xValue: 50.000, xPass: true, yValue: 50.005, yPass: true, finalPass: true }
  ];

  const handleStart = (e) => {
    e.preventDefault();
    if (serial.trim()) {
      setIsStarted(true);
      handleStartTimer(); // เริ่มจับเวลาทันทีที่สแกนงาน
    }
  };

  const handleResetAll = () => {
    setIsStarted(false);
    setSerial("");
    handleResetTimer();
  };

  return (
    <div className="w-full space-y-3">
      {/* Top Header Bar */}
      <div className="flex justify-between items-center bg-card p-3 rounded-xl border border-white/10 shadow-sm">
        <div className="flex items-center gap-1">
          <h1 className="text-xz font-bold text-primary">Measurement: XY-Axis</h1>
          {isStarted && (
            <span className="text-xs px-2 py-0.1 bg-blue-500/10 text-blue-400 border border-blue-500/20 rounded-md font-mono">
              SN: {serial || "MOCK-SERIAL-1234"}
            </span>
          )}

          {/* ⏱️ ก้อน UI สำหรับระบบ Timer วางต่อจาก Serial Number */}
          {isStarted && (
            <div className="flex items-center gap-1 bg-black/20 px-1 py-1 rounded-lg border border-white/5 ml-2">
              <span className="text-xs text-secondary font-medium">Cycle Time:</span>
              <span className="text-sm font-mono font-bold text-accent animate-pulse">{formatTime(seconds)}</span>
              
              <div className="flex gap-1 ml-1 border-l border-white/10 pl-2">
                {!isTimerRunning ? (
                  <button onClick={handleStartTimer} className="p-1 bg-green-500/20 text-green-400 hover:bg-green-500/30 rounded transition-colors" title="Start">
                    <HiPlay size={12} />
                  </button>
                ) : (
                  <button onClick={handleStopTimer} className="p-1 bg-yellow-500/20 text-yellow-400 hover:bg-yellow-500/30 rounded transition-colors" title="Pause">
                    <HiPause size={12} />
                  </button>
                )}
                <button onClick={handleResetTimer} className="text-[10px] px-1.5 py-0.5 bg-white/5 hover:bg-white/10 rounded text-gray-400 transition-colors">
                  Clear
                </button>
              </div>
            </div>
          )}
        </div>
        
        {isStarted && (
          <div className="flex gap-2">
            <button onClick={handleResetAll} className="flex items-center gap-1 bg-red-500/10 text-red-500 border border-red-500/20 px-3 py-1.5 rounded-lg text-xs font-bold hover:bg-red-500/20 transition-colors">
              <HiOutlineXMark size={14}/> Reset View
            </button>
            <button className="flex items-center gap-1 bg-green-600 text-white px-4 py-1.5 rounded-lg text-xs font-bold hover:bg-green-700 shadow-sm transition-colors">
              <HiOutlineCheckCircle size={14} /> Save Record
            </button>
          </div>
        )}
      </div>

      {!isStarted ? (
        /* 1. หน้าจอ Scan Serial Number */
        <div className="glass-card p-8 rounded-xl max-w-md mx-auto mt-16 text-center space-y-4 shadow-xl">
          <HiOutlineQrCode className="text-5xl text-accent mx-auto" />
          <h2 className="text-xl font-bold">Start New Inspection</h2>
          <form onSubmit={handleStart} className="space-y-3">
            <input 
              type="text" autoFocus value={serial} onChange={e => setSerial(e.target.value)}
              placeholder="Scan Serial Number..."
              className="w-full text-center text-lg p-3 glass-input rounded-lg focus:ring-2 focus:ring-accent outline-none font-bold"
            />
            <button type="submit" className="w-full btn-primary py-2.5 rounded-lg font-bold text-base shadow-md">
              Start Measurement
            </button>
          </form>
        </div>
      ) : (
        /* 2. หน้าจอ Dashboard วัด XY พร้อมกันในหน้าเดียว */
        <div className="grid grid-cols-2 gap-3">
          {mockPoints.map((point) => (
            <div key={point.name} className="bg-card p-3 rounded-xl border border-white/5 space-y-2 shadow-sm flex flex-col justify-between">
              <div className="flex justify-between items-center border-b border-white/5 pb-1">
                <span className="text-xs font-bold text-accent uppercase tracking-wider">{point.name}</span>
                <span className={`text-[10px] px-1.5 py-0.2 rounded font-bold uppercase ${point.finalPass ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'}`}>
                  {point.finalPass ? "PASS" : "NG"}
                </span>
              </div>

              <div className="grid grid-cols-2 gap-2">
                {/* กล่องแสดงผล แกน X */}
                <div className={`p-2 rounded-lg border flex flex-col items-center justify-center h-14 transition-all ${
                  point.xPass ? 'bg-green-500/5 border-green-500/30' : 'bg-red-500/5 border-red-500/30'
                }`}>
                  <span className="text-[10px] text-secondary font-medium uppercase tracking-tight">X-Axis</span>
                  <span className={`text-xl font-mono font-bold ${point.xPass ? 'text-green-500' : 'text-red-500'}`}>
                    {point.xValue.toFixed(3)}
                  </span>
                </div>

                {/* กล่องแสดงผล แกน Y */}
                <div className={`p-2 rounded-lg border flex flex-col items-center justify-center h-14 transition-all ${
                  point.yPass ? 'bg-green-500/5 border-green-500/30' : 'bg-red-500/5 border-red-500/30'
                }`}>
                  <span className="text-[10px] text-secondary font-medium uppercase tracking-tight">Y-Axis</span>
                  <span className={`text-xl font-mono font-bold ${point.yPass ? 'text-green-500' : 'text-red-500'}`}>
                    {point.yValue.toFixed(3)}
                  </span>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default QualityCheckGauge;