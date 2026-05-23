import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db
from backend.models.models import PaintingLamp

def init_paintings_data():
    """初始化画中灯数据"""
    
    paintings_data = [
        {
            'name': '西安安伽墓围屏石榻所见夜宴图',
            'description': '陕西西安北周大象元年（579年）安伽墓的墓主人为北周同州萨保（北朝至隋唐时期专门管理胡人聚落的首领），墓中出土一套围屏石榻，围屏表面以浅浮雕形式表现各类生活或仪式场景。其中，正面第三幅描绘了一组宴飨奏乐的场面：主人坐在屋宇下的榻上，手持酒杯，边环绕乐伎与侍者。在屋殿前的台阶下，以一名胡腾舞者为中心，有五人应和起舞，有的人抱持酒坛，有的人高举酒盆。其中，右上角的一人手捧灯台，灯盏上的灯火尚在燃烧。这个不起眼的细节，既暗示了宴会的时间是在夜间，同时也将灯台融入舞蹈的律动中来。伴随节奏跳跃的灯火，席间众人的酒盏交相辉映，将夜宴的欢愉表现得淋漓尽致。从灯的形制来看，舞者手捧的豆形油灯延续了汉代豆形灯的基本样式，并没有更多华丽的修饰。',
            'period': '北周',
            'image_path': 'b9.jpg'
        },
        {
            'name': '山西屯留康庄村元墓南壁灯檠图',
            'description': '其中的灯檠延续此前传统，多以影作砖雕形式雕出，侍女则以壁画形式表现。其中的灯檠也不同于金代以前的多枝形制，而是着重表现巨大的灯柱，山东地区元代墓葬中的灯檠多是此类。在山西地区元代墓葬壁画中，此类灯檠则被表现得更为高大，甚至超出了一般人的身高。本图位于山西屯留康庄村一座元大德十年（1306年）的墓葬中，在墓室南壁东侧雕出一座大如椽柱的灯檠，燃灯的侍女踩在板凳上，小心翼翼地将手高举去挑拨灯捻，仍然尚有不及。',
            'period': '元',
            'image_path': 'b10.jpg'
        },
        {
            'name': '敦煌莫高窟第159窟壁画中的五彩灯轮',
            'description': '莫高窟中第159窟西龛的唐代壁画中，一名妇人正在五层灯轮前燃灯，另有两人手捧灯油走向灯轮。在二人面前的供台上，还放着炊饼、胡饼、馓饼与䭔飥等四盘供品。这样的画面生动地反映出唐代民间燃灯供佛的场景。',
            'period': '唐',
            'image_path': 'b11.jpg'
        },
        {
            'name': '敦煌莫高窟第146窟壁画中的五彩灯轮',
            'description': '莫高窟第400窟北壁上的隋代壁画中便有一座灯轮，灯轮共三层，每层皆有羽葆，羽葆下放置油灯。类似的灯轮除了三层的，多以五层灯轮较为常见。在莫高窟第146窟北壁的五代经变画（如图）中，于虹桥前立有一座五层灯轮，灯轮为十字形底座，每层上放置油灯。灯轮下有两人正在点灯，其身后则有两人手捧油碗作为接应。这样的灯轮不仅出现在经变画中，同时在世俗百姓的礼佛场景中也有表现。',
            'period': '隋',
            'image_path': 'b12.jpg'
        },
        {
            'name': '河南南阳麒麟岗画像石墓所见灯檠图像',
            'description': '该图位于南阳麒麟岗汉代画像石墓中。在墓葬主室墓门南北的立柱上，分别刻画了一座三枝的灯檠与一位站立燃灯的侍女。长生之灯与燃灯者的组合形象，使墓葬的幽室内多了一些人间之味，也让墓主的精神在另一个世界长久地明亮。',
            'period': '汉',
            'image_path': 'b16.jpg'
        },
        {
            'name': '山西大同辽代许从赟墓西南壁灯檠图',
            'description': '山西大同辽代乾亨四年（982年）许从赟墓，则在墓室西南壁上绘制了一幅灯檠图，不同者在于灯檠整体均为影作砖雕，共三枝，灯盏之上还绘制出了燃烧的灯芯。灯檠右侧的侍女一手捧油碗，另一手持勺子添加灯油。',
            'period': '辽',
            'image_path': 'b14.jpg'
        },
        {
            'name': '北京大兴西杭子村1号辽墓南壁燃灯图',
            'description': '北京大兴西杭子村1号辽墓，在墓室南壁西侧绘制了一幅燃灯图。图中侍女身着红色圆领窄袖长袍，正在为灯檠填油。她面前的灯檠与人同高，其中灯架下面的两个灯碗为绘制，上方中央的灯碗则为影作砖雕。',
            'period': '辽',
            'image_path': 'b13.jpg'
        },
        {
            'name': '河南南阳陈棚画像石墓所见燃灯侍者形象',
            'description': '河南南阳陈棚汉代画像石墓中，在墓葬后室南北过梁的立柱上，分别以浅浮雕的形式刻画了两位持灯侍者。二人身着袍服，梳髻戴帻，单手握灯。灯均为觚形，其中灯焰正在燃烧。',
            'period': '汉',
            'image_path': 'b15.jpg'
        }
    ]
    
    with app.app_context():
        # 检查是否已有数据
        existing_count = PaintingLamp.query.count()
        if existing_count > 0:
            print(f"数据库中已有 {existing_count} 条画中灯数据，跳过初始化")
            return
        
        # 插入数据
        for painting_data in paintings_data:
            painting = PaintingLamp(
                name=painting_data['name'],
                description=painting_data['description'],
                period=painting_data['period'],
                image_path=painting_data['image_path']
            )
            db.session.add(painting)
        
        try:
            db.session.commit()
            print(f"成功插入 {len(paintings_data)} 条画中灯数据")
        except Exception as e:
            db.session.rollback()
            print(f"插入画中灯数据失败: {e}")

if __name__ == '__main__':
    init_paintings_data()
