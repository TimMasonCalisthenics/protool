import { useState, useEffect } from 'react';
import { useStep } from '@context/MeasurementContext';
import { showSuccess, showError } from '@utils/toast';
import { 
  createMeasurementDraft, 
  saveMeasurement, 
  cancelMeasurementDraft, 
  getMeasurementsDraft 
} from '@services/measurementService';
import { start_readSensor, stop_readSensor } from '@services/airgaugeSensor/airgaugeService';
import { HiOutlineQrCode, HiArrowRight, HiOutlineXMark } from "react-icons/hi2";

function QualityCheckGaugeX() {
  const { product, draftMeasurement, setDraftMeasurement, nextStep, zeroStep } = useStep();
  const [serial, setSerial] = useState("");
  const [measurementData, setMeasurementData] = useState([]);
  const [isStarting, setIsStarting] = useState(false);

  // 1. ควบคุมการเริ่ม/หยุด Sensor
  useEffect(() => {
    if (draftMeasurement?.id) {
      start_readSensor().catch(() => console.error("Sensor start failed"));
      return () => {
        stop_readSensor().catch(() => console.error("Sensor stop failed"));
      };
    }
  }, [draftMeasurement?.id]);

  // 2. Polling ดึงข้อมูลทุก 0.5 วินาที
  useEffect(() => {
    if (!draftMeasurement?.id) return;
      const fetchData = async () => {
      try {
        const response = await getMeasurementsDraft();
        if (response?.data) {
          // 1. ลองหาตามชื่อที่ควรจะเป็นก่อน
          let specs = response.data.measurement_draft_specs || response.data.specs;
  
        // 2. ถ้าไม่เจอ ให้หาว่ามี Key ไหนใน data ที่เป็น Array บ้าง (กันพลาด)
        if (!specs) {
          const foundKey = Object.keys(response.data).find(key => Array.isArray(response.data[key]));
          specs = foundKey ? response.data[foundKey] : [];
        }
  
        // 3. กรองข้อมูลเฉพาะของ ID ที่เปิดอยู่
        const currentSpecs = specs.filter(s => s.measurement_id === draftMeasurement.id);
        setMeasurementData(currentSpecs);
        }
      } catch (error) {
        console.error("❌ Fetch error:", error);
      }
    };
    fetchData(); 
    const intervalId = setInterval(fetchData, 500);
    return () => clearInterval(intervalId);
  }, [draftMeasurement?.id]);

  const handleStartMeasurement = async (e) => {
    e.preventDefault();
    if (!serial.trim()) return showError("กรุณาระบุ Serial Number");
    setIsStarting(true);
    
    try {
      const res = await createMeasurementDraft(serial, serial, product.step1.id, 'draft'); 
      
      // ✅ แก้ไข: ไม่ว่า res จะหน้าตาเป็นยังไง ถ้า API ตอบกลับมาสำเร็จ (200 OK)
      // ให้เราสั่ง setDraftMeasurement ทันที เพื่อบังคับให้ UI เปลี่ยนหน้าครับ
      if (res) {
        setDraftMeasurement(res.data || res); 
        showSuccess("Measurement Started!");
      }
    } catch (error) {
      // ⚠️ ถ้ายังขึ้น Error "ไม่สามารถสร้างใบงานได้" ทั้งที่ข้อมูลใน DB มีแล้ว
      // ให้ลอง "ดัก Error" ออกมาดูครับว่าติดอะไรกันแน่
      console.error("DEBUG START:", error);
      showError("ระบบกำลังโหลดใบงานเดิม...");
      
      // 💡 ท่าไม้ตาย: ถ้าสร้างใหม่ไม่ได้ แปลว่ามีของเก่าอยู่ ให้บังคับเปลี่ยนหน้าเลย
      window.location.reload(); // บังคับ Refresh เพื่อให้ useEffect ไปดึงของเก่ามาโชว์
    } finally {
      setIsStarting(false);
    }
  };

  const handleCancel = async () => {
    try {
        await cancelMeasurementDraft(); //
        showSuccess("ยกเลิกงานวัดเรียบร้อย");
        zeroStep(); // กลับไปหน้าแรกสุด
    } catch (error) {
        showError("ไม่สามารถยกเลิกงานได้");
    }
  };

  // เช็คว่าวัดครบทุกจุดหรือยัง
  const isXFilled = () => {
    if (!Array.isArray(product?.step3)) return false;
    return product.step3.every(point => {
      const detail = (measurementData || []).find(
        item => item.point_name?.toLowerCase() === point.point_name?.toLowerCase()
      );
      return detail?.captured_values?.length >= 1; 
    });
  };

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      {/* Header UI แบบเดิมของคุณ */}
      <div className="flex justify-between items-center bg-white/5 p-4 rounded-2xl border border-white/10">
        <h1 className="text-3xl font-bold text-primary">Measurement: X-Axis</h1>
        {draftMeasurement?.id && (
            <div className="flex gap-2">
                <button onClick={handleCancel} className="flex items-center gap-1 bg-red-500/10 text-red-500 border border-red-500/20 px-4 py-2 rounded-xl font-bold hover:bg-red-500/20">
                    <HiOutlineXMark size={20}/> Cancel
                </button>
                <button disabled={!isXFilled()} onClick={nextStep} className="flex items-center gap-2 btn-primary px-6 py-2 rounded-xl disabled:opacity-50">
                    Next to Y-Axis <HiArrowRight />
                </button>
            </div>
        )}
      </div>

      {!draftMeasurement?.id ? (
        /* หน้า Scan QR Code */
        <div className="glass-card p-10 rounded-2xl max-w-lg mx-auto mt-20 text-center space-y-6">
          <HiOutlineQrCode className="text-6xl text-accent mx-auto" />
          <h2 className="text-2xl font-bold">Start New Measurement</h2>
          <form onSubmit={handleStartMeasurement} className="space-y-4">
            <input 
              type="text" autoFocus value={serial} onChange={e => setSerial(e.target.value)}
              placeholder="Scan Serial Number..."
              className="w-full text-center text-xl p-4 glass-input rounded-xl focus:ring-2 focus:ring-accent outline-none font-bold"
            />
            <button type="submit" disabled={isStarting} className="w-full btn-primary py-3 rounded-xl font-bold text-lg disabled:opacity-50">
              {isStarting ? "Starting..." : "Start Measurement"}
            </button>
          </form>
        </div>
      ) : (
        /* ส่วนแสดงผล AIRPOINT แบบเดิม */
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {Array.isArray(product?.step3) && product.step3.map((point) => {
            const detail = (measurementData || []).find(
              item => item.point_name?.toLowerCase() === point.point_name?.toLowerCase()
            );

            // เจาะชั้นข้อมูล [[50.052]]
            const rawValue = detail?.captured_values?.[0];
            const finalValue = Array.isArray(rawValue) ? rawValue[0] : rawValue;
            const resultX = detail?.final_value;

            return (
              <div key={point.point_name} className="glass-card p-6 rounded-xl border border-border-color space-y-4">
                <span className="text-lg font-bold text-accent uppercase">{point.point_name}</span>
                <div className={`h-24 flex flex-col items-center justify-center rounded-xl border-2 transition-all
                  ${finalValue !== undefined 
                    ? (detail?.is_pass 
                      ? 'bg-green-500/10 border-green-500 shadow-lg shadow-green-500/20' // ✅ PASS (เขียว)
                      : 'bg-red-500/10 border-red-500 shadow-lg shadow-red-500/20')     // ❌ NG (แดง)
                      : 'bg-black/5 border-dashed border-gray-300' // ⏳ Waiting
                  }`}>
                  
                  
                  <span className="text-xs uppercase font-bold text-secondary">X-Axis Value</span>
                  <span className={`text-4xl font-mono font-bold 
                     ${finalValue !== undefined 
                      ? (detail?.is_pass ? 'text-green-600' : 'text-red-600') 
                      : 'text-primary'}`}
                    >
                    {finalValue !== undefined ? Number(finalValue).toFixed(3) : "-.---"}
                  </span>
                  
                </div>
                <div className={`mt-2 py-2 text-center rounded-lg font-bold border transition-colors
                    ${resultX != null 
                      ? (detail?.is_pass 
                      ? 'bg-green-500 text-white border-green-600' // ✅ PASS (เขียวเข้มขอบชัด)
                      : 'bg-red-500 text-white border-red-600')  // ❌ NG (แดงเข้มขอบชัด)
                      : 'bg-transparent text-secondary border-dashed border-gray-300' // ⏳ Waiting (โปร่งแสงขอบประ)
                      }`}
                  >
                      Final Result: {resultX != null ? Number(resultX).toFixed(3) : "Waiting for X..."}
                  </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}

export default QualityCheckGaugeX;