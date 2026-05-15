import { useEffect } from "react";
import { StepProvider, useStep } from "@context/MeasurementContext";
import QualityCheckGaugeX from "@pages/QualityCheckGaugePage/QualityCheckGaugeX";
import QualityCheckGaugeY from "@pages/QualityCheckGaugePage/QualityCheckGaugeY";

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
      return <QualityCheckGaugeX />;
    case 2:
      // หน้าสอง: วัดแกน Y + สรุปผล
      return <QualityCheckGaugeY />;
    case -1:
      return null; // รอให้ useEffect ทำงาน
    default:
      // Default ให้กลับมาหน้า X เสมอ
      return <QualityCheckGaugeX />;
  }
};

export default function Measurement() {
  return (
    <StepProvider>
      <div className="w-auto mx-auto p-6 bg-page">
        <StepContent />
      </div>
    </StepProvider>
  );
}