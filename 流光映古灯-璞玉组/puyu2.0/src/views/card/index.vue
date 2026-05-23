<template>
	<div class="ancient-lamp-museum">
		<header class="museum-header">
			<div class="header-content">
				<h1 class="museum-title">
					文物展示
				</h1>
			</div>
		</header>
		
		<section class="filter-section">
			<div class="filter-container">
				<div class="filter-groups">
					<div class="filter-group">
						<label class="filter-label">年代筛选</label>
						<select v-model="selectedAge" class="filter-select" @change="handleFilter">
						<option value="">全部年代</option>
						<option v-for="age in ageOptions" :key="age" :value="age">
							{{ age }}
						</option>
					</select>
					</div>

					<div class="filter-group">
						<label class="filter-label">材质筛选</label>
						<select v-model="selectedMaterial" class="filter-select" @change="handleFilter">
							<option value="">全部材质</option>
							<option v-for="material in materialOptions" :key="material" :value="material">
								{{ material }}
							</option>
						</select>
					</div>

					<div class="filter-group">
						<label class="filter-label">灯具类型</label>
						<select v-model="selectedType" class="filter-select" @change="handleFilter">
							<option value="">全部类型</option>
							<option v-for="type in typeOptions" :key="type" :value="type">
								{{ type }}
							</option>
						</select>
					</div>
					
					<div class="search-group">
						<input v-model="searchText" type="text" placeholder="请输入搜索内容" class="search-input">
						<button @click="handleSearch" class="search-btn">搜索</button>
						<button @click="handleReset" class="reset-btn">清空</button>
					</div>
				</div>
			</div>
		</section>

		<section class="lamp-list-section">
			<div class="lamp-list-container">
				<div v-if="filteredLamps.length===0" class="no-result">
					<div class="no-result-icon">📜</div>
					<p class="no-result-text">未找到符合条件的灯具，可尝试调整筛选条件</p>
				</div>
				
				<div class="lamp-cards" v-else>
					<div class="lamp-card" v-for="lamp in filteredLamps" :key="lamp.id">
						<div class="lamp-image-container">
							<img :src="getImageUrl(lamp.image)" :alt="lamp.name" class="lamp-image" @error="handleImageError($event)">
							<div class="lamp-age-tag">{{lamp.age}}</div>
						</div>
						<div class="lamp-info">
							<h3 class="lamp-name">{{lamp.name}}</h3>
							<div class="lamp-meta">
								材质：{{ lamp.material }}
								类型：{{ lamp.type }}
							</div>
							<button class="detail-btn" @click="showDetail(lamp)">查看详情</button>
						</div>
					</div>
				</div>
			</div>
		</section>

		<teleport to="body">
			<div class="detail-modal" v-if="currentLamp">
				<div class="modal-overlay" @click="closeDetail"></div>
				<div class="modal-content">
					<button class="close-btn" @click="closeDetail">×</button>

					<div class="modal-header">
						<h2 class="modal-title">{{ currentLamp.name }}</h2>
					</div>

					<div class="modal-body">
						<div class="modal-image-container">
							<img :src="getImageUrl(currentLamp.image)" :alt="currentLamp.name" class="modal-image" @error="handleImageError($event)">
						</div>

						<div class="modal-detail">
							<h3 class="detail-title">文物详情</h3>
							<div class="detail-content">
								<p class="detail-paragraph">{{ currentLamp.detail }}</p>

								<div class="detail-properties" v-if="currentLamp.properties && currentLamp.properties.length > 0">
									<h4 class="properties-title">工艺特点</h4>
									<ul class="properties-list">
										<li class="property-item" v-for="(prop, i) in currentLamp.properties" :key="i">
											{{ prop }}
										</li>
									</ul>                                                                                                                                                                                                                                                                                                                                                                                       							</div>

								<div class="detail-history" v-if="currentLamp.history">
									<h4 class="history-title">历史背景</h4>
									<p class="history-content">{{ currentLamp.history }}</p>
								</div>
							</div>
						</div>
					</div>
				</div>
			</div>
		</teleport>
	</div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import axios from 'axios';



const lampData = ref([]);
const ageOptions = ref([]);
const materialOptions = ref([]);
const typeOptions = ref([]);
const ageCategories = ref({
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
});



