from maa.agent.agent_server import AgentServer
from maa.custom_recognition import CustomRecognition
from maa.context import Context
import time


@AgentServer.custom_recognition("skill_ocr_detection")
class SkillOCRRecognition(CustomRecognition):
    """
    自定义OCR识别模块，用于检测技能CD状态和动画状态
    - 检测技能图标上的"剩余"文字判断CD状态
    - 检测"御主"文字判断动画状态
    """
    
    def analyze(
        self,
        context: Context,
        argv: CustomRecognition.AnalyzeArg,
    ) -> CustomRecognition.AnalyzeResult:

        # 定义不同技能的ROI列表
        skill_roilist = [
            # 技能1roi
            [34,540,76,82],
            # 技能2roi
            [123,542,75,77],
            # 技能3roi
            [211,542,77,78],
            # 技能4roi
            [351,543,75,79],
            # 技能5roi
            [442,542,74,78],
            # 技能6roi
            [529,538,76,83],
            # 技能7roi
            [670,541,77,81],
            # 技能8roi
            [758,546,76,72],
            # 技能9roi
            [846,545,75,73],
        ]

        # 基于 skill_roilist 循环处理每个技能 ROI
        for idx, roi in enumerate(skill_roilist):
            print(f"开始识别技能{idx+1} - ROI: {roi}")
            # 后续逻辑可在此循环内继续展开
            result = context.run_recognition(
                "技能是否进入cd",
                argv.image,
                pipeline_override={
                    "技能是否进入cd": {
                        "recognition": "OCR",
                        "roi": roi, 
                        "expected": "剩余"
                    }
                }
            )


            if not result:
                print(f"技能{idx+1} 未进入CD状态")
                context.run_action("点击技能", 
                    box=(roi[0], roi[1], roi[2], roi[3]),
                    reco_detail="",
                    pipeline_override={
                        "点击技能": {
                            "action": "Click",
                            "target": True,
                        }
                    }

                )
            else:
                print(f"技能{idx+1} 进入CD状态")
                
        return None



@AgentServer.custom_recognition("animation_accelerator")
class AnimationAccelerator(CustomRecognition):
    """
    动画加速模块，用于在技能释放后快速点击空白区域加速动画
    """
    
    def analyze(
        self,
        context: Context,
        argv: CustomRecognition.AnalyzeArg,
    ) -> CustomRecognition.AnalyzeResult:
        try:
            # 获取加速参数
            click_positions = argv.param.get("positions", [[600, 300]])  # 默认点击位置
            click_count = argv.param.get("count", 3)  # 默认点击次数
            click_delay = argv.param.get("delay", 0.1)  # 默认点击间隔
            
            logger.info(f"启动动画加速 - 点击位置: {click_positions}, 点击次数: {click_count}, 间隔: {click_delay}s")
            
            # 执行多次点击操作
            for i in range(click_count):
                for pos in click_positions:
                    if len(pos) >= 2:
                        click_job = context.tasker.controller.post_click(pos[0], pos[1])
                        click_job.wait()
                        logger.info(f"动画加速点击 - 位置: {pos}, 第{i+1}/{click_count}次")
                time.sleep(click_delay)
            
            logger.info("动画加速完成")
            
            # 返回成功结果
            return CustomRecognition.AnalyzeResult(
                box=(0, 0, 0, 0),
                detail="Animation acceleration completed",
                confidence=1.0
            )
            
        except Exception as e:
            error_msg = f"动画加速过程中发生错误: {str(e)}"
            logger.error(error_msg)
            return CustomRecognition.AnalyzeResult(
                box=(0, 0, 0, 0),
                detail=error_msg,
                confidence=0.0
            )