// QualityCheckGauge.jsx
import { useState } from 'react';
import { HiOutlineQrCode, HiOutlineCheckCircle, HiOutlineXMark, HiPlay, HiPause } from "react-icons/hi2";

function QualityCheckGauge() {
  // สลับสถานะเพื่อดูหน้า Mockup: false = หน้าสแกน, true = หน้าเริ่มวัดงานแล้ว
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

  // ข้อมูลจำลอง (Mock Data) สำหรับจุดวัดประเภทต่างๆ เพื่อดูพิกัดความสมดุลบนจอ 13 นิ้ว
  const mockPoints = [
    { name: "AIRPOINT 1", xValue: 50.012, xPass: true, yValue: 49.998, yPass: true, finalPass: true },
    { name: "AIRPOINT 2", xValue: 50.054, xPass: false, yValue: 50.002, yPass: true, finalPass: false },
    { name: "AIRPOINT 3", xValue: 49.991, xPass: true, yValue: 49.985, yPass: false, finalPass: false },
    { name: "AIRPOINT 4", xValue: 50.000, xPass: true, yValue: 50.005, yPass: true, finalPass: true }
  ];

  const handleStart = (e) => {
    e.preventDefault();
    if (serial.trim()) setIsStarted(true);
  };

  const handleReset = () => {
    setIsStarted(false);
    setSerial("");
  };

  return (
    <div className="w-full space-y-3">
      {/* Top Header Bar แบบกระชับสัดส่วนสูงเพียงเล็กน้อย */}
      <div className="flex justify-between items-center bg-card p-3 rounded-xl border border-white/10 shadow-sm">
        <div className="flex items-center gap-3">
          <h1 className="text-xl font-bold text-primary">Measurement: XY-Axis Simultaneous</h1>
          {isStarted && (
            <span className="text-xs px-2 py-0.5 bg-blue-500/10 text-blue-400 border border-blue-500/20 rounded-md font-mono">
              SN: {serial || "MOCK-SERIAL-1234"}
            </span>
          )}
        </div>
        
        {isStarted && (
          <div className="flex gap-2">
            <button onClick={handleReset} className="flex items-center gap-1 bg-red-500/10 text-red-500 border border-red-500/20 px-3 py-1.5 rounded-lg text-xs font-bold hover:bg-red-500/20 transition-colors">
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
        /* 2. หน้าจอ Dashboard วัด XY พร้อมกันในหน้าเดียว (Grid Layout ปรับสมดุลจอ 13 นิ้ว) */
        <div className="grid grid-cols-2 gap-3">
          {mockPoints.map((point) => (
            <div key={point.name} className="bg-card p-3 rounded-xl border border-white/5 space-y-2 shadow-sm flex flex-col justify-between">
              {/* ชื่อจุดวัด */}
              <div className="flex justify-between items-center border-b border-white/5 pb-1">
                <span className="text-xs font-bold text-accent uppercase tracking-wider">{point.name}</span>
                <span className={`text-[10px] px-1.5 py-0.2 rounded font-bold uppercase ${point.finalPass ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'}`}>
                  {point.finalPass ? "PASS" : "NG"}
                </span>
              </div>
              {/*Timer ตัวนับเวลา*/}

              {/* ส่วนของการจัดวาง แกน X และ แกน Y ข้างกันแบบซ้าย-ขวา */}
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