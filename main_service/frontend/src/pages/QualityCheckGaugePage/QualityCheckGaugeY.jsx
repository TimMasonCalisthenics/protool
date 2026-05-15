import { useState, useEffect } from 'react';
import { useStep } from '@context/MeasurementContext';
import { showSuccess, showError } from '@utils/toast';
import { saveMeasurement, cancelMeasurementDraft } from '@services/measurementService';
import { getMeasurementsDraft } from '@services/measurements_draft_service';
import { HiOutlineCheckCircle, HiOutlineXMark } from "react-icons/hi2";

function QualityCheckGaugeY() {
  const { product, draftMeasurement, zeroStep } = useStep();
  const [measurementData, setMeasurementData] = useState([]);

  useEffect(() => {
    if (!draftMeasurement?.id) return;
    const fetchData = async () => {
    try {
      const response = await getMeasurementsDraft();
      if (response?.data) {
      // ✅ ดึงข้อมูลออกมาให้ถูกชั้น เหมือนแกน X
        let specs = response.data.measurement_draft_specs || response.data.specs || response.data;
      
      // ✅ ถ้าเป็น Object (ที่เพิ่งแกะเป็น Dict จาก Backend) ให้หาตัวที่เป็น Array
        if (!Array.isArray(specs)) {
          const foundKey = Object.keys(response.data).find(key => Array.isArray(response.data[key]));
          specs = foundKey ? response.data[foundKey] : [];
        }
      
      // ✅ กรองเฉพาะจุดวัดของใบงานปัจจุบัน
        const currentSpecs = specs.filter(s => s.measurement_id === draftMeasurement.id);
        setMeasurementData(currentSpecs);
    }
    }catch (error) {
    console.error("Fetch Y error:", error);
    }
  };
    fetchData();
    const intervalId = setInterval(fetchData, 500);
    return () => clearInterval(intervalId);
  }, [draftMeasurement?.id]);

  // แก้ไข: ใส่ Array.isArray ป้องกันแครช
  const isYFilled = () => {
    if (!Array.isArray(product?.step3)) return false;
    return product.step3.every(point => {
      const detail = measurementData.find(
      item => item.point_name?.toLowerCase() === point.point_name?.toLowerCase()
      );
    // ✅ ต้องมีข้อมูลทั้ง X และ Y ถึงจะกดจบงานได้
      return detail?.captured_values?.length >= 2; 
    });
  };

  const handleFinish = async () => {
    try {
      await saveMeasurement("air_gauge");
      showSuccess("บันทึกข้อมูลเรียบร้อย!");
      zeroStep(); 
    } catch (error) {
      showError("Error saving measurement");
    }
  };

  const handleCancel = async () => {
    try {
        await cancelMeasurementDraft();
        showSuccess("ยกเลิกงานวัดเรียบร้อย");
        zeroStep();
    } catch (error) {
        showError("Error canceling draft");
    }
  };

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      <div className="flex justify-between items-center bg-white/5 p-4 rounded-2xl border border-white/10">
        <h1 className="text-3xl font-bold text-primary">Measurement: Y-Axis</h1>
        <div className="flex gap-2">
            <button onClick={handleCancel} className="flex items-center gap-1 bg-red-500/10 text-red-500 border border-red-500/20 px-4 py-2 rounded-xl font-bold hover:bg-red-500/20">
                <HiOutlineXMark size={20}/> Cancel
            </button>
            <button disabled={!isYFilled()} onClick={handleFinish} className="flex items-center gap-2 bg-green-500 text-white px-6 py-2 rounded-xl disabled:opacity-50 font-bold">
                Finish & Save <HiOutlineCheckCircle size={20} />
            </button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* แก้ไข: ใส่ Array.isArray เช็คก่อน map */}
        {Array.isArray(product?.step3) && product.step3.length > 0 ? (
            product.step3.map((point, idx) => {
            const detail = measurementData.find(item => item.point_name?.toLowerCase() === point.point_name?.toLowerCase());
            const valueY = detail?.captured_values?.[1]; 
            const result = detail?.final_value;
            const rawValueY = detail?.captured_values?.[1];
            const finalValueY = Array.isArray(rawValueY) ? rawValueY[0] : rawValueY;

            return (
                <div key={idx} className="glass-card p-6 rounded-xl border border-border-color space-y-4">
                <span className="text-lg font-bold text-accent uppercase">{point.point_name}</span>
                <div className={`h-24 flex flex-col items-center justify-center rounded-xl border-2 transition-all
                    ${valueY !== undefined ? 'bg-indigo-500/10 border-indigo-500 shadow-lg shadow-indigo-500/20' : 'bg-black/5 border-dashed border-gray-300'}`}>
                    <span className="text-xs uppercase font-bold text-secondary">Y-Axis Value</span>
                    <span className="text-4xl font-mono font-bold text-primary">
                    {finalValueY !== undefined ? Number(finalValueY).toFixed(3) : "-.---"}
                    </span>
                </div>
                
                <div className={`py-2 text-center rounded-lg font-bold border transition-colors
                    ${result != null 
                        ? (detail?.is_pass ? 'bg-green-500 text-white border-green-600' : 'bg-red-500 text-white border-red-600') 
                        : 'bg-transparent text-secondary border-dashed'}`}>
                    Final Result: {result != null ? Number(result).toFixed(3) : "Waiting for Y..."}
                </div>
                </div>
            )
            })
        ) : (
             <div className="col-span-full text-center py-10 text-secondary">
                  ไม่มีจุดวัดให้แสดง หรือกำลังโหลดข้อมูล...
             </div>
        )}
      </div>
    </div>
  );
}
export default QualityCheckGaugeY;