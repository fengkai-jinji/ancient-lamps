import os
import datetime
import requests
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename
from backend.utils.config import DB_CONFIG, FLASK_CONFIG
from backend.models.models import db, AncientLamp, LampHistory, HomeLamp, GraphNode, GraphEdge, MapLamp, PaintingLamp

app = Flask(__name__)

# 配置数据库连接
app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+mysqlconnector://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}?charset={DB_CONFIG['charset']}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# 配置CORS支持前端跨域请求
CORS(app)

# 初始化数据库
db.init_app(app)

# 创建上传目录
UPLOAD_FOLDER = 'static/images'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# 地理编码函数，根据地址获取经纬度
def geocode(address):
    # 高德地图API key
    api_key = os.environ.get("AMAP_API_KEY")
    url = f"https://restapi.amap.com/v3/geocode/geo?key={api_key}&address={address}&output=json"
    try:
        response = requests.get(url)
        data = response.json()
        if data.get('status') == '1' and len(data.get('geocodes', [])) > 0:
            location = data['geocodes'][0]['location']
            longitude, latitude = location.split(',')
            return float(longitude), float(latitude)
        return None, None
    except Exception as e:
        print(f"地理编码错误: {e}")
        return None, None

# API路由
@app.route('/api/lamps', methods=['GET'])
def get_lamps():
    try:
        lamps = AncientLamp.query.all()
        return jsonify([lamp.to_dict() for lamp in lamps])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# 获取历史时间轴数据
@app.route('/api/history', methods=['GET'])
def get_history():
    try:
        history_items = LampHistory.query.order_by(LampHistory.id).all()
        return jsonify([item.to_dict() for item in history_items])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# 添加历史时间轴数据
@app.route('/api/history', methods=['POST'])
def add_history():
    try:
        # 处理表单数据
        dynasty = request.form.get('dynasty')
        year_range = request.form.get('year_range')
        name = request.form.get('name')
        description = request.form.get('description')
        
        # 处理文件上传
        file = request.files.get('file')
        if not file or not allowed_file(file.filename):
            return jsonify({'error': '无效的图片文件'}), 400
        
        # 保存图片
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # 创建新历史记录
        new_history = LampHistory(
            dynasty=dynasty,
            year_range=year_range,
            name=name,
            description=description,
            image_path=filename
        )
        
        db.session.add(new_history)
        db.session.commit()
        
        return jsonify(new_history.to_dict()), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# 获取单个历史节点数据
@app.route('/api/history/<int:history_id>', methods=['GET'])
def get_history_item(history_id):
    try:
        history = LampHistory.query.get_or_404(history_id)
        return jsonify(history.to_dict()), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# 更新历史时间轴数据
@app.route('/api/history/<int:history_id>', methods=['PUT'])
def update_history(history_id):
    try:
        history = LampHistory.query.get_or_404(history_id)
        
        # 更新基本信息
        history.dynasty = request.form.get('dynasty', history.dynasty)
        history.year_range = request.form.get('year_range', history.year_range)
        history.name = request.form.get('name', history.name)
        history.description = request.form.get('description', history.description)
        
        # 处理文件上传
        file = request.files.get('file')
        if file and allowed_file(file.filename):
            # 删除旧图片
            if history.image_path:
                old_filepath = os.path.join(app.config['UPLOAD_FOLDER'], history.image_path)
                if os.path.exists(old_filepath):
                    os.remove(old_filepath)
            
            # 保存新图片
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            history.image_path = filename
        
        db.session.commit()
        return jsonify(history.to_dict()), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# 删除历史时间轴数据