const getImageUrl = (imagePath) => {
    if (!imagePath) return '';
    // 直接使用后端静态文件服务
    if (typeof imagePath === 'string') {
        if (imagePath.startsWith('/static/')) {
            return `http://localhost:5000${imagePath}`;
        } else {
            return `http://localhost:5000/static/images/${imagePath}`;
        }
    }
    return imagePath;
};

const fetchLamps = async () => {
    try {
        const res = await axios.get('http://localhost:5000/api/lamps');
        lampData.value = res.data;
        console.log("数据同步成功，当前总数:", lampData.value.length);
    } catch (error) {
        console.warn("未连接后端，仅显示基础馆藏", error);
    }
};

const fetchFilterOptions = async () => {
    try {
        const res = await axios.get('http://localhost:5000/api/tools/filter-options');
        ageOptions.value = res.data.ages;
        materialOptions.value = res.data.materials;
        typeOptions.value = res.data.types;
        ageCategories.value = res.data.age_categories;
        console.log("筛选选项同步成功");
    } catch (error) {
        console.warn("获取筛选选项失败，使用默认选项", error);
    }
};

onMounted(() => {
    fetchLamps();
    fetchFilterOptions();
});

const searchText = ref('');
const selectedAge = ref('');
const selectedMaterial = ref('');
const selectedType = ref('');
const currentLamp = ref(null);

const getAgeCategory = (age) => {
    // 尝试直接匹配
    for (const [key, category] of Object.entries(ageCategories.value)) {
        if (age.includes(key)) {
            return category;
        }
    }
    // 特殊处理
    if (age.includes('新石器')) return '新石器时代';
    if (age.includes('周')) return '周';
    if (age.includes('春秋')) return '春秋';
    if (age.includes('战国')) return '战国';
    if (age.includes('西汉')) return '西汉';
    if (age.includes('东汉')) return '东汉';
    if (age.includes('西晋')) return '西晋';
    if (age.includes('东晋')) return '东晋';
    if (age.includes('北魏') || age.includes('南北朝')) return '南北朝';
    if (age.includes('隋') || age.includes('唐')) return '隋唐';
    if (age.includes('五代') || age.includes('十国')) return '五代十国';
    if (age.includes('宋')) return '宋';
    if (age.includes('辽') || age.includes('金')) return '宋辽金';
    if (age.includes('元')) return '元';
    if (age.includes('明')) return '明';
    if (age.includes('清')) return '清';
    return age;
};

const filteredLamps = computed(() => {
		const searchLower = searchText.value.toLowerCase();
		return lampData.value.filter(lamp => {
			const matchSearch = !searchLower ||
				lamp.name.toLowerCase().includes(searchLower) ||
				(lamp.detail && lamp.detail.toLowerCase().includes(searchLower)) ||
				lamp.material.toLowerCase().includes(searchLower);
			const matchAge = !selectedAge.value || getAgeCategory(lamp.age) === selectedAge.value;
			const matchMaterial = !selectedMaterial.value || 
				lamp.material.includes(selectedMaterial.value) || 
				selectedMaterial.value.includes(lamp.material);
			const matchType = !selectedType.value || 
				lamp.type.includes(selectedType.value) || 
				selectedType.value.includes(lamp.type);

			return matchSearch && matchAge && matchMaterial && matchType;
		});
	});

const handleSearch = () => {};

const handleReset = () => {
    searchText.value = '';
    selectedAge.value = '';
    selectedMaterial.value = '';
    selectedType.value = '';
};

const handleFilter = () => {};

const showDetail = (lamp) => {
    currentLamp.value = lamp;
    document.body.style.overflow = 'hidden';
};

const closeDetail = () => {
    currentLamp.value = null;
    document.body.style.overflow = '';
};

const handleImageError = (e) => {
    e.target.src = 'http://localhost:5000/static/images/logo.jpg';
    console.warn('图片加载失败，已使用默认图片替代');
};
</script>

<style scoped>
* {
	margin: 0;
	padding: 0;
	box-sizing: border-box;
	font-family: "楷体";
}

.ancient-lamp-museum {
	min-height: 100vh;
	background-color: #f8f5f0;
	background-repeat: repeat;
	color: #5d4037;
}

