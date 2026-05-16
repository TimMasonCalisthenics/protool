import { useEffect } from "react";
import { StepProvider, useStep } from "@context/MeasurementContext";
import QualityCheckGauge from "@/pages/QualityCheckGaugePage/QualityCheckGauge";


const StepContent = () => {
  const { currentStep, zeroStep } = useStep();
  
  // ย้ายการทำ zeroStep มาไว้ใน useEffect เพื่อไม่ให้ React แครชตอน Render
  useEffect(() => {
    if (currentStep === -1) {
      zeroStep();
    }
  }, [currentStep, zeroStep]);

  switch (currentStep) {
    case 1:
      // หน้าแรก: รับ Serial + วัดแกน X
      return <QualityCheckGauge />;
    case 2:
      // หน้าสอง: วัดแกน Y + สรุปผล
      return <QualityCheckGauge />;
    case -1:
      return null; // รอให้ useEffect ทำงาน
    default:
      // Default ให้กลับมาหน้า X เสมอ
      return <QualityCheckGauge />;
  }
};

export default function Measurement() {
  return (
    <StepProvider>
      <div className="w-full mx-auto p-4 bg-page min-h-[calc(100-4rem)]">
        <StepContent />
      </div>
    </StepProvider>
  );
}