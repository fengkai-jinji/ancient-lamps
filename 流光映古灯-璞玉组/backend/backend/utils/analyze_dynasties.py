from app import app, db
from models import AncientLamp

with app.app_context():
    print('数据库中的朝代数据:')
    dynasties = set()
    for lamp in AncientLamp.query.all():
        dynasties.add(lamp.所属朝代)
    print(sorted(dynasties))