.museum-header {
	width: 100%;
	height: auto;
	min-height: 8rem;
	display: flex;
	align-items: center;
	justify-content: center;
	text-align: center;
	background: linear-gradient(135deg, #f8f5f0 0%, #f0ede8 100%);
	border-bottom: 2px solid #8b6b46;
	position: relative;
	overflow: hidden;
}

.museum-header::before {
	content: '';
	position: absolute;
	top: 0;
	left: 0;
	right: 0;
	bottom: 0;
	z-index: 0;
}

.header-content {
	position: relative;
	z-index: 1;
}

.museum-title {
	font-size: 2.5rem;
	color: #5d4037;
	margin: 0;
	display: flex;
	align-items: center;
	justify-content: center;
	gap: 0.5rem;
	letter-spacing: 2px;
}

.title-char {
	display: inline-block;
	transition: transform 0.3s ease;
	text-shadow: 1px 1px 2px rgba(93, 64, 55, 0.2);
}

.museum-title:hover .title-char {
	transform: translateY(-3px);
}

.museum-title:hover .title-char:nth-child(odd) {
	transform: translateY(-3px) rotate(-2deg);
}

.museum-title:hover .title-char:nth-child(even) {
	transform: translateY(-3px) rotate(2deg);
}

.filter-section {
	padding: 1.5rem;
	background-color: rgba(255, 253, 245, 0.8);
	border-bottom: 1px solid #e0d8c8;
}

.filter-container {
	max-width: 1200px;
	margin: 0 auto;
}

.filter-groups {
	display: flex;
	flex-wrap: wrap;
	gap: 1.5rem;
	align-items: center;
}

.filter-group {
	display: flex;
	align-items: center;
	gap: 0.5rem;
}

.filter-label {
	font-size: 1rem;
	color: #6b4c2f;
	font-weight: 500;
}

.filter-select {
	padding: 0.4rem 0.8rem;
	border: 1px solid #8b6b46;
	border-radius: 6px;
	background-color: #fff;
	font-size: 1rem;
	color: #5d4037;
	cursor: pointer;
	transition: all 0.3s ease;
	appearance: none;
	background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='16' height='16' fill='none' viewBox='0 0 24 24' stroke='%235d4037'%3E%3Cpath stroke-linecap='round' stroke-linejoin='round' stroke-width='2' d='M19 9l-7 7-7-7'%3E%3C/path%3E%3C/svg%3E");
	background-repeat: no-repeat;
	background-position: right 0.5rem center;
	background-size: 1em;
	padding-right: 2rem;
}

.filter-select:focus {
	outline: none;
	border-color: #5d4037;
	box-shadow: 0 0 0 2px rgba(93, 64, 55, 0.2);
}

.filter-select:hover {
	border-color: #5d4037;
}

.filter-select option {
	background-color: #fff;
	color: #5d4037;
}

.search-group {
	display: flex;
	gap: 0.5rem;
}

.search-input {
	flex: 1;
	padding: 0.5rem 1rem;
	border: 1px solid #8b6b46;
	border-radius: 4px;
	background-color: #fff;
	font-size: 1rem;
	color: #5d4037;
}

.search-input:focus {
	outline: none;
	border-color: #5d4037;
	box-shadow: 0 0 0 2px rgba(93, 64, 55, 0.2);
}

.search-btn,
.reset-btn {
	padding: 0.5rem 1.2rem;
	border: none;
	border-radius: 6px;
	cursor: pointer;
	font-size: 1.15rem;
	transition: all 0.3s ease;
	position: relative;
	overflow: hidden;
}

.search-btn {
	background-color: #5d4037;
	color: #fff;
}

.search-btn:hover {
	background-color: #8b6b46;
	transform: translateY(-1px);
	box-shadow: 0 4px 12px rgba(93, 64, 55, 0.3);
}

.search-btn:active {
	transform: translateY(0);
}

.reset-btn {
	background-color: #e0d8c8;
	color: #5d4037;
}

.reset-btn:hover {
	background-color: #8b6b46;
	transform: translateY(-1px);
	box-shadow: 0 4px 12px rgba(139, 107, 70, 0.3);
}

.reset-btn:active {
	transform: translateY(0);
}

.lamp-list-section {
	padding: 2rem 1rem;
}

.lamp-list-container {
	max-width: 1200px;
	margin: 0 auto;
}

.no-result {
	text-align: center;
	padding: 4rem 2rem;
	color: #8b6b46;
}

.no-result-icon {
	font-size: 3rem;
	margin-bottom: 1rem;
}

.no-result-text {
	font-size: 1.2rem;
}

.lamp-cards {
	display: grid;
	grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
	gap: 2.5rem;
	padding: 1rem;
}

.lamp-card {
	background-color: #fff;
	border-radius: 12px;
	box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
	overflow: hidden;
	transition: transform 0.3s ease, box-shadow 0.3s ease;
	position: relative;
	border: 1px solid #f0ede8;
}

.lamp-card::before {
	content: '';
	position: absolute;
	top: 0;
	left: 0;
	right: 0;
	height: 4px;
	background: linear-gradient(90deg, #5d4037, #8b6b46, #5d4037);
	opacity: 0;
	transition: opacity 0.3s ease;
}

.lamp-card:hover {
	transform: translateY(-8px);
	box-shadow: 0 12px 24px rgba(93, 64, 55, 0.15);
}

.lamp-card:hover::before {
	opacity: 1;
}

.lamp-image-container {
	position: relative;
	height: 220px;
	margin-bottom: 1rem;
	border-radius: 0;
	overflow: hidden;
	background-color: #B5A381;
}

.lamp-image {
	width: 100%;
	height: 100%;
	object-fit: cover;
	transition: transform 0.5s ease;
}

.lamp-card:hover .lamp-image {
	transform: scale(1.05);
}

.lamp-age-tag {
	position: absolute;
	top: 0.5rem;
	left: 0.5rem;
	padding: 0.3rem 0.6rem;
	background-color: #5d4037;
	color: #fff;
	font-size: 0.95rem;
	border-radius: 4px;
}

.lamp-info {
	padding: 1rem;
}

.lamp-name {
	font-size: 1.4rem;
	color: #5d4037;
	margin-bottom: 0.5rem;
	border-bottom: 1px solid #e0d8c8;
	padding-bottom: 0.5rem;
	margin-left: 5px;
}

.lamp-meta {
	display: flex;
	flex-wrap: wrap;
	gap: 0.5rem;
	font-size: 1.05rem;
	color: #8b6b46;
	margin-bottom: 0.8rem;
	margin-left: 5px;
}

.detail-btn {
	display: inline-block;
	margin-left: 5px;
	padding: 0.4rem 1rem;
	background-color: #c8aa6e;
	color: #fff;
	border: none;
	border-radius: 6px;
	font-size: 0.9rem;
	cursor: pointer;
	transition: all 0.3s ease;
	position: relative;
	overflow: hidden;
}

.detail-btn::before {
	content: '';
	position: absolute;
	top: 50%;
	left: 50%;
	width: 0;
	height: 0;
	border-radius: 50%;
	background-color: rgba(255, 255, 255, 0.3);
	transform: translate(-50%, -50%);
	transition: width 0.6s ease, height 0.6s ease;
}

.detail-btn:hover {
	background-color: #8b5a2b;
	transform: translateY(-1px);
	box-shadow: 0 4px 12px rgba(200, 170, 110, 0.3);
}

.detail-btn:active::before {
	width: 300px;
	height: 300px;
}

.detail-modal {
	position: fixed;
	top: 0;
	left: 0;
	width: 100%;
	height: 100%;
	z-index: 1000;
	display: flex;
	align-items: center;
	justify-content: center;
	animation: modalFadeIn 0.3s ease-out;
}

@keyframes modalFadeIn {
	from {
		opacity: 0;
	}
	to {
		opacity: 1;
	}
}

.modal-overlay {
	position: absolute;
	top: 0;
	left: 0;
	width: 100%;
	height: 100%;
	background-color: rgba(0, 0, 0, 0.7);
	backdrop-filter: blur(2px);
}

.modal-content {
	position: relative;
	width: 95%;
	max-width: 1200px;
	max-height: 95vh;
	overflow-y: auto;
	background-color: #fff;
	border-radius: 12px;
	box-shadow: 0 12px 48px rgba(0, 0, 0, 0.3);
	padding: 2rem;
	background-color: #f8f5f0;
	animation: modalSlideIn 0.3s ease-out;
}

@keyframes modalSlideIn {
	from {
		opacity: 0;
		transform: scale(0.9) translateY(-20px);
	}
	to {
		opacity: 1;
		transform: scale(1) translateY(0);
	}
}

.close-btn {
	position: absolute;
	top: 1rem;
	right: 1rem;
	width: 35px;
	height: 35px;
	border-radius: 50%;
	background-color: #8b5a2b;
	color: #fff;
	border: none;
	font-size: 1.4rem;
	cursor: pointer;
	display: flex;
	align-items: center;
	justify-content: center;
	transition: all 0.3s ease;
	z-index: 10;
}

.close-btn:hover {
	background-color: #6b4c2f;
	transform: rotate(90deg);
}

.close-btn:active {
	transform: scale(0.9);
}

.modal-header {
	margin-bottom: 1.5rem;
	border-bottom: 2px solid #c8aa6e;
	padding-bottom: 1rem;
}

.modal-title {
	font-size: 2rem;
	color: #5d4037;
	margin: 0;
}

.modal-body {
	display: flex;
	flex-wrap: wrap;
	gap: 2rem;
	align-items: flex-start;
}

.modal-image-container {
	flex: 1;
	min-width: 400px;
	max-width: 500px;
	height: 500px;
	overflow: hidden;
	border-radius: 8px;
	background-color: #f8f5f0;
	display: flex;
	align-items: center;
	justify-content: center;
	padding: 20px;
}

.modal-image {
	width: 100%;
	height: 100%;
	object-fit: contain;
	transition: transform 0.5s ease;
}

.modal-image:hover {
	transform: scale(1.05);
}

.modal-detail {
	flex: 1.5;
	min-width: 300px;
}

.detail-title {
	font-size: 1.6rem;
	color: #8b5a2b;
	margin-bottom: 1rem;
	border-bottom: 1px solid #e0d8c8;
	padding-bottom: 0.5rem;
}

.detail-content {
	margin-top: 1rem;
}

.detail-paragraph {
	font-size: 1.2rem;
	line-height: 1.6;
	margin-bottom: 1.2rem;
	color: #33281e;
}

.properties-title,
.history-title {
	font-size: 1.3rem;
	color: #6b4c2f;
	margin-bottom: 0.5rem;
	font-weight: 500;
}

.properties-list {
	list-style-type: disc;
	padding-left: 1.5rem;
	color: #33281e;
	line-height: 1.5;
	font-size: 1.15rem;
}

.history-content {
	font-size: 1.2rem;
	line-height: 1.6;
	color: #33281e;
}

::-webkit-scrollbar {
	width: 8px;
}

::-webkit-scrollbar-track {
	background: #f5f0e6;
}

::-webkit-scrollbar-thumb {
	background: #c8aa6e;
	border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
	background: #8b5a2b;
}

@keyframes fadeInUp {
	from {
		opacity: 0;
		transform: translateY(20px);
	}
	to {
		opacity: 1;
		transform: translateY(0);
	}
}

.lamp-card {
	animation: fadeInUp 0.5s ease-out;
}

.lamp-card:nth-child(2) {
	animation-delay: 0.1s;
}

.lamp-card:nth-child(3) {
	animation-delay: 0.2s;
}

.lamp-card:nth-child(4) {
	animation-delay: 0.3s;
}

.lamp-card:nth-child(n+5) {
	animation-delay: 0.4s;
}

@media (max-width: 768px) {
	.museum-title {
		font-size: 2rem;
		flex-wrap: wrap;
		gap: 0.2rem;
	}

	.filter-groups {
		flex-direction: column;
		align-items: flex-start;
		gap: 1rem;
	}

	.filter-group {
		width: 100%;
	}

	.filter-select {
		width: 100%;
	}

	.modal-body {
		flex-direction: column;
	}

	.modal-image-container {
		height: 300px;
		max-width: 100%;
	}

	.lamp-cards {
		gap: 1.5rem;
		padding: 0.5rem;
	}
}

@media (max-width: 480px) {
	.museum-title {
		font-size: 1.6rem;
		flex-wrap: wrap;
	}

	.title-char {
		display: inline;
	}

	.search-group {
		flex-direction: column;
	}

	.search-group > button {
		width: 100%;
	}

	.lamp-cards {
		grid-template-columns: 1fr;
	}

	.modal-content {
		padding: 1.5rem 1rem;
		width: 95%;
		max-height: 95vh;
	}

	.modal-title {
		font-size: 1.5rem;
		margin-top: 1rem;
	}

	.close-btn {
		width: 30px;
		height: 30px;
		top: 0.5rem;
		right: 0.5rem;
	}
}
</style>