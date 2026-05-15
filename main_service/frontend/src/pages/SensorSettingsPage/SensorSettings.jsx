import React from 'react'
import AirgaugeSettings from './sensors/AirgaugeSettings';

function SensorSettings() {
    return (
        <div className="min-h-screen bg-page p-6 text-primary transition-colors duration-300">
            {/* Background Animations */}
            <div className="fixed inset-0 overflow-hidden -z-10">
                <div className="absolute top-[-10%] right-[-5%] w-[500px] h-[500px] bg-accent/10 rounded-full blur-[120px]"></div>
                <div className="absolute bottom-[-10%] left-[-5%] w-[500px] h-[500px] bg-indigo-500/10 rounded-full blur-[120px]"></div>
            </div>

            <div className="max-w-6xl mx-auto space-y-8">
                {/* ตัดปุ่ม Toggle และ Tab Navigation ออกทั้งหมด 
                  เหลือแค่ Component AirgaugeSettings เพียวๆ 
                */}
                <div className="transition-all duration-500 ease-in-out">
                    <div className="relative block animate-in fade-in">
                        <AirgaugeSettings />
                    </div>
                </div>
            </div>
        </div>
    )
}

export default SensorSettings