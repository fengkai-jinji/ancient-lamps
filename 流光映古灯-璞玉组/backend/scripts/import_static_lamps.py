import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db
from backend.models.models import AncientLamp

# 前端固定的灯具数据
static_lamps = [
    {
        "id": "static-lamp-1",
        "name": "透雕人鸟兽玉饰件",
        "age": "新石器时代",
        "material": "玉",
        "type": "装饰灯",
        "image": "a7.png",
        "detail": "新石器时代玉器精品，造型精美，工艺精湛",
        "properties": "透雕工艺;造型独特",
        "history": "出土于新石器时代遗址，反映了当时的工艺水平"
    },
    {
        "id": "static-lamp-2",
        "name": "青铜剑",
        "age": "春秋",
        "material": "青铜",
        "type": "特殊灯",
        "image": "a8.png",
        "detail": "春秋时期青铜剑，剑身修长，纹饰精美",
        "properties": "青铜铸造;纹饰精美",
        "history": "春秋时期兵器，象征权力和地位"
    },
    {
        "id": "static-lamp-3",
        "name": "长信宫灯",
        "age": "西汉",
        "material": "青铜（鎏金）",
        "type": "人物形灯",
        "image": "a9.png",
        "detail": "西汉长信宫灯，造型为宫女持灯，设计巧妙",
        "properties": "鎏金工艺;环保设计",
        "history": "出土于河北满城汉墓，为汉代灯具精品"
    },
    {
        "id": "static-lamp-4",
        "name": "错银铜牛灯",
        "age": "东汉",
        "material": "青铜（错银）",
        "type": "动物形灯",
        "image": "a10.png",
        "detail": "东汉错银铜牛灯，造型为牛形，工艺精湛",
        "properties": "错银工艺;造型生动",
        "history": "东汉时期灯具精品，反映了当时的工艺水平"
    },
    {
        "id": "static-lamp-5",
        "name": "青釉熊水注灯",
        "age": "东吴-西晋",
        "material": "青瓷",
        "type": "座灯",
        "image": "a11.png",
        "detail": "东吴-西晋青釉熊水注灯，造型为熊形，釉色青润",
        "properties": "青釉工艺;造型生动",
        "history": "三国两晋时期陶瓷灯具精品"
    },
    {
        "id": "static-lamp-6",
        "name": "十五连枝灯",
        "age": "战国",
        "material": "青铜",
        "type": "连枝灯",
        "image": "a2.png",
        "detail": "战国十五连枝灯，造型复杂，工艺精湛",
        "properties": "青铜铸造;造型复杂",
        "history": "战国时期灯具精品，象征富贵和地位"
    },
    {
        "id": "static-lamp-7",
        "name": "省油瓷灯",
        "age": "宋",
        "material": "瓷",
        "type": "座灯",
        "image": "a14.png",
        "detail": "宋代省油瓷灯，设计巧妙，省油环保",
        "properties": "瓷质细腻;省油设计",
        "history": "宋代灯具精品，体现了当时的环保理念"
    },
    {
        "id": "static-lamp-8",
        "name": "雁鱼铜灯",
        "age": "西汉",
        "material": "青铜",
        "type": "动物形灯",
        "image": "a12.png",
        "detail": "西汉雁鱼铜灯，造型为雁衔鱼，设计巧妙",
        "properties": "青铜铸造;环保设计",
        "history": "西汉时期灯具精品，反映了当时的工艺水平"
    }
]

def import_static_lamps():
    with app.app_context():
        # 检查数据库连接
        try:
            from sqlalchemy import text
            db.session.execute(text('SELECT 1'))
            print("数据库连接正常")
        except Exception as e:
            print(f"数据库连接失败: {e}")
            return
        
        # 导入数据
        for lamp_data in static_lamps:
            # 检查是否已存在
            existing_lamp = AncientLamp.query.filter_by(灯具编号=lamp_data['id']).first()
            if existing_lamp:
                print(f"灯具 {lamp_data['name']} 已存在，跳过")
                continue
            
            # 创建新灯具
            new_lamp = AncientLamp(
                灯具编号=lamp_data['id'],
                灯具名称=lamp_data['name'],
                所属朝代=lamp_data['age'],
                灯具类型=lamp_data['type'],
                材质=lamp_data['material'],
                详情描述=lamp_data['detail'],
                工艺特点=lamp_data['properties'],
                历史背景=lamp_data['history'],
                图片路径=lamp_data['image']
            )
            
            try:
                db.session.add(new_lamp)
                db.session.commit()
                print(f"成功导入灯具: {lamp_data['name']}")
            except Exception as e:
                db.session.rollback()
                print(f"导入灯具 {lamp_data['name']} 失败: {e}")
        
        print("导入完成")

if __name__ == "__main__":
    import_static_lamps()
