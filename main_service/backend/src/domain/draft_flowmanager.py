from enumCore.common import CommonEnum
class DraftFlowManager:

    FLOW_ORDER = [CommonEnum.Mitutoyo.value, CommonEnum.Airguage.value,CommonEnum.Airguage_X_axis.value , CommonEnum.Airguage_Y_axis.value]

    @staticmethod
    def build_flow(product):
        used = {p.sensor_type for p in product.spec_points}
        ordered = [s for s in DraftFlowManager.FLOW_ORDER if s in used]
        return ['qrcode'] + ordered

    @staticmethod
    def next_stage(flow, current):
        idx = flow.index(current)
        if idx + 1 >= len(flow):
            return "completed"
        return flow[idx + 1]