@app.route('/api/history/<int:history_id>', methods=['DELETE'])
def delete_history(history_id):
    try:
        history = LampHistory.query.get_or_404(history_id)
        
        # 删除图片文件
        if history.image_path:
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], history.image_path)
            if os.path.exists(filepath):
                os.remove(filepath)
        
        db.session.delete(history)
        db.session.commit()
        
        return jsonify({'message': '删除成功'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# 获取首页灯具数据
@app.route('/api/home', methods=['GET'])
def get_home_lamps():
    try:
        home_lamps = HomeLamp.query.order_by(HomeLamp.id).all()
        return jsonify([lamp.to_dict() for lamp in home_lamps])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# 添加首页灯具
@app.route('/api/home', methods=['POST'])
def add_home_lamp():
    try:
        title = request.form.get('title', '').strip()
        blank = request.form.get('blank', 'false').lower() == 'true'
        
        if not title:
            return jsonify({'error': '标题不能为空'}), 400
        
        # 处理文件上传
        file = request.files.get('file')
        if not file:
            return jsonify({'error': '请上传图片'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': '文件类型不允许'}), 400
        
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        new_lamp = HomeLamp(
            title=title,
            image_path=filename,
            blank=blank
        )
        
        db.session.add(new_lamp)
        db.session.commit()
        
        return jsonify(new_lamp.to_dict()), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# 获取单个首页灯具
@app.route('/api/home/<int:lamp_id>', methods=['GET'])
def get_home_lamp(lamp_id):
    try:
        lamp = HomeLamp.query.get_or_404(lamp_id)
        return jsonify(lamp.to_dict()), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# 更新首页灯具
@app.route('/api/home/<int:lamp_id>', methods=['PUT'])
def update_home_lamp(lamp_id):
    try:
        lamp = HomeLamp.query.get_or_404(lamp_id)
        
        # 更新基本信息
        lamp.title = request.form.get('title', lamp.title)
        lamp.blank = request.form.get('blank', str(lamp.blank)).lower() == 'true'
        
        # 处理文件上传
        file = request.files.get('file')
        if file and allowed_file(file.filename):
            # 删除旧图片
            if lamp.image_path:
                old_filepath = os.path.join(app.config['UPLOAD_FOLDER'], lamp.image_path)
                if os.path.exists(old_filepath):
                    os.remove(old_filepath)
            
            # 保存新图片
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            lamp.image_path = filename
        
        db.session.commit()
        return jsonify(lamp.to_dict()), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# 删除首页灯具
@app.route('/api/home/<int:lamp_id>', methods=['DELETE'])
def delete_home_lamp(lamp_id):
    try:
        lamp = HomeLamp.query.get_or_404(lamp_id)
        
        # 删除图片文件
        if lamp.image_path:
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], lamp.image_path)
            if os.path.exists(filepath):
                os.remove(filepath)
        
        db.session.delete(lamp)
        db.session.commit()
        
        return jsonify({'message': '删除成功'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/lamps', methods=['POST'])
def add_lamp():
    try:
        # 处理表单数据
        name = request.form.get('name')
        age = request.form.get('age')
        material = request.form.get('material')
        lamp_type = request.form.get('type', '座灯')
        detail = request.form.get('detail')
        properties = request.form.get('properties')
        history = request.form.get('history')
        
        # 处理文件上传
        file = request.files.get('file')
        if not file or not allowed_file(file.filename):
            return jsonify({'error': '无效的图片文件'}), 400
        
        # 生成灯具编号
        lamp_count = AncientLamp.query.count()
        lamp_id = f'lamp-{lamp_count + 1}'
        
        # 保存图片
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # 创建新灯具记录
        new_lamp = AncientLamp(
            灯具编号=lamp_id,
            灯具名称=name,
            所属朝代=age,
            灯具类型=lamp_type,
            材质=material,
            详情描述=detail,
            工艺特点=properties,
            历史背景=history,
            图片路径=filename
        )
        
        db.session.add(new_lamp)
        db.session.commit()
        
        return jsonify(new_lamp.to_dict()), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/lamps/<int:lamp_id>', methods=['DELETE'])
def delete_lamp(lamp_id):
    try:
        lamp = AncientLamp.query.get_or_404(lamp_id)
        
        # 删除图片文件
        if lamp.图片路径:
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], lamp.图片路径)
            if os.path.exists(filepath):
                os.remove(filepath)
        
        db.session.delete(lamp)
        db.session.commit()
        
        return jsonify({'message': '删除成功'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/lamps/<int:lamp_id>', methods=['PUT'])
def update_lamp(lamp_id):
    try:
        lamp = AncientLamp.query.get_or_404(lamp_id)
        
        # 处理表单数据
        name = request.form.get('name')
        age = request.form.get('age')
        material = request.form.get('material')
        lamp_type = request.form.get('type')
        detail = request.form.get('detail')
        properties = request.form.get('properties')
        history = request.form.get('history')
        
        # 更新灯具信息
        if name:
            lamp.灯具名称 = name
        if age:
            lamp.所属朝代 = age
        if material:
            lamp.材质 = material
        if lamp_type:
            lamp.灯具类型 = lamp_type
        if detail:
            lamp.详情描述 = detail
        if properties:
            lamp.工艺特点 = properties
        if history:
            lamp.历史背景 = history
        
        # 处理文件上传
        file = request.files.get('file')
        if file and allowed_file(file.filename):
            # 删除旧图片
            if lamp.图片路径:
                old_filepath = os.path.join(app.config['UPLOAD_FOLDER'], lamp.图片路径)
                if os.path.exists(old_filepath):
                    os.remove(old_filepath)
            
            # 保存新图片
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            lamp.图片路径 = filename
        
        db.session.commit()
        
        return jsonify(lamp.to_dict()), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/lamps/<int:lamp_id>', methods=['GET'])
def get_lamp(lamp_id):
    try:
        lamp = AncientLamp.query.get_or_404(lamp_id)
        return jsonify(lamp.to_dict()), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# 静态文件访问路由
@app.route('/static/images/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# 健康检查路由
@app.route('/')
def hello_world():
    return '古代精品灯具API服务运行中'

# 前端应用路由
@app.route('/app')
def front_end_app():
    from flask import send_from_directory
    return send_from_directory('templates', 'chose.vue')

# 管理页面路由
@app.route('/admin')
def admin_page():
    from flask import render_template
    return render_template('admin.html')

# 数据库连接测试
@app.route('/api/test-db')
def test_db():
    try:
        from sqlalchemy import text
        result = db.session.execute(text('SELECT 1')).fetchall()
        return jsonify({'status': '数据库连接正常', 'result': str(result)})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# 系统工具API路由

# 导出数据为CSV
@app.route('/api/tools/export')
def export_data():
    try:
        import csv
        import io
        from flask import send_file
        
        # 获取所有灯具数据
        lamps = AncientLamp.query.all()
        
        # 创建CSV文件
        output = io.StringIO()
        writer = csv.writer(output)
        
        # 写入表头
        writer.writerow(['ID', '灯具编号', '灯具名称', '所属朝代', '灯具类型', '材质', '详情描述', '工艺特点', '历史背景', '图片路径', '创建时间', '更新时间'])
        
        # 写入数据
        for lamp in lamps:
            writer.writerow([
                lamp.id,
                lamp.灯具编号,
                lamp.灯具名称,
                lamp.所属朝代,
                lamp.灯具类型,
                lamp.材质,
                lamp.详情描述,
                lamp.工艺特点,
                lamp.历史背景,
                lamp.图片路径,
                lamp.创建时间,
                lamp.更新时间
            ])
        
        # 重置文件指针
        output.seek(0)
        
        # 发送CSV文件
        return send_file(
            io.BytesIO(output.getvalue().encode('utf-8-sig')),
            mimetype='text/csv',
            as_attachment=True,
            download_name='lamps_data.csv'
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# 清理缓存
@app.route('/api/tools/clear-cache')
def clear_cache():
    try:
        import glob
        import os
        
        # 清理上传目录中的临时文件（如果有的话）
        upload_folder = app.config['UPLOAD_FOLDER']
        temp_files = glob.glob(os.path.join(upload_folder, 'temp_*'))
        for temp_file in temp_files:
            if os.path.exists(temp_file):
                os.remove(temp_file)
        
        return jsonify({'message': '缓存清理完成'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# 备份数据库
@app.route('/api/tools/backup')
def backup_database():
    try:
        import mysql.connector
        import os
        import datetime
        
        # 创建备份目录
        backup_dir = 'backups'
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)
        
        # 生成备份文件名
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_file = os.path.join(backup_dir, f'db_backup_{timestamp}.sql')
        
        # 使用mysql命令导出数据库
        import subprocess
        cmd = f"mysqldump -u {DB_CONFIG['user']} -p{DB_CONFIG['password']} -h {DB_CONFIG['host']} {DB_CONFIG['database']} > {backup_file}"
        subprocess.run(cmd, shell=True)
        
        # 检查备份文件是否生成
        if os.path.exists(backup_file) and os.path.getsize(backup_file) > 0:
            return jsonify({'message': '数据库备份成功', 'backup_file': backup_file}), 200
        else:
            return jsonify({'error': '数据库备份失败'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# 查看备份列表
@app.route('/api/tools/backups')
def list_backups():
    try:
        import os
        
        backup_dir = 'backups'
        backups = []
        
        if os.path.exists(backup_dir):
            for filename in os.listdir(backup_dir):
                if filename.endswith('.sql'):
                    filepath = os.path.join(backup_dir, filename)
                    stat = os.stat(filepath)
                    backups.append({
                        'filename': filename,
                        'filepath': filepath,
                        'size': round(stat.st_size / 1024, 2),  # KB
                        'created_time': datetime.datetime.fromtimestamp(stat.st_ctime).strftime('%Y-%m-%d %H:%M:%S')
                    })
        
        # 按创建时间倒序排列
        backups.sort(key=lambda x: x['created_time'], reverse=True)
        
        return jsonify({'backups': backups}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# 下载备份文件
@app.route('/api/tools/backups/<filename>')
def download_backup(filename):
    try:
        import os
        from flask import send_file
        
        backup_dir = 'backups'
        filepath = os.path.join(backup_dir, filename)
        
        if not os.path.exists(filepath):
            return jsonify({'error': '备份文件不存在'}), 404
        
        return send_file(filepath, as_attachment=True)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# 删除备份文件
@app.route('/api/tools/backups/<filename>', methods=['DELETE'])
def delete_backup(filename):
    try:
        import os
        
        backup_dir = 'backups'
        filepath = os.path.join(backup_dir, filename)
        
        if not os.path.exists(filepath):
            return jsonify({'error': '备份文件不存在'}), 404
        
        os.remove(filepath)
        return jsonify({'message': '备份文件删除成功'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# 数据库分析
@app.route('/api/tools/analytics')
def database_analytics():
    try:
        # 前端固定数据
        static_lamps = [
            {
                "id": "lamp-1",
                "name": "透雕人鸟兽玉饰件",
                "age": "新石器时代",
                "material": "玉",
                "type": "装饰灯"
            },
            {
                "id": "lamp-2",
                "name": "青铜剑",
                "age": "春秋",
                "material": "青铜",
                "type": "特殊灯"
            },
            {
                "id": "lamp-3",
                "name": "长信宫灯",
                "age": "西汉",
                "material": "青铜（鎏金）",
                "type": "人物形灯"
            },
            {
                "id": "lamp-4",
                "name": "错银铜牛灯",
                "age": "东汉",
                "material": "青铜（错银）",
                "type": "动物形灯"
            },
            {
                "id": "lamp-5",
                "name": "青釉熊水注灯",
                "age": "东吴-西晋",
                "material": "青瓷",
                "type": "座灯"
            },
            {
                "id": "lamp-6",
                "name": "十五连枝灯",
                "age": "战国",
                "material": "青铜",
                "type": "连枝灯"
            },
            {
                "id": "lamp-7",
                "name": "省油瓷灯",
                "age": "宋",
                "material": "瓷",
                "type": "座灯"
            },
            {
                "id": "lamp-8",
                "name": "雁鱼铜灯",
                "age": "西汉",
                "material": "青铜",
                "type": "动物形灯"
            }
        ]
        
        # 从数据库获取灯具数据
        db_lamps = AncientLamp.query.all()
        
        # 转换数据库数据格式
        db_lamps_list = []
        for lamp in db_lamps:
            db_lamps_list.append({
                "id": lamp.id,
                "name": lamp.灯具名称,
                "age": lamp.所属朝代,
                "material": lamp.材质,
                "type": lamp.灯具类型
            })
        
        # 合并所有灯具数据
        all_lamps = static_lamps + db_lamps_list
        
        # 统计数据
        age_stats = {}
        material_stats = {}
        type_stats = {}
        
        for lamp in all_lamps:
            # 统计年代
            if lamp['age'] in age_stats:
                age_stats[lamp['age']] += 1
            else:
                age_stats[lamp['age']] = 1
            
            # 统计材质
            if lamp['material'] in material_stats:
                material_stats[lamp['material']] += 1
            else:
                material_stats[lamp['material']] = 1
            
            # 统计类型
            if lamp['type'] in type_stats:
                type_stats[lamp['type']] += 1
            else:
                type_stats[lamp['type']] = 1
        
        # 转换为图表所需格式
        age_data = []
        for age, count in age_stats.items():
            age_data.append({"name": age, "value": count})
        
        material_data = []
        for material, count in material_stats.items():
            material_data.append({"name": material, "value": count})
        
        type_data = []
        for type_, count in type_stats.items():
            type_data.append({"name": type_, "value": count})
        
        # 年代排序（按历史顺序）
        age_order = ["新石器时代", "周", "春秋", "战国", "西汉", "东汉", "东吴-西晋", "隋唐", "宋", "明清"]
        age_data.sort(key=lambda x: age_order.index(x['name']) if x['name'] in age_order else 999)
        
        # 准备柱状图数据
        bar_x = [item['name'] for item in age_data]
        bar_y = [item['value'] for item in age_data]
        
        # 返回分析结果
        analytics_data = {
            "total_lamps": len(all_lamps),
            "static_lamps": len(static_lamps),
            "db_lamps": len(db_lamps_list),
            "age_distribution": age_data,
            "material_distribution": material_data,
            "type_distribution": type_data,
            "age_trend": {
                "x": bar_x,
                "y": bar_y
            }
        }
        
        return jsonify(analytics_data), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# 获取筛选选项
@app.route('/api/tools/filter-options')
def get_filter_options():
    try:
        # 从数据库获取灯具数据
        db_lamps = AncientLamp.query.all()
        
        # 使用数据库数据
        all_lamps = [
            {"age": lamp.所属朝代, "material": lamp.材质, "type": lamp.灯具类型}
            for lamp in db_lamps
        ]
        
        # 提取唯一值
        materials = set()
        types = set()
        
        for lamp in all_lamps:
            materials.add(lamp["material"])
            types.add(lamp["type"])
        
        # 朝代归类映射
        age_categories = {
            "新石器时代": "新石器时代",
            "周": "周",
            "春秋": "春秋",
            "战国": "战国",
            "西汉": "西汉",
            "东汉": "东汉",
            "西晋": "西晋",
            "东晋": "东晋",
            "北魏": "南北朝",
            "南朝": "南北朝",
            "北朝": "南北朝",
            "隋": "隋唐",
            "唐": "隋唐",
            "五代": "五代十国",
            "十国": "五代十国",
            "宋": "宋",
            "辽": "宋辽金",
            "金": "宋辽金",
            "元": "元",
            "明": "明",
            "清": "清"
        }
        
        # 生成标准朝代选项（按历史顺序）
        standard_ages = [
            "新石器时代", "周", "春秋", "战国", "西汉", "东汉", "西晋", "东晋", "南北朝", 
            "隋唐", "五代十国", "宋", "宋辽金", "元", "明", "清"
        ]
        
        # 生成材质和类型选项
        standard_materials = sorted(materials)
        standard_types = sorted(types)
        
        return jsonify({
            "ages": standard_ages,
            "materials": standard_materials,
            "types": standard_types,
            "age_categories": age_categories
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# 系统信息
@app.route('/api/tools/system-info')
def system_info():
    try:
        import platform
        import datetime
        import socket
        
        # 获取系统基本信息
        system_info = {
            'system': platform.system(),
            'release': platform.release(),
            'version': platform.version(),
            'machine': platform.machine(),
            'python_version': platform.python_version(),
            'hostname': socket.gethostname(),
            'ip_address': socket.gethostbyname(socket.gethostname()),
            'current_time': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'uptime': 'N/A'
        }
        
        # 尝试获取硬件信息
        try:
            import psutil
            system_info['uptime'] = str(datetime.timedelta(seconds=psutil.boot_time()))
            system_info['cpu'] = {
                'count': psutil.cpu_count(),
                'percent': psutil.cpu_percent(interval=1)
            }
            system_info['memory'] = {
                'total': round(psutil.virtual_memory().total / (1024**3), 2),
                'available': round(psutil.virtual_memory().available / (1024**3), 2),
                'used': round(psutil.virtual_memory().used / (1024**3), 2),
                'percent': psutil.virtual_memory().percent
            }
            system_info['disk'] = {
                'total': round(psutil.disk_usage('/').total / (1024**3), 2),
                'used': round(psutil.disk_usage('/').used / (1024**3), 2),
                'free': round(psutil.disk_usage('/').free / (1024**3), 2),
                'percent': psutil.disk_usage('/').percent
            }
        except ImportError:
            # 如果psutil不可用，返回基本信息
            system_info['cpu'] = {'count': 'N/A', 'percent': 'N/A'}
            system_info['memory'] = {'total': 'N/A', 'available': 'N/A', 'used': 'N/A', 'percent': 'N/A'}
            system_info['disk'] = {'total': 'N/A', 'used': 'N/A', 'free': 'N/A', 'percent': 'N/A'}
        
        return jsonify(system_info), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# 知识图谱API路由

# 获取知识图谱数据
@app.route('/api/graph', methods=['GET'])
def get_graph_data():
    try:
        nodes = GraphNode.query.all()
        edges = GraphEdge.query.all()
        return jsonify({
            'nodes': [node.to_dict() for node in nodes],
            'edges': [edge.to_dict() for edge in edges]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# 添加知识图谱节点
@app.route('/api/graph/nodes', methods=['POST'])
def add_graph_node():
    try:
        name = request.form.get('name')
        if not name:
            return jsonify({'error': '节点名称不能为空'}), 400
        
        # 处理图片上传
        image_path = None
        if 'file' in request.files:
            file = request.files['file']
            if file and file.filename:
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                image_path = filename
        
        symbol_size = request.form.get('symbol_size')
        
        node = GraphNode(
            name=name,
            image_path=image_path,
            symbol_size=symbol_size
        )
        db.session.add(node)
        db.session.commit()
        return jsonify(node.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# 添加知识图谱边
@app.route('/api/graph/edges', methods=['POST'])
def add_graph_edge():
    try:
        source = request.form.get('source')
        target = request.form.get('target')
        if not source or not target:
            return jsonify({'error': '源节点和目标节点不能为空'}), 400
        
        edge = GraphEdge(
            source=source,
            target=target
        )
        db.session.add(edge)
        db.session.commit()
        return jsonify(edge.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# 删除知识图谱节点
@app.route('/api/graph/nodes/<int:id>', methods=['DELETE'])
def delete_graph_node(id):
    try:
        node = GraphNode.query.get(id)
        if not node:
            return jsonify({'error': '节点不存在'}), 404
        
        # 删除对应的图片文件（如果存在）
        if node.image_path:
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], node.image_path)
            if os.path.exists(image_path):
                os.remove(image_path)
        
        # 删除相关的边
        edges = GraphEdge.query.filter(
            (GraphEdge.source == node.name) | (GraphEdge.target == node.name)
        ).all()
        for edge in edges:
            db.session.delete(edge)
        
        db.session.delete(node)
        db.session.commit()
        return jsonify({'message': '删除成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# 删除知识图谱边
@app.route('/api/graph/edges/<int:id>', methods=['DELETE'])
def delete_graph_edge(id):
    try:
        edge = GraphEdge.query.get(id)
        if not edge:
            return jsonify({'error': '边不存在'}), 404
        
        db.session.delete(edge)
        db.session.commit()
        return jsonify({'message': '删除成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# AI对话API路由
@app.route('/api/ai/chat', methods=['POST'])
def ai_chat():
    try:
        data = request.json
        message = data.get('message')
        
        if not message:
            return jsonify({'error': '消息内容不能为空'}), 400
        
        # 使用DeepSeek API
        api_key = os.environ.get("DEEPSEEK_API_KEY")
        url = 'https://api.deepseek.com/v1/chat/completions'
        
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {api_key}'
        }
        
        payload = {
            'model': 'deepseek-chat',
            'messages': [
                {
                    'role': 'system',
                    'content': '你是智慧古灯助手，专注于解答关于古灯的历史、文化、设计和3D打印等方面的问题。请用友好、专业的语言回答用户的问题。'
                },
                {
                    'role': 'user',
                    'content': message
                }
            ],
            'temperature': 0.7,
            'max_tokens': 1000
        }
        
        response = requests.post(url, headers=headers, json=payload)
        
        if not response.ok:
            raise Exception(f'API error: {response.status}')
        
        data = response.json()
        return jsonify({'response': data['choices'][0]['message']['content']})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# 地图灯具API路由

# 获取地图灯具数据
@app.route('/api/map', methods=['GET'])
def get_map_lamps():
    try:
        lamps = MapLamp.query.all()
        return jsonify([lamp.to_dict() for lamp in lamps])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# 添加地图灯具
@app.route('/api/map', methods=['POST'])
def add_map_lamp():
    try:
        name = request.form.get('name')
        longitude = request.form.get('longitude')
        latitude = request.form.get('latitude')
        address = request.form.get('address')
        description = request.form.get('description')
        dynasty = request.form.get('dynasty')
        
        if not name:
            return jsonify({'error': '名称不能为空'}), 400
        
        # 如果没有提供经纬度但提供了地址，使用地理编码获取经纬度
        if not longitude or not latitude:
            if address:
                longitude, latitude = geocode(address)
                if not longitude or not latitude:
                    return jsonify({'error': '无法根据地址获取经纬度，请手动输入经纬度'}), 400
            else:
                return jsonify({'error': '请提供经纬度或地址'}), 400
        
        # 处理图片上传
        image_path = None
        if 'file' in request.files:
            file = request.files['file']
            if file and file.filename:
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                image_path = filename
        
        lamp = MapLamp(
            name=name,
            longitude=float(longitude),
            latitude=float(latitude),
            image_path=image_path,
            description=description,
            dynasty=dynasty
        )
        db.session.add(lamp)
        db.session.commit()
        return jsonify(lamp.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# 更新地图灯具
@app.route('/api/map/<int:lamp_id>', methods=['PUT'])
def update_map_lamp(lamp_id):
    try:
        lamp = MapLamp.query.get(lamp_id)
        if not lamp:
            return jsonify({'error': '灯具不存在'}), 404
        
        # 处理表单数据
        name = request.form.get('name')
        longitude = request.form.get('longitude')
        latitude = request.form.get('latitude')
        description = request.form.get('description')
        dynasty = request.form.get('dynasty')
        
        if name:
            lamp.name = name
        if longitude:
            lamp.longitude = float(longitude)
        if latitude:
            lamp.latitude = float(latitude)
        if description:
            lamp.description = description
        if dynasty:
            lamp.dynasty = dynasty
        
        # 处理图片上传
        if 'file' in request.files:
            file = request.files['file']
            if file and file.filename:
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                lamp.image_path = filename
        
        db.session.commit()
        return jsonify(lamp.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# 删除地图灯具
@app.route('/api/map/<int:lamp_id>', methods=['DELETE'])
def delete_map_lamp(lamp_id):
    try:
        lamp = MapLamp.query.get(lamp_id)
        if not lamp:
            return jsonify({'error': '灯具不存在'}), 404
        
        db.session.delete(lamp)
        db.session.commit()
        return jsonify({'message': '删除成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# 画中灯API路由
# 获取所有画中灯
@app.route('/api/paintings', methods=['GET'])
def get_paintings():
    try:
        paintings = PaintingLamp.query.all()
        return jsonify([painting.to_dict() for painting in paintings])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# 添加画中灯
@app.route('/api/paintings', methods=['POST'])
def add_painting():
    try:
        name = request.form.get('name')
        description = request.form.get('description')
        period = request.form.get('period')
        
        if not name or not description or not period:
            return jsonify({'error': '名称、描述和时期不能为空'}), 400
        
        # 处理图片上传
        if 'file' not in request.files:
            return jsonify({'error': '请上传图片'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': '请上传图片'}), 400
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            
            painting = PaintingLamp(
                name=name,
                description=description,
                period=period,
                image_path=filename
            )
            db.session.add(painting)
            db.session.commit()
            return jsonify(painting.to_dict()), 201
        else:
            return jsonify({'error': '不支持的文件格式'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# 更新画中灯
@app.route('/api/paintings/<int:painting_id>', methods=['PUT'])
def update_painting(painting_id):
    try:
        painting = PaintingLamp.query.get(painting_id)
        if not painting:
            return jsonify({'error': '画中灯不存在'}), 404
        
        # 处理表单数据
        name = request.form.get('name')
        description = request.form.get('description')
        period = request.form.get('period')
        
        if name:
            painting.name = name
        if description:
            painting.description = description
        if period:
            painting.period = period
        
        # 处理图片上传
        if 'file' in request.files:
            file = request.files['file']
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                painting.image_path = filename
        
        db.session.commit()
        return jsonify(painting.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# 删除画中灯
@app.route('/api/paintings/<int:painting_id>', methods=['DELETE'])
def delete_painting(painting_id):
    try:
        painting = PaintingLamp.query.get(painting_id)
        if not painting:
            return jsonify({'error': '画中灯不存在'}), 404
        
        db.session.delete(painting)
        db.session.commit()
        return jsonify({'message': '删除成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        print("数据库表创建完成")
    
    app.run(
        host=FLASK_CONFIG['host'],
        port=FLASK_CONFIG['port'],
        debug=FLASK_CONFIG['debug']
    )