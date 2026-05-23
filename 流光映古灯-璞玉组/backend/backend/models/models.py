from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class AncientLamp(db.Model):
    __tablename__ = '古代精品灯具'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    灯具编号 = db.Column(db.String(50), unique=True, nullable=False)
    灯具名称 = db.Column(db.String(100), nullable=False)
    所属朝代 = db.Column(db.String(50), nullable=False)
    灯具类型 = db.Column(db.String(50), nullable=False)
    材质 = db.Column(db.String(50), default='青铜')
    详情描述 = db.Column(db.Text)
    工艺特点 = db.Column(db.Text)
    历史背景 = db.Column(db.Text)
    图片路径 = db.Column(db.String(200))
    创建时间 = db.Column(db.DateTime, default=datetime.utcnow)
    更新时间 = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            '灯具编号': self.灯具编号,
            '灯具名称': self.灯具名称,
            'age': self.所属朝代,
            'type': self.灯具类型,
            'material': self.材质,
            'detail': self.详情描述,
            'properties': self.工艺特点.split(';') if self.工艺特点 else [],
            'history': self.历史背景,
            'image': f'/static/images/{self.图片路径}' if self.图片路径 else None,
            'name': self.灯具名称
        }

class LampHistory(db.Model):
    __tablename__ = '灯具历史时间轴'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    dynasty = db.Column(db.String(50), nullable=False)
    year_range = db.Column(db.String(100), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    image_path = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'year': self.dynasty,
            'dynasty': self.year_range,
            'name': self.name,
            'image': f'/static/images/{self.image_path}',
            'description': self.description
        }

class HomeLamp(db.Model):
    __tablename__ = '首页灯具展示'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(100), nullable=False)
    image_path = db.Column(db.String(200), nullable=False)
    blank = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'image': f'/static/images/{self.image_path}',
            'blank': self.blank
        }

class GraphNode(db.Model):
    __tablename__ = '知识图谱节点'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    image_path = db.Column(db.String(200))
    symbol_size = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        result = {
            'id': self.id,
            'name': self.name
        }
        if self.image_path:
            result['symbol'] = f'image://http://localhost:5000/static/images/{self.image_path}'
        # 确保返回symbolSize，即使为空
        result['symbolSize'] = eval(self.symbol_size) if self.symbol_size else [120, 67.5]
        return result

class GraphEdge(db.Model):
    __tablename__ = '知识图谱边'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    source = db.Column(db.String(100), nullable=False)
    target = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'source': self.source,
            'target': self.target
        }

class MapLamp(db.Model):
    __tablename__ = '地图灯具'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    image_path = db.Column(db.String(200))
    description = db.Column(db.Text)
    dynasty = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        result = {
            'id': self.id,
            'name': self.name,
            'lnglat': [self.longitude, self.latitude],
            'description': self.description,
            'dynasty': self.dynasty
        }
        if self.image_path:
            result['image'] = f'http://localhost:5000/static/images/{self.image_path}'
        return result

class PaintingLamp(db.Model):
    __tablename__ = '画中灯'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    period = db.Column(db.String(50), nullable=False)
    image_path = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'period': self.period,
            'imageUrl': f'http://localhost:5000/static/images/{self.image_path}'
        